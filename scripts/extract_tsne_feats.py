################################################################
# scripts/extract_tsne_feats.py  (qrd_eeg)
# Van de 12 (Hinh 3 t-SNE): trich dac trung student THAT tren TAP TEST cho
# 4 method (no_kd, kd_base, feature_kd, qrd_teacher_guided), 1 fold + 1 seed
# co dinh, de ve lai Hinh 3 co the tai lap (co dung 4 panel, cung fold/seed,
# cung sieu tham so t-SNE khi ve o buoc sau).
# KHONG sua train_method (chi truyen save_test_feats=True).
################################################################
import os, sys, copy
import numpy as np
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
FOLD        = int(os.environ.get("QRD_TSNE_FOLD", "0"))
SEED        = int(os.environ.get("QRD_TSNE_SEED", "1"))
MAX_EPOCHS  = int(os.environ.get("QRD_MAX_EPOCHS", "30"))

METHODS = [("no_kd", "no_kd"), ("kd_base", "kd_base"),
           ("feature_kd", "feature_kd"), ("qrd_teacher_guided", "qrd_teacher_guided")]
_only = os.environ.get("QRD_TSNE_ONLY")
if _only:
    METHODS = [m for m in METHODS if m[0] in _only.split(",")]

HP = dict(alpha=0.5, temperature=4.0, beta_qrd=0.02, gamma_feat=1.0, gamma_rkd=1.0,
          n_qubits=4, n_q_layers=2, qrd_batch_size=16, num_anchors=8, knn_k=4,
          entropy_weight=0.5, disagreement_weight=0.5)

def build_args_dicts(max_epochs):
    common = {
        "use_folds": True, "n_folds": 5, "resume": False, "resume_exp_id": "",
        "n_subsets": 7, "ensemble_loss_1": True, "ensemble_loss_2": True,
        "loss_2_single_expert": False, "n_modules_stage_1": 4,
        "stage_1_is_shared": False, "stage_2_is_shared": True, "feats_aggr": "mean",
        "pre_align": True, "dataset_name": os.environ.get("QRD_DATASET", "PhysionetMI"),
        "batch_size": 64, "batch_size_val": 64,
        "backbone_k_width": 1, "dropout_input": 0.4, "dropout_1": 0.1,
        "load_ckpt": False, "ckpt_file": "", "checkpoint": "best",
        "use_scheduler": False, "warmup": False, "cuda": torch.cuda.is_available(),
        "exp_group": "tsne_feats",
        "max_epochs": max_epochs, "warmup_epochs": 0,
        "optim": "sgd", "lr": 0.005, "momentum": 0.9, "weight_decay": 0.01, "coef_cls": 1.0,
    }
    teacher = copy.deepcopy(common); teacher["net_cls"]="ensemble"; teacher["use_subsets"]=True
    student = copy.deepcopy(common); student["net_cls"]="eegnet";  student["use_subsets"]=False
    return teacher, student

def main():
    patch_braindecode_legacy()
    os.makedirs(OUT_DIR, exist_ok=True)
    teacher_dict, student_dict = build_args_dicts(MAX_EPOCHS)
    ckpt = os.path.join(TEACHER_DIR, f"teacher_fold{FOLD:02d}.pth")
    assert os.path.exists(ckpt), f"missing teacher ckpt: {ckpt}"
    print(f"FOLD={FOLD} SEED={SEED} EPOCHS={MAX_EPOCHS} METHODS={[m[0] for m in METHODS]}")

    for tag, method in METHODS:
        t_args = create_exp_args(exp_args_dict=teacher_dict, fold_idx=FOLD)
        s_args = create_exp_args(exp_args_dict=student_dict, fold_idx=FOLD)
        # No KD khong co so hang distillation de can bang nen phai dung
        # alpha=1.0 (full cross-entropy), giong moi noi khac trong bai
        # (xem body_en.tex Muc 4.1); HP['alpha']=0.5 chi dung cho cac
        # method CO distillation. Sua audit docs/AUDIT_PAPER_CODE_2026_10_03.md
        # muc 3 (truoc day dung chung 0.5 cho ca 4 panel).
        hp_tag = dict(HP, alpha=1.0) if tag == "no_kd" else HP
        res = train_method(method, s_args, t_args, ckpt, seed=SEED, verbose=True,
                            save_test_feats=True, **hp_tag)
        out_path = os.path.join(OUT_DIR, f"tsne_feats_{tag}.npz")
        np.savez(out_path,
                 feats=res["test_feats"], labels=res["test_labels"],
                 subjects=res["test_subjects"], acc=res["acc"],
                 alpha=hp_tag["alpha"],
                 method=method, fold=FOLD, seed=SEED)
        print(f"[{tag}] acc={res['acc']:.2f} n_test={res['test_feats'].shape[0]} "
              f"feat_dim={res['test_feats'].shape[1]} -> {out_path}")

if __name__ == "__main__":
    main()
