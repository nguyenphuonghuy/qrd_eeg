################################################################
# scripts/run_ensemble.py  (qrd_eeg)
# Baseline giam-variance: no-KD EEGNet x 5 seed, ensemble logits.
# KHONG dung train_method (bao ve loi). Train no-KD toi gian (chi CE).
# Xuat 2 dai luong cho C2, cung dinh dang per-subject CSV:
#   - nokd_single_seed{K} : per-subject acc moi seed (5 gia tri -> variance 1 model)
#   - deep_ensemble_nokd  : per-subject acc tu logits TRUNG BINH 5 seed (variance ensemble)
################################################################
import os, sys, copy, datetime
import numpy as np
import pandas as pd
import torch

_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from src.config import *
from src.args_utils import create_exp_args
from src.initializers import init_dataset, init_net, init_criterion, init_optimizer
# them thu muc scripts/ (chua train_all.py cua ta) vao path
_SELF = os.path.dirname(os.path.abspath(__file__))
if _SELF not in sys.path:
    sys.path.insert(0, _SELF)
from train_all import patch_braindecode_legacy
from braindecode.util import set_random_seeds

N_FOLDS = int(os.environ.get("QRD_N_FOLDS", "5"))
SEEDS = list(range(int(os.environ.get("QRD_N_SEEDS", "5"))))
MAX_EPOCHS = int(os.environ.get("QRD_MAX_EPOCHS", "30"))
OUT = os.environ.get("QRD_OUT_DIR", os.path.join(os.path.dirname(__file__), "..", "results"))


def build_args_dict(max_epochs):
    return {
        "use_folds": True, "n_folds": N_FOLDS, "resume": False, "resume_exp_id": "",
        "n_subsets": 7, "ensemble_loss_1": True, "ensemble_loss_2": True,
        "loss_2_single_expert": False, "n_modules_stage_1": 4,
        "stage_1_is_shared": False, "stage_2_is_shared": True, "feats_aggr": "mean",
        "pre_align": True, "dataset_name": "PhysionetMI",
        "batch_size": 64, "batch_size_val": 64,
        "backbone_k_width": 1, "dropout_input": 0.4, "dropout_1": 0.1,
        "load_ckpt": False, "ckpt_file": "", "checkpoint": "best",
        "use_scheduler": False, "warmup": False,
        "cuda": torch.cuda.is_available(),
        "exp_group": datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S"),
        "max_epochs": max_epochs, "warmup_epochs": 0, "optim": "sgd", "lr": 0.005,
        "momentum": 0.9, "weight_decay": 0.01, "coef_cls": 1.0,
        "net_cls": "eegnet", "use_subsets": False,
    }


@torch.no_grad()
def collect_logits(loader, net, device):
    net.eval(); L, Y, S = [], [], []
    for batch in loader:
        if batch["eeg"].shape[0] == 1: continue
        x = batch["eeg"].float().to(device)
        L.append(net(x)["scores"].cpu())
        Y.append(batch["target"].cpu())
        subj = batch["subject"]
        S.append(subj.cpu() if torch.is_tensor(subj) else torch.as_tensor([int(s) for s in subj]))
    return torch.cat(L).numpy(), torch.cat(Y).numpy(), torch.cat(S).numpy()


def per_subject_rows(method, fold, logits, y, s):
    pred = logits.argmax(1)
    out = []
    for sid in np.unique(s):
        m = s == sid
        out.append(dict(method=method, fold=fold, subject=int(sid),
                        acc=100.0 * (pred[m] == y[m]).mean(), n=int(m.sum())))
    return out


def main():
    patch_braindecode_legacy()
    os.makedirs(OUT, exist_ok=True)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    args_dict = build_args_dict(MAX_EPOCHS)
    rows = []

    for fold in range(N_FOLDS):
        args = create_exp_args(exp_args_dict=args_dict, fold_idx=fold)
        prog = os.path.join(os.getcwd(), "results", "PhysionetMI", "ensemble", args.exp_group)
        os.makedirs(prog, exist_ok=True); args.progress_folder = prog
        dl_train, dl_val, dl_test, dinfo = init_dataset(args=args)

        logits_sum = None; y_ref = s_ref = None
        for seed in SEEDS:
            set_random_seeds(seed=seed, cuda=(device == "cuda"))
            net = init_net(args, dinfo).to(device)
            ce = init_criterion()
            opt = init_optimizer(args, net)
            for epoch in range(MAX_EPOCHS):
                net.train()
                for batch in dl_train:
                    if batch["eeg"].shape[0] == 1: continue
                    x = batch["eeg"].float().to(device); yb = batch["target"].to(device)
                    loss = ce(net(x)["scores"], yb)
                    opt.zero_grad(); loss.backward(); opt.step()
            logits, y, s = collect_logits(dl_test, net, device)
            rows += per_subject_rows(f"nokd_single_seed{seed}", fold, logits, y, s)
            logits_sum = logits if logits_sum is None else logits_sum + logits
            y_ref, s_ref = y, s
            print(f"[fold {fold}] seed {seed}: acc={100.0*(logits.argmax(1)==y).mean():.2f}")

        ens = logits_sum / len(SEEDS)
        rows += per_subject_rows("deep_ensemble_nokd", fold, ens, y_ref, s_ref)
        print(f"[fold {fold}] ENSEMBLE: acc={100.0*(ens.argmax(1)==y_ref).mean():.2f}")

    df = pd.DataFrame(rows)
    out = os.path.join(OUT, "ensemble_per_subject.csv")
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}")
    for meth in ["deep_ensemble_nokd"]:
        d = df[df.method == meth]
        print(f"{meth}: per-subject mean={d['acc'].mean():.2f} +/- {d['acc'].std(ddof=1):.2f} (n={d['subject'].nunique()})")


if __name__ == "__main__":
    main()
