################################################################
# scripts/train_all.py  (qrd_eeg)
# Trainer hop nhat: moi method (teacher/no_kd/kd_base/feature_kd/
# rkd_classical/qrd_*/ck_*) + metric acc/kappa/F1 + fix braindecode _raw.
# Import tu 'src' cua repo Ensemble-MI (da them vao sys.path boi run_all.py).
################################################################
import os, time, math
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
from sklearn.metrics import cohen_kappa_score, f1_score

try:
    import pennylane as qml
    _HAS_PENNYLANE = True
except Exception:
    _HAS_PENNYLANE = False

from braindecode.util import set_random_seeds
from src.initializers import init_dataset, init_net, init_criterion, init_optimizer
from src.utils import get_input_dict, compute_weighted_preds


def patch_braindecode_legacy():
    try:
        from braindecode.datasets import base as bd_base
    except Exception as e:
        print("[compat] cannot import braindecode base:", e); return
    cls = getattr(bd_base, "EEGWindowsDataset", None)
    if cls is None or getattr(cls, "_qrd_patched", False):
        return
    raw_attr = cls.__dict__.get("raw", None)
    if not isinstance(raw_attr, property):
        cls._qrd_patched = True
        print("[compat] braindecode 'raw' is plain attribute; no patch needed."); return
    def _raw_getter(self):
        d = object.__getattribute__(self, "__dict__")
        r = d.get("_raw", None)
        return r if r is not None else d.get("raw", None)
    cls.raw = property(_raw_getter); cls._qrd_patched = True
    print("[compat] Patched EEGWindowsDataset.raw for legacy pickles.")


class KDLoss(nn.Module):
    def __init__(self, temperature=6.0):
        super().__init__(); self.temperature = temperature
    def forward(self, s_logits, t_logits):
        t = self.temperature
        return F.kl_div(F.log_softmax(s_logits/t, dim=1),
                        F.softmax(t_logits/t, dim=1),
                        reduction="batchmean") * (t*t)


def _prepare_feats(feats):
    if feats.ndim == 3: feats = feats.mean(1)
    elif feats.ndim > 2: feats = feats.view(feats.shape[0], -1)
    return feats


class FeatureKDLoss(nn.Module):
    def __init__(self, s_dim, t_dim):
        super().__init__()
        self.proj = nn.Identity() if s_dim == t_dim else nn.Linear(s_dim, t_dim)
    def forward(self, s_feats, t_feats):
        return F.mse_loss(self.proj(_prepare_feats(s_feats)), _prepare_feats(t_feats))


class ClassicalRKDLoss(nn.Module):
    def forward(self, s_feats, t_feats):
        s = _prepare_feats(s_feats); t = _prepare_feats(t_feats)
        def pdist_norm(x):
            d = torch.cdist(x, x, p=2)
            mask = ~torch.eye(d.shape[0], dtype=torch.bool, device=x.device)
            return d / d[mask].mean().clamp_min(1e-8)
        return F.smooth_l1_loss(pdist_norm(s), pdist_norm(t))


