################################################################
# scripts/run_all.py  (qrd_eeg)
# Driver: chay toan bo ma tran method x fold -> 1 file ket qua.
# Doc duong dan tu bien moi truong (chuan kd_full):
#   ENSEMBLE_MI_DIR : repo Ensemble-MI trong external/ (them vao sys.path)
#   QRD_TEACHER_DIR : thu muc chua teacher_fold0*.pth
#   QRD_OUT_DIR     : noi ghi results_all.xlsx (mac dinh results/)
################################################################
import os, sys, copy, time, argparse, datetime, random
import numpy as np
import pandas as pd
import torch

sys.dont_write_bytecode = True

# --- wire repo Ensemble-MI tu bien moi truong (khong hardcode) ---
_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path:
    sys.path.insert(0, _REPO)
# them thu muc scripts/ (chua train_all.py cua ta) vao path
_SELF = os.path.dirname(os.path.abspath(__file__))
if _SELF not in sys.path:
    sys.path.insert(0, _SELF)

from src.config import *
from src.args_utils import create_exp_args
from train_all import (
    patch_braindecode_legacy, train_method, evaluate_teacher,
    init_dataset, init_net, METHOD_TABLE,
)

TEACHER_DIR = os.environ.get("QRD_TEACHER_DIR",
                             os.path.join(os.path.dirname(__file__), "..", "checkpoints"))
OUT_DIR = os.environ.get("QRD_OUT_DIR",
                         os.path.join(os.path.dirname(__file__), "..", "results"))
N_FOLDS = 5
DEFAULT_EPOCHS = 30
GLOBAL_SEED = 1312

HP = dict(
    alpha=0.5, temperature=4.0, beta_qrd=0.02, gamma_feat=1.0, gamma_rkd=1.0,
    n_qubits=int(os.environ.get("QRD_N_QUBITS", "4")), n_q_layers=2,
    qrd_batch_size=16, num_anchors=8, knn_k=4,
    entropy_weight=0.5, disagreement_weight=0.5,
)
DEFAULT_METHODS = [
    "no_kd", "kd_base", "feature_kd", "rkd_classical",
    "qrd_dense", "qrd_anchor", "qrd_global_local", "qrd_teacher_guided",
    "ck_cosine_tg", "ck_rbf_tg",
]

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
        "use_scheduler": False, "warmup": False,
        "cuda": torch.cuda.is_available(),
        "exp_group": datetime.datetime.now().strftime("%Y_%m_%d-%H%M%S"),
        "max_epochs": max_epochs, "warmup_epochs": 0,
        "optim": "sgd", "lr": 0.005, "momentum": 0.9, "weight_decay": 0.01,
        "coef_cls": 1.0,
    }
    teacher = copy.deepcopy(common); teacher["net_cls"]="ensemble"; teacher["use_subsets"]=True
    student = copy.deepcopy(common); student["net_cls"]="eegnet";  student["use_subsets"]=False
    return teacher, student

