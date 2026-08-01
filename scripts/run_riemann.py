################################################################
# scripts/run_riemann.py  (qrd_eeg)
# Baseline EEG co dien: Covariances -> TangentSpace -> LDA (pyriemann).
# KHONG teacher/student/KD. Dung init_dataset (use_folds) de lay raw trials,
# chay 5-fold, gop -> per-subject acc cho du 103 subject.
# Xuat: results/riemann_per_subject.csv  (method=riemann_ts_lda), cung dinh dang
# voi results_all_per_subject.csv de tron vao phan tich C2.
################################################################
import os, sys, copy, datetime
import numpy as np
import pandas as pd

_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)

from src.config import *
from src.args_utils import create_exp_args
from src.initializers import init_dataset
# them thu muc scripts/ (chua train_all.py cua ta) vao path
_SELF = os.path.dirname(os.path.abspath(__file__))
if _SELF not in sys.path:
    sys.path.insert(0, _SELF)
from train_all import patch_braindecode_legacy

from pyriemann.estimation import Covariances
from pyriemann.tangentspace import TangentSpace
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.pipeline import make_pipeline

N_FOLDS = int(os.environ.get("QRD_N_FOLDS", "5"))
OUT = os.environ.get("QRD_OUT_DIR",
                     os.path.join(os.path.dirname(__file__), "..", "results"))


def loader_to_arrays(loader):
    """Rut toan bo (X, y, subject) tu mot dataloader."""
    X, Y, S = [], [], []
    for batch in loader:
        x = batch["eeg"]
        X.append(x.numpy() if hasattr(x, "numpy") else np.asarray(x))
        Y.append(np.asarray(batch["target"]))
        subj = batch["subject"]
        S.append(subj.numpy() if hasattr(subj, "numpy") else
                 np.asarray([int(s) for s in subj]))
    X = np.concatenate(X, 0).astype(np.float64)  # (N, ch, time)
    return X, np.concatenate(Y, 0), np.concatenate(S, 0)


def build_args_dict():
    common = {
        "use_folds": True, "n_folds": N_FOLDS, "resume": False, "resume_exp_id": "",
        "n_subsets": 7, "ensemble_loss_1": True, "ensemble_loss_2": True,
        "loss_2_single_expert": False, "n_modules_stage_1": 4,
        "stage_1_is_shared": False, "stage_2_is_shared": True, "feats_aggr": "mean",
        "pre_align": True, "dataset_name": "PhysionetMI",
        "batch_size": 64, "batch_size_val": 64,
        "backbone_k_width": 1, "dropout_input": 0.4, "dropout_1": 0.1,
        "load_ckpt": False, "ckpt_file": "", "checkpoint": "best",
        "use_scheduler": False, "warmup": False, "cuda": False,
        "exp_group": datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S"),
        "max_epochs": 1, "warmup_epochs": 0, "optim": "sgd", "lr": 0.005,
        "momentum": 0.9, "weight_decay": 0.01, "coef_cls": 1.0,
        "net_cls": "ensemble", "use_subsets": True,
    }
    return common


def main():
    patch_braindecode_legacy()
    os.makedirs(OUT, exist_ok=True)
    args_dict = build_args_dict()
    rows = []

    for fold in range(N_FOLDS):
        args = create_exp_args(exp_args_dict=args_dict, fold_idx=fold)
        prog = os.path.join(os.getcwd(), "results", "PhysionetMI", "riemann", args.exp_group)
        os.makedirs(prog, exist_ok=True); args.progress_folder = prog
        dl_train, dl_val, dl_test, _ = init_dataset(args=args)

        Xtr, ytr, _ = loader_to_arrays(dl_train)
        Xte, yte, Ste = loader_to_arrays(dl_test)

        clf = make_pipeline(Covariances(estimator="oas"), TangentSpace(), LinearDiscriminantAnalysis())
        clf.fit(Xtr, ytr)
        pred = clf.predict(Xte)

        for sid in np.unique(Ste):
            m = Ste == sid
            rows.append(dict(method="riemann_ts_lda", fold=fold, subject=int(sid),
                             acc=100.0 * (pred[m] == yte[m]).mean(), n=int(m.sum())))
        print(f"[fold {fold}] riemann: test_acc={100.0*(pred==yte).mean():.2f} "
              f"({len(np.unique(Ste))} subjects)")

    df = pd.DataFrame(rows)
    out = os.path.join(OUT, "riemann_per_subject.csv")
    df.to_csv(out, index=False)
    print(f"\nSaved: {out}")
    print(f"Overall per-subject mean acc = {df['acc'].mean():.2f} +/- {df['acc'].std(ddof=1):.2f} "
          f"(n={df['subject'].nunique()} subjects)")


if __name__ == "__main__":
    main()