class RelationalDistillLoss(nn.Module):
    def __init__(self, kernel_type, s_dim, t_dim, n_qubits=4, n_q_layers=2, seed=1234,
                 reduce="proj", proj_input=False, theta_mode="shared",
                 teacher_proj_seed=None):
        super().__init__()
        # teacher_proj_seed (Van de lon 2, review IJRCS): mac dinh None -> giu
        # nguyen hanh vi cu (W_T lay tu luong RNG toan cuc dang chay, phu thuoc
        # gian tiep vao seed huan luyen qua thu tu goi ham). Neu dat mot so
        # nguyen, W_T duoc khoi tao lai TU MOT GENERATOR RIENG voi dung phan
        # bo mac dinh cua nn.Linear (Kaiming-uniform), doc lap voi seed huan
        # luyen -> dung de do do nhay cua ket qua voi rieng W_T.
        self.teacher_proj_seed = teacher_proj_seed
        self.kernel_type = kernel_type; self.n_qubits = n_qubits
        self.reduce = reduce
        # theta_mode (Van de lon 1, doi chung "teacher co dinh"): "shared" = mot
        # theta kha huan dung chung teacher/student (mac dinh cu); "shared_fixed" =
        # mot theta dung chung nhung giu co dinh (khong nhan gradient); "split" =
        # theta_T co dinh rieng, theta_S khoi tao giong het theta_T nhung kha huan.
        assert theta_mode in ("shared", "shared_fixed", "split")
        self.theta_mode = theta_mode
        # proj_input: cosine/rbf tinh tren khong gian da chieu (giong quantum) thay vi
        # dac trung 144 chieu tho. Muc dich: kiem soat cong bang so chieu + tham so hoc
        # duoc giua kernel luong tu va kernel co dien (xem phan biem "Van de 7").
        self.proj_input = proj_input
        self.dump_path = None  # set tu ngoai; luu K cua batch dau tien roi tat
        self._dumped = False
        needs_proj = (kernel_type == "quantum" and reduce == "proj") or \
                     (kernel_type in ("cosine", "rbf") and proj_input)
        if needs_proj:
            self.student_proj = nn.Linear(s_dim, n_qubits)
            self.teacher_proj = nn.Linear(t_dim, n_qubits)
            if teacher_proj_seed is not None:
                g = torch.Generator().manual_seed(int(teacher_proj_seed))
                nn.init.kaiming_uniform_(self.teacher_proj.weight, a=math.sqrt(5),
                                          generator=g)
                fan_in = self.teacher_proj.weight.shape[1]
                bound = 1.0 / math.sqrt(fan_in) if fan_in > 0 else 0.0
                nn.init.uniform_(self.teacher_proj.bias, -bound, bound, generator=g)
            # muc tieu quan he teacher PHAI CO DINH. Neu teacher_proj kha huan
            # thi L_QRD co nghiem tam thuong W->0 (moi mau cung mot goc,
            # K = ma tran toan 1, loss = 0) ma student khong hoc gi.
            for _p in self.teacher_proj.parameters():
                _p.requires_grad = False
        if kernel_type == "quantum":
            if not _HAS_PENNYLANE:
                raise RuntimeError("PennyLane missing but kernel_type='quantum'")
            self.dev = qml.device("default.qubit", wires=n_qubits)
            rng = np.random.default_rng(seed)
            w = rng.normal(0.0, 0.1, size=(n_q_layers, n_qubits, 3))
            if self.theta_mode == "split":
                # theta_T va theta_S khoi tao TU CUNG mot draw ngau nhien (giong
                # het nhau luc t=0) de khac biet ket qua chi den tu viec theta_S
                # duoc cap nhat rieng, khong den tu khac diem khoi tao.
                self.q_weights_teacher = nn.Parameter(torch.tensor(w, dtype=torch.float32))
                self.q_weights_student = nn.Parameter(torch.tensor(w.copy(), dtype=torch.float32))
                self.q_weights_teacher.requires_grad = False
            else:
                self.q_weights = nn.Parameter(torch.tensor(w, dtype=torch.float32))
                if self.theta_mode == "shared_fixed":
                    self.q_weights.requires_grad = False
            @qml.qnode(self.dev, interface="torch", diff_method="backprop")
            def circuit(x, q_weights):
                # data re-uploading: xen ke ma hoa va vuong viu, ket bang ma hoa
                # -> khong con unitary nao dung ngoai cung nen kernel khong suy bien
                for l in range(n_q_layers):
                    qml.AngleEmbedding(x, wires=range(n_qubits), rotation="Y")
                    qml.StronglyEntanglingLayers(q_weights[l:l+1], wires=range(n_qubits))
                qml.AngleEmbedding(x, wires=range(n_qubits), rotation="Y")
                return qml.state()
            self.circuit = circuit
    def _chunk_reduce(self, f):
        # giam chieu tat dinh: chia deu thanh n_qubits nhom, lay trung binh
        B, D = f.shape
        q = self.n_qubits
        if D % q != 0:
            f = F.pad(f, (0, q - (D % q)), mode="constant", value=0.0)
            D = f.shape[1]
        return f.view(B, q, D // q).mean(dim=2)
    def _angles(self, feats, which):
        f = _prepare_feats(feats)
        if self.reduce == "proj":
            f = self.student_proj(f) if which == "student" else self.teacher_proj(f)
        else:
            f = self._chunk_reduce(f)
        return torch.tanh(f) * np.pi
    def _states(self, angles, which):
        dev0 = angles.device
        a = angles.cpu()              # GIU grad (khong detach) -> student_proj hoc qua mach
        if self.theta_mode == "split":
            w = (self.q_weights_teacher if which == "teacher" else self.q_weights_student).cpu()
        else:
            w = self.q_weights.cpu()  # Parameter, co grad tru khi theta_mode="shared_fixed"
        s = torch.stack([self.circuit(a[i], w)
                         for i in range(a.shape[0])], dim=0)
        return s.to(dev0)             # dua states ve GPU cho kernel/loss
    def _quantum_kernel(self, feats, which):
        s = self._states(self._angles(feats, which), which)
        return (torch.abs(s @ torch.conj(s).T) ** 2).real
    def _classical_input(self, feats, which):
        f = _prepare_feats(feats)
        if self.proj_input:
            f = self.student_proj(f) if which == "student" else self.teacher_proj(f)
        return f
    def _cosine_kernel(self, feats, which):
        x = F.normalize(self._classical_input(feats, which), dim=1)
        return 0.5 * (1.0 + x @ x.T)
    def _rbf_kernel(self, feats, which):
        x = self._classical_input(feats, which); d2 = torch.cdist(x, x, p=2) ** 2
        with torch.no_grad(): med = d2[d2 > 0].median().clamp_min(1e-8)
        return torch.exp(-d2 / (2.0 * med))
    def _kernel(self, feats, which):
        if self.kernel_type == "quantum": return self._quantum_kernel(feats, which)
        if self.kernel_type == "cosine":  return self._cosine_kernel(feats, which)
        if self.kernel_type == "rbf":     return self._rbf_kernel(feats, which)
        raise ValueError(self.kernel_type)
    def forward(self, s_feats, t_feats, pair_mask=None):
        Ks = self._kernel(s_feats, "student"); Kt = self._kernel(t_feats, "teacher")
        with torch.no_grad():
            _n = Ks.shape[0]
            _off = ~torch.eye(_n, dtype=torch.bool, device=Ks.device)
            self.last_diag = dict(
                var_Ks=float(Ks[_off].var()), var_Kt=float(Kt[_off].var()),
                mean_Ks=float(Ks[_off].mean()),
                w_s=float(self.student_proj.weight.abs().mean())
                     if hasattr(self, "student_proj") else float("nan"))
        if self.dump_path is not None and not self._dumped:
            import numpy as _np
            _np.savez(self.dump_path, kernel_type=self.kernel_type,
                      K_student=Ks.detach().cpu().numpy(),
                      K_teacher=Kt.detach().cpu().numpy())
            self._dumped = True
        l = F.mse_loss(Ks, Kt) if pair_mask is None else F.mse_loss(Ks[pair_mask], Kt[pair_mask])
        # raw_loss: gia tri L_QRD THO, TRUOC khi nhan beta_qrd. Dung de doi
        # chieu do lon giua 3 dang ham nhan (Van de lon 3, review IJRCS) -
        # tinh cho ca 3 kernel_type vi khong phu thuoc cach tinh Ks/Kt.
        self.last_diag["raw_loss"] = float(l.detach())
        return l


def _normalized_entropy(logits):
    p = F.softmax(logits, dim=1)
    return -(p * torch.log(p + 1e-8)).sum(1) / np.log(logits.shape[1])

def _js_divergence(lp, lq):
    p = F.softmax(lp, dim=1); q = F.softmax(lq, dim=1); m = 0.5 * (p + q)
    kl = lambda a, b: (a * (torch.log(a + 1e-8) - torch.log(b + 1e-8))).sum(1)
    return 0.5 * (kl(p, m) + kl(q, m))

def select_informative_idx(t_logits, s_logits, q, ew=0.5, dw=0.5):
    with torch.no_grad():
        score = ew * _normalized_entropy(t_logits) + dw * _js_divergence(t_logits, s_logits)
        return torch.topk(score, k=min(q, t_logits.shape[0]), largest=True).indices

def select_random_idx(n, q, device="cpu"):
    # Doi chung candidate-pool (Van de lon 4, review IJRCS): giu NGUYEN
    # candidate pool = toan bo N mau cua batch giong V5, nhung thay tieu chi
    # entropy+disagreement bang chon ngau nhien -> tach rieng dong gop cua
    # "tieu chi chon" khoi dong gop cua "kich thuoc candidate pool".
    with torch.no_grad():
        return torch.randperm(n, device=device)[:min(q, n)]

def build_pair_mask(sel, q, t_feats=None, num_anchors=8, knn_k=4, device="cpu"):
    if sel in ("dense", "teacher_guided"): return None
    mask = torch.zeros(q, q, dtype=torch.bool, device=device)
    A = min(num_anchors, q); mask[:A, :A] = True
    if sel == "global_local" and t_feats is not None:
        t = _prepare_feats(t_feats)[:q]
        with torch.no_grad():
            d = torch.cdist(t, t, p=2); d.fill_diagonal_(float("inf"))
            knn = torch.topk(d, k=min(knn_k, q - 1), largest=False).indices
        for i in range(q):
            mask[i, knn[i]] = True; mask[knn[i], i] = True
    return mask


@torch.no_grad()
def evaluate_full(dataloader, student, criterion, device, return_feats=False):
    """Metric gop (acc/kappa/f1) + per-subject acc (nen cho variance C2).
    return_feats=True: them dac trung trung gian 144-chieu (nen cho phan tich
    t-SNE co the tai lap - xem Van de 12)."""
    student.eval(); tot_loss, tot_n = 0.0, 0; P, Y, S = [], [], []
    Feats = [] if return_feats else None
    for batch in dataloader:
        if batch["eeg"].shape[0] == 1: continue
        x = batch["eeg"].float().to(device); y = batch["target"].to(device)
        sout = student(x); logits = sout["scores"]
        if return_feats: Feats.append(sout["feats"].detach().cpu())
        tot_loss += criterion(logits, y).item() * y.shape[0]; tot_n += y.shape[0]
        P.append(logits.argmax(1).cpu()); Y.append(y.cpu())
        subj = batch["subject"]
        S.append(subj.cpu() if torch.is_tensor(subj) else torch.as_tensor([int(s) for s in subj]))
    yp = torch.cat(P).numpy(); yt = torch.cat(Y).numpy(); ys = torch.cat(S).numpy()
    per_subject = {}
    for sid in np.unique(ys):
        m = ys == sid
        per_subject[int(sid)] = {"acc": 100.0 * (yp[m] == yt[m]).mean(), "n": int(m.sum())}
    out = {"loss": tot_loss / max(tot_n, 1), "acc": 100.0 * (yp == yt).mean(),
            "kappa": cohen_kappa_score(yt, yp), "f1": f1_score(yt, yp, average="macro"),
            "per_subject": per_subject}
    if return_feats:
        out["feats"] = torch.cat(Feats).numpy(); out["labels"] = yt; out["subjects"] = ys
    return out


@torch.no_grad()
def evaluate_teacher(dataloader, teacher, device):
    teacher.eval(); P, Y = [], []
    for batch in dataloader:
        if batch["eeg"].shape[0] == 1: continue
        y = batch["target"].to(device)
        logits = compute_weighted_preds(teacher(get_input_dict(batch, device)))
        P.append(logits.argmax(1).cpu()); Y.append(y.cpu())
    yp = torch.cat(P).numpy(); yt = torch.cat(Y).numpy()
    return {"acc": 100.0 * (yp == yt).mean(),
            "kappa": cohen_kappa_score(yt, yp), "f1": f1_score(yt, yp, average="macro")}


METHOD_TABLE = {
    "no_kd":            dict(kd=False, feat=False, rkd=False, kernel=None,      sel=None),
    "kd_base":          dict(kd=True,  feat=False, rkd=False, kernel=None,      sel=None),
    "feature_kd":       dict(kd=True,  feat=True,  rkd=False, kernel=None,      sel=None),
    "rkd_classical":    dict(kd=True,  feat=False, rkd=True,  kernel=None,      sel=None),
    "qrd_dense":        dict(kd=True,  feat=False, rkd=False, kernel="quantum", sel="dense"),
    "qrd_dense_noproj": dict(kd=True,  feat=False, rkd=False, kernel="quantum", sel="dense", reduce="chunk"),
    "qrd_anchor":       dict(kd=True,  feat=False, rkd=False, kernel="quantum", sel="anchor"),
    "qrd_global_local": dict(kd=True,  feat=False, rkd=False, kernel="quantum", sel="global_local"),
    "qrd_teacher_guided": dict(kd=True, feat=False, rkd=False, kernel="quantum", sel="teacher_guided"),
    "ck_cosine_tg":     dict(kd=True,  feat=False, rkd=False, kernel="cosine",  sel="teacher_guided"),
    "ck_rbf_tg":        dict(kd=True,  feat=False, rkd=False, kernel="rbf",     sel="teacher_guided"),
    # Bien the "proj": cosine/RBF tinh tren KHONG GIAN 4 CHIEU da chieu qua W_S/W_T,
    # giong het nhanh luong tu, thay vi dac trung 144 chieu tho. Kiem soat cong bang
    # so chieu dau vao + so tham so hoc duoc (580 tu W_S, giong V5) giua 3 dang kernel.
    "ck_cosine_tg_proj": dict(kd=True, feat=False, rkd=False, kernel="cosine", sel="teacher_guided", proj_input=True),
    "ck_rbf_tg_proj":    dict(kd=True, feat=False, rkd=False, kernel="rbf",    sel="teacher_guided", proj_input=True),
    # Doi chung theta_mode (Van de lon 1 - review IJRCS): "qrd_dense" (V2, o tren)
    # la nhanh theta_mode="shared" mac dinh, dung lam moc so sanh. Hai bien the
    # duoi day GIU NGUYEN moi thu khac (sel="dense", reduce="proj") va CHI doi
    # cach xu ly theta cua mach luong tu.
    "qrd_dense_theta_fixed": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                                   sel="dense", theta_mode="shared_fixed"),
    "qrd_dense_theta_split": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                                   sel="dense", theta_mode="split"),
    # Do nhay voi W_T (Van de lon 2 - review IJRCS): 5 method giong het "qrd_dense"
    # (V2) ve moi mat, CHI khac o teacher_proj_seed - 5 lan khoi tao W_T DOC LAP
    # nhau, dung PHAN BO GIONG HET nn.Linear mac dinh. Chay o MOT seed huan luyen
    # co dinh (xem jobs/wt_sensitivity.pbs) de tach rieng phuong sai do W_T khoi
    # phuong sai do seed huan luyen (da bao cao 0,734pp trong bai, tu qrd_dense).
    "qrd_dense_wt1": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                           sel="dense", teacher_proj_seed=90001),
    "qrd_dense_wt2": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                           sel="dense", teacher_proj_seed=90002),
    "qrd_dense_wt3": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                           sel="dense", teacher_proj_seed=90003),
    "qrd_dense_wt4": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                           sel="dense", teacher_proj_seed=90004),
    "qrd_dense_wt5": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                           sel="dense", teacher_proj_seed=90005),
    # Doi chung candidate pool (Van de lon 4 - review IJRCS): giong het V5
    # (qrd_teacher_guided) ve moi mat - candidate pool = toan bo N=64 mau
    # cua batch - CHI khac o tieu chi chon: ngau nhien thay vi
    # entropy+disagreement. Dung de tach dong gop cua "tieu chi chon" khoi
    # dong gop cua "kich thuoc candidate pool" trong ket qua V5.
    "qrd_random_pool64": dict(kd=True, feat=False, rkd=False, kernel="quantum",
                               sel="random_pool64"),
}


