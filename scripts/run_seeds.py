################################################################
# scripts/run_seeds.py  (qrd_eeg)
# Seed-variance: chay LAI vai method chu chot voi NHIEU seed de do
# do on dinh cua low-tail robustness (min-subject, sigma_sub) qua seed.
# KHONG sua train_method/run_all. Tai dung train_method (bao ve loi).
# Xuat: results/seeds_per_subject.csv  (method = "{tag}_s{seed}")
# Env override cho smoke: QRD_SEEDS, QRD_N_FOLDS, QRD_MAX_EPOCHS
################################################################
import os, sys, copy, time, datetime
import numpy as np
import pandas as pd
import torch

sys.dont_write_bytecode = True
_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path: sys.path.insert(0, _REPO)
_SELF = os.path.dirname(os.path.abspath(__file__))
if _SELF not in sys.path: sys.path.insert(0, _SELF)

from src.config import *
from src.args_utils import create_exp_args
from train_all import patch_braindecode_legacy, train_method, METHOD_TABLE

TEACHER_DIR = os.environ.get("QRD_TEACHER_DIR", os.path.join(_SELF, "..", "checkpoints"))
OUT_DIR     = os.environ.get("QRD_OUT_DIR",     os.path.join(_SELF, "..", "results"))
N_FOLDS     = int(os.environ.get("QRD_N_FOLDS",   "5"))
MAX_EPOCHS  = int(os.environ.get("QRD_MAX_EPOCHS","30"))
SEEDS       = [int(s) for s in os.environ.get("QRD_SEEDS", "1,2,3,4,5").split(",")]

HP = dict(alpha=float(os.environ.get("QRD_ALPHA", "0.5")), temperature=4.0, beta_qrd=0.02,
          gamma_feat=1.0, gamma_rkd=1.0,
          n_qubits=int(os.environ.get("QRD_N_QUBITS", "4")), n_q_layers=2,
          qrd_batch_size=16, num_anchors=8, knn_k=4,
          entropy_weight=0.5, disagreement_weight=0.5)

# (tag hien thi, ten method trong METHOD_TABLE, beta_qrd override)
RUNS = [
    ("kd_base",            "kd_base",            None),
    ("qrd_teacher_guided", "qrd_teacher_guided", 0.02),
    ("qrd_tg_b0.05",       "qrd_teacher_guided", 0.05),
]

# Env override: QRD_RUNS="tag:method:beta,tag:method,..."  (beta rong -> None)
_RUNS_ENV = os.environ.get("QRD_RUNS", "").strip()
if _RUNS_ENV:
    _parsed = []
    for _it in _RUNS_ENV.split(","):
        _it = _it.strip()
        if not _it: continue
        _p = _it.split(":")
        if len(_p) == 2:   _tag, _m, _b = _p[0], _p[1], None
        elif len(_p) == 3: _tag, _m, _b = _p[0], _p[1], (float(_p[2]) if _p[2].strip() else None)
        else: sys.exit("ERROR: QRD_RUNS sai dinh dang: '%s'" % _it)
        if _m.strip() not in METHOD_TABLE:
            sys.exit("ERROR: method '%s' khong co trong METHOD_TABLE: %s" % (_m, list(METHOD_TABLE)))
        _parsed.append((_tag.strip(), _m.strip(), _b))
    RUNS = _parsed