def teacher_ckpt_path(teacher_dir, fold):
    return os.path.join(teacher_dir, f"teacher_fold{fold:02d}.pth")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--folds", type=str, default=",".join(str(f) for f in range(N_FOLDS)))
    ap.add_argument("--methods", type=str, default=",".join(DEFAULT_METHODS))
    ap.add_argument("--epochs", type=int, default=DEFAULT_EPOCHS)
    ap.add_argument("--out", type=str, default=os.path.join(OUT_DIR, "results_all.xlsx"))
    ap.add_argument("--teacher_dir", type=str, default=TEACHER_DIR)
    ap.add_argument("--skip_teacher", action="store_true")
    a = ap.parse_args()

    folds = [int(x) for x in a.folds.split(",") if x != ""]
    methods = [m.strip() for m in a.methods.split(",") if m.strip()]
    for m in methods:
        assert m in METHOD_TABLE, f"unknown method '{m}'. Options: {list(METHOD_TABLE)}"

    # repo create_exp_args() tu parse sys.argv -> xoa flag cua ta di
    sys.argv = [sys.argv[0]]

    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    random.seed(GLOBAL_SEED); np.random.seed(GLOBAL_SEED); torch.manual_seed(GLOBAL_SEED)
    if torch.cuda.is_available(): torch.cuda.manual_seed_all(GLOBAL_SEED)

    patch_braindecode_legacy()
    teacher_dict, student_dict = build_args_dicts(a.epochs)

    rows, t0 = [], time.time()
    subject_rows = []
    subj_csv = a.out.replace('.xlsx', '_per_subject.csv')
    for fold in folds:
        ckpt = teacher_ckpt_path(a.teacher_dir, fold)
        assert os.path.exists(ckpt), f"missing teacher checkpoint: {ckpt}"

        if not a.skip_teacher:
            t_args = create_exp_args(exp_args_dict=teacher_dict, fold_idx=fold)
            device = "cuda" if torch.cuda.is_available() else "cpu"
            prog = os.path.join(os.getcwd(), "results", t_args.dataset_name, "teacher_eval", t_args.exp_group)
            os.makedirs(prog, exist_ok=True); t_args.progress_folder = prog
            _, _, dl_test, dinfo = init_dataset(args=t_args)
            teacher = init_net(t_args, dinfo).to(device)
            teacher.load_state_dict(torch.load(ckpt, map_location=device), strict=True)
            tm = evaluate_teacher(dl_test, teacher, device)
            rows.append(dict(method="teacher", fold=fold, acc=tm["acc"], kappa=tm["kappa"], f1=tm["f1"], mean_epoch_time=0.0))
            print(f"[fold {fold}] teacher: acc={tm['acc']:.2f} kappa={tm['kappa']:.3f} f1={tm['f1']:.3f}")
            del teacher

        for method in methods:
            t_args = create_exp_args(exp_args_dict=teacher_dict, fold_idx=fold)
            s_args = create_exp_args(exp_args_dict=student_dict, fold_idx=fold)
            res = train_method(method, s_args, t_args, ckpt, verbose=True, **HP)
            rows.append(dict(method=method, fold=fold, acc=res["acc"], kappa=res["kappa"], f1=res["f1"], mean_epoch_time=res["mean_epoch_time"]))
            for sid, d in res["per_subject"].items():
                subject_rows.append(dict(method=method, fold=fold, subject=int(sid), acc=d["acc"], n=d["n"]))
            pd.DataFrame(rows).to_excel(a.out, index=False)
            pd.DataFrame(subject_rows).to_csv(subj_csv, index=False)

        # --- beta-sensitivity: qrd_teacher_guided x beta in {0.01,0.05} (0.02 da co) ---
        if "qrd_teacher_guided" in methods:
            for _beta in (0.01, 0.05):
                _hp = dict(HP); _hp["beta_qrd"] = _beta
                _tag = f"qrd_tg_b{_beta}"
                _ta = create_exp_args(exp_args_dict=teacher_dict, fold_idx=fold)
                _sa = create_exp_args(exp_args_dict=student_dict, fold_idx=fold)
                _res = train_method("qrd_teacher_guided", _sa, _ta, ckpt, verbose=True, **_hp)
                rows.append(dict(method=_tag, fold=fold, acc=_res["acc"], kappa=_res["kappa"], f1=_res["f1"], mean_epoch_time=_res["mean_epoch_time"]))
                for sid, d in _res["per_subject"].items():
                    subject_rows.append(dict(method=_tag, fold=fold, subject=int(sid), acc=d["acc"], n=d["n"]))
                pd.DataFrame(rows).to_excel(a.out, index=False)
                pd.DataFrame(subject_rows).to_csv(subj_csv, index=False)
                print(f"[fold {fold}] {_tag}: acc={_res['acc']:.2f}")
            print(f"[fold {fold}] {method}: acc={res['acc']:.2f} kappa={res['kappa']:.3f} f1={res['f1']:.3f}")

    df = pd.DataFrame(rows); df.to_excel(a.out, index=False)
    pd.DataFrame(subject_rows).to_csv(subj_csv, index=False)
    def agg(g):
        return pd.Series({"acc_mean":g["acc"].mean(),"acc_std":g["acc"].std(ddof=1),
                          "kappa_mean":g["kappa"].mean(),"kappa_std":g["kappa"].std(ddof=1),
                          "f1_mean":g["f1"].mean(),"epoch_time":g["mean_epoch_time"].mean(),
                          "n_folds":g["acc"].count()})
    summary = df.groupby("method", sort=False).apply(agg).reset_index()
    order = ["teacher"] + methods
    summary["__o"] = summary["method"].apply(lambda m: order.index(m) if m in order else 999)
    summary = summary.sort_values("__o").drop(columns="__o").reset_index(drop=True)
    sp = a.out.replace(".xlsx", "_summary.xlsx"); summary.to_excel(sp, index=False)
    print("\n" + "="*70 + "\nSUMMARY (mean +/- std)\n" + "="*70)
    for _, r in summary.iterrows():
        print(f"{r['method']:>20s} | acc {r['acc_mean']:5.2f}+/-{r['acc_std']:.2f} | kappa {r['kappa_mean']:.3f} | f1 {r['f1_mean']:.3f} | {r['epoch_time']:.1f}s/ep | n={int(r['n_folds'])}")
    print(f"\nSaved: {a.out} and {sp}\nWall: {(time.time()-t0)/60:.1f} min")

if __name__ == "__main__":
    main()