def train_method(method, student_args, teacher_args, teacher_ckpt,
                 alpha=0.5, temperature=6.0, beta_qrd=0.02, gamma_feat=0.1, gamma_rkd=1.0,
                 n_qubits=4, n_q_layers=2, qrd_batch_size=16, num_anchors=8, knn_k=4,
                 entropy_weight=0.5, disagreement_weight=0.5, seed=20200220, verbose=True,
                 save_test_feats=False):
    cfg = METHOD_TABLE[method]
    use_cuda = bool(student_args.cuda) and torch.cuda.is_available()
    device = "cuda" if use_cuda else "cpu"
    set_random_seeds(seed=seed, cuda=use_cuda)
    student_args.cuda = teacher_args.cuda = use_cuda

    progress_folder = os.path.join(os.getcwd(), "results", student_args.dataset_name,
                                   "qrd_all", getattr(student_args, "exp_group", "run"))
    os.makedirs(progress_folder, exist_ok=True)
    student_args.progress_folder = progress_folder
    teacher_args.progress_folder = progress_folder

    dl_train, dl_val, dl_test, dinfo = init_dataset(args=teacher_args)
    student = init_net(student_args, dinfo).to(device)
    teacher = init_net(teacher_args, dinfo).to(device)
    teacher.load_state_dict(torch.load(teacher_ckpt, map_location=device), strict=True)
    teacher.eval()
    for p in teacher.parameters(): p.requires_grad = False

    s_dim = t_dim = 144
    ce = init_criterion()
    kd = KDLoss(temperature) if cfg["kd"] else None
    feat_loss = FeatureKDLoss(s_dim, t_dim).to(device) if cfg["feat"] else None
    rkd_loss = ClassicalRKDLoss().to(device) if cfg["rkd"] else None
    rel_loss = RelationalDistillLoss(cfg["kernel"], s_dim, t_dim, n_qubits, n_q_layers,
                                     reduce=cfg.get("reduce", "proj"),
                                     proj_input=cfg.get("proj_input", False),
                                     theta_mode=cfg.get("theta_mode", "shared"),
                                     teacher_proj_seed=cfg.get("teacher_proj_seed", None)
                                     ).to(device) if cfg["kernel"] else None
    if rel_loss is not None and os.environ.get("QRD_KERNEL_DUMP"):
        _dd = os.environ["QRD_KERNEL_DUMP"]; os.makedirs(_dd, exist_ok=True)
        rel_loss.dump_path = os.path.join(_dd, f"kernel_{cfg['kernel']}_{method}.npz")

    optimizer = init_optimizer(student_args, student)
    extra = []
    if feat_loss is not None: extra += [p for p in feat_loss.parameters() if p.requires_grad]
    if rel_loss is not None:  extra += [p for p in rel_loss.parameters() if p.requires_grad]
    if extra: optimizer.add_param_group({"params": extra, "weight_decay": 0.0})

    if verbose:
        np_ = sum(int(np.prod(p.size())) for p in student.parameters() if p.requires_grad)
        print(f"\n=== method={method} | student_params={np_} | kernel={cfg['kernel']} sel={cfg['sel']} ===")

    history, epoch_times = [], []
    best_val, best_test = -1.0, None
    grad_diag = bool(os.environ.get("QRD_GRAD_DIAG")) and rel_loss is not None
    for epoch in range(student_args.max_epochs):
        student.train(); t0 = time.time(); _grad_diag_done = False
        for batch in dl_train:
            if batch["eeg"].shape[0] == 1: continue
            x = batch["eeg"].float().to(device); y = batch["target"].to(device)
            with torch.no_grad():
                tout = teacher(get_input_dict(batch, device))
                t_logits = compute_weighted_preds(tout); t_feats = tout["feats"]
            sout = student(x); s_logits, s_feats = sout["scores"], sout["feats"]
            loss = alpha * ce(s_logits, y)
            if kd is not None:        loss = loss + (1.0 - alpha) * kd(s_logits, t_logits)
            if feat_loss is not None: loss = loss + gamma_feat * feat_loss(s_feats, t_feats)
            if rkd_loss is not None:  loss = loss + gamma_rkd * rkd_loss(s_feats, t_feats)
            if rel_loss is not None:
                q = min(qrd_batch_size, x.shape[0])
                if cfg["sel"] == "teacher_guided":
                    idx = select_informative_idx(t_logits, s_logits, q, entropy_weight, disagreement_weight)
                    sf, tf, mask = s_feats[idx], t_feats[idx], None
                elif cfg["sel"] == "random_pool64":
                    idx = select_random_idx(x.shape[0], q, device=device)
                    sf, tf, mask = s_feats[idx], t_feats[idx], None
                else:
                    sf, tf = s_feats[:q], t_feats[:q]
                    mask = build_pair_mask(cfg["sel"], q, t_feats=t_feats, num_anchors=num_anchors, knn_k=knn_k, device=device)
                rel_term = rel_loss(sf, tf, pair_mask=mask)
                if grad_diag and not _grad_diag_done:
                    # Do gradient norm RIENG cua beta*L_QRD len tham so student
                    # (Van de lon 3, review IJRCS): backward tach biet, retain_graph
                    # de khong pha do thi dung cho backward chinh ngay sau do; zero_grad
                    # truoc/sau de khong tron voi gradient cua CE/KD/feat/rkd.
                    student.zero_grad()
                    (beta_qrd * rel_term).backward(retain_graph=True)
                    _gn = math.sqrt(sum(float(p.grad.norm()) ** 2
                                         for p in student.parameters() if p.grad is not None))
                    rel_loss._grad_norm_student_diag = _gn
                    student.zero_grad()
                    _grad_diag_done = True
                loss = loss + beta_qrd * rel_term
            optimizer.zero_grad(); loss.backward(); optimizer.step()
        epoch_times.append(time.time() - t0)
        val = evaluate_full(dl_val, student, ce, device)
        test = evaluate_full(dl_test, student, ce, device, return_feats=save_test_feats)
        history.append(dict(epoch=epoch+1, val_acc=val["acc"], test_acc=test["acc"],
                            test_kappa=test["kappa"], test_f1=test["f1"], dur=epoch_times[-1]))
        if verbose:
            _d = getattr(rel_loss, "last_diag", None) if rel_loss is not None else None
            _gns = getattr(rel_loss, "_grad_norm_student_diag", None) if rel_loss is not None else None
            _qs = (f" | QRD varKs={_d['var_Ks']:.2e} varKt={_d['var_Kt']:.2e} "
                   f"meanKs={_d['mean_Ks']:.3f} |Ws|={_d['w_s']:.4f} "
                   f"rawL={_d.get('raw_loss', float('nan')):.3e}"
                   + (f" gradNormS={_gns:.3e}" if _gns is not None else "")
                   ) if _d else ""
            print(f"  ep{epoch+1:03d} val_acc={val['acc']:.2f} test_acc={test['acc']:.2f} "
                  f"kappa={test['kappa']:.3f} f1={test['f1']:.3f} ({epoch_times[-1]:.1f}s)" + _qs)
        if val["acc"] > best_val:
            best_val = val["acc"]; best_test = test
    out = dict(method=method, acc=best_test["acc"], kappa=best_test["kappa"], f1=best_test["f1"],
                per_subject=best_test["per_subject"],
                mean_epoch_time=float(np.mean(epoch_times)), history=pd.DataFrame(history))
    if save_test_feats:
        out["test_feats"] = best_test["feats"]; out["test_labels"] = best_test["labels"]
        out["test_subjects"] = best_test["subjects"]
    return out