def build_args_dicts(max_epochs):
    common = {
        "use_folds": True, "n_folds": N_FOLDS, "resume": False, "resume_exp_id": "",
        "n_subsets": 7, "ensemble_loss_1": True, "ensemble_loss_2": True,
        "loss_2_single_expert": False, "n_modules_stage_1": 4,
        "stage_1_is_shared": False, "stage_2_is_shared": True, "feats_aggr": "mean",
        "pre_align": True, "dataset_name": os.environ.get("QRD_DATASET", "PhysionetMI"),
        "batch_size": 64, "batch_size_val": 64,
        "backbone_k_width": 1, "dropout_input": 0.4, "dropout_1": 0.1,
        "load_ckpt": False, "ckpt_file": "", "checkpoint": "best",
        "use_scheduler": False, "warmup": False, "cuda": torch.cuda.is_available(),
        "exp_group": datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S"),
        "max_epochs": max_epochs, "warmup_epochs": 0,
        "optim": "sgd", "lr": 0.005, "momentum": 0.9, "weight_decay": 0.01, "coef_cls": 1.0,
    }
    teacher = copy.deepcopy(common); teacher["net_cls"]="ensemble"; teacher["use_subsets"]=True
    student = copy.deepcopy(common); student["net_cls"]="eegnet";  student["use_subsets"]=False
    return teacher, student

def teacher_ckpt_path(fold): return os.path.join(TEACHER_DIR, f"teacher_fold{fold:02d}.pth")

def main():
    patch_braindecode_legacy()
    os.makedirs(OUT_DIR, exist_ok=True)
    teacher_dict, student_dict = build_args_dicts(MAX_EPOCHS)
    subj_csv = os.path.join(OUT_DIR, os.environ.get("QRD_SEEDS_OUT", "seeds_per_subject.csv"))
    if os.path.exists(subj_csv) and not os.environ.get("QRD_OVERWRITE"):
        sys.exit("ERROR: %s DA TON TAI. Dat QRD_SEEDS_OUT khac, hoac QRD_OVERWRITE=1 neu that su muon de." % subj_csv)
    subject_rows = []
    print(f"SEEDS={SEEDS} FOLDS={N_FOLDS} EPOCHS={MAX_EPOCHS} RUNS={[r[0] for r in RUNS]}")

    for seed in SEEDS:
        for fold in range(N_FOLDS):
            ckpt = teacher_ckpt_path(fold)
            assert os.path.exists(ckpt), f"missing teacher ckpt: {ckpt}"
            for tag, method, beta in RUNS:
                hp = dict(HP)
                if beta is not None: hp["beta_qrd"] = beta
                t_args = create_exp_args(exp_args_dict=teacher_dict, fold_idx=fold)
                s_args = create_exp_args(exp_args_dict=student_dict, fold_idx=fold)
                _t_run = time.time()
                res = train_method(method, s_args, t_args, ckpt, seed=seed, verbose=False, **hp)
                for sid, d in res["per_subject"].items():
                    subject_rows.append(dict(method=f"{tag}_s{seed}", tag=tag, seed=seed,
                                             fold=fold, subject=int(sid), acc=d["acc"], n=d["n"]))
                pd.DataFrame(subject_rows).to_csv(subj_csv, index=False)
                print(f"[{datetime.datetime.now():%H:%M:%S}][seed {seed}][fold {fold}] {tag}: "
                      f"acc={res['acc']:.2f} dt={time.time()-_t_run:.1f}s", flush=True)

    df = pd.DataFrame(subject_rows)
    print(f"\nSaved: {subj_csv}  ({df['method'].nunique()} method-seed combos)")
    for tag in sorted(set(r[0] for r in RUNS)):
        sub = df[df.tag==tag]
        # sigma_sub va min-subject PER SEED, roi lay mean+/-std QUA seed
        per_seed = sub.groupby("seed").apply(
            lambda g: pd.Series({"sigma_sub": g.groupby("subject").acc.mean().std(ddof=1),
                                 "min_sub":   g.groupby("subject").acc.mean().min()}),
            include_groups=False)
        print(f"{tag:<20} sigma_sub={per_seed.sigma_sub.mean():.2f}+/-{per_seed.sigma_sub.std(ddof=1):.2f} "
              f"| min_sub={per_seed.min_sub.mean():.2f}+/-{per_seed.min_sub.std(ddof=1):.2f}")

if __name__ == "__main__":
    main()
