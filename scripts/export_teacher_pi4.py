################################################################
# scripts/export_teacher_pi4.py  (qrd_eeg)
# Xuat kien truc teacher (EnsembleEEG, Ensemble-MI) thanh TorchScript
# doc lap, dung de do do tre suy luan that tren Raspberry Pi 4 (khong
# can braindecode/mne o phia Pi4, chi can torch).
# Trong so NGAU NHIEN (co seed de tai lap): do tre suy luan chi phu
# thuoc kien truc/kich thuoc tensor, khong phu thuoc GIA TRI trong so
# (dung logic da ap dung cho student, xem export_student_pi4.py).
#
# LUU Y VE INPUT DANG DICT: EnsembleEEG.forward(x_dict) doi hoi x_dict la
# dict co khoa 'x'. Da doc code models/ensemble.py: voi cau hinh that
# cua bai (stage_1_is_shared=False -> Backbone_Multi, stage_2_is_shared=
# True -> Classifier_Shared), cac khoa 'subset'/'dataset_idx' CHI duoc
# dung de tinh loss luc huan luyen, KHONG duoc doc trong forward() cua
# ca Backbone_Multi lan Classifier_Shared khi eval. Vi vay input toi
# thieu hop le cho suy luan la {'x': tensor}, khop dung nhanh code thuc
# te se chay khi trace.
################################################################
import os, sys, torch

sys.dont_write_bytecode = True
_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path: sys.path.insert(0, _REPO)

from models import EnsembleEEG

torch.manual_seed(20200220)

N_ELECTRODES = 64
WINDOW_SIZE = 300
N_CLASSES = 2

# Cau hinh khop dung Bang tab:cauhinh / build_args_dicts trong
# scripts/run_seeds.py: n_subsets=7, backbone_k_width=1,
# n_modules_stage_1=4, stage_1_is_shared=False, stage_2_is_shared=True,
# dropout_input=0.4, dropout_1=0.1. n_datasets_train KHONG duoc doc
# trong forward() (chi luu lai, khong dung de dung encoder) nen gia tri
# cu the khong anh huong do tre/RAM do duoc.
net = EnsembleEEG(
    n_datasets_train=62,
    in_chans=N_ELECTRODES,
    input_window_samples=WINDOW_SIZE,
    dropout_input_prob=0.4,
    dropout_1_prob=0.1,
    n_subsets=7,
    k_width=1,
    n_classes=N_CLASSES,
    n_modules_backbone=4,
    stage_1_is_shared=False,
    stage_2_is_shared=True,
)
net.eval()

example = {"x": torch.randn(1, N_ELECTRODES, WINDOW_SIZE)}
with torch.no_grad():
    out = net(example)
print("output keys:", list(out.keys()), "scores shape:", tuple(out["scores"].shape))

traced = torch.jit.trace(net, (example,), strict=False)
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "pi4_latency")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "teacher_ensembleeeg_traced.pt")
traced.save(out_path)
print("Saved:", out_path, "size(KB)=", os.path.getsize(out_path) / 1024)

n_params = sum(p.numel() for p in net.parameters())
print("n_params:", n_params)

# sanity: reload va so sanh output voi ban goc
reloaded = torch.jit.load(out_path)
with torch.no_grad():
    out2 = reloaded(example)
diff = (out["scores"] - out2["scores"]).abs().max().item()
print("max abs diff (goc vs traced-reload):", diff)
assert diff < 1e-5, "Traced model KHONG khop model goc"
print("OK: traced model khop model goc.")
