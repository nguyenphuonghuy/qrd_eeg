"""Effect size va CI 95% cho bang ket qua chinh PhysionetMI (dap Reviewer A, C).

Cung cach gop voi phan tich chinh: gia tri moi seed = mean qua subject (acc co
trong so n trong tung subject), paired t-test tren seed 1-5 so voi KDBase.
ITR tinh tu do chinh xac trung binh theo cong thuc Wolpaw, N = 2, T = 3,0 s.

Dung: .stats_venv/bin/python3 -I scripts/effect_sizes_main_table.py
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
SEEDS = [1, 2, 3, 4, 5]
T_WIN = 3.0
# (nhan hien thi, tag, file)
ROWS = [
    ("No KD (alpha=1.0)", "no_kd", "no_kd_alpha1_2026_08_03/no_kd_alpha1_per_subject.csv"),
    ("KDBase", "kd_base", "seeds_per_subject.csv"),
    ("FeatureKD", "feature_kd", "seeds2_per_subject.csv"),
    ("RelationalKD", "rkd_classical", "seeds2_per_subject.csv"),
    ("V1 Dense", "qrd_dense_noproj", "qrd_v1_rerun_2026_08_03/seeds_v1_rerun_per_subject.csv"),
    ("V2 Dense", "qrd_dense", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V3 Anchor", "qrd_anchor", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V4 Anchor+kNN", "qrd_global_local", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V5 Guided (quantum)", "qrd_teacher_guided", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V5 cosine", "ck_cosine_tg", "seeds2_per_subject.csv"),
    ("V5 RBF", "ck_rbf_tg", "seeds2_per_subject.csv"),
]


def per_seed(path, tag):
    df = pd.read_csv(os.path.join(R, path))
    df = df[(df.tag == tag) & (df.seed.isin(SEEDS))].assign(w=lambda d: d.acc * d.n)
    g = df.groupby(["seed", "subject"], as_index=False)[["w", "n"]].sum()
    g["a"] = g.w / g.n
    s = g.groupby("seed").a.mean()
    assert list(s.index) == SEEDS, (tag, list(s.index))
    assert (g.groupby("seed").subject.nunique() == 103).all(), tag
    return s.values


def itr(acc_pct, n=2, t=T_WIN):
    p = acc_pct / 100.0
    b = np.log2(n) + p * np.log2(p) + (1 - p) * np.log2((1 - p) / (n - 1))
    return b, b * 60.0 / t


def main():
    vals = {lab: per_seed(f, tag) for lab, tag, f in ROWS}
    ref = vals["KDBase"]
    print("%-22s %8s %6s %8s %18s %7s %6s %6s %6s" % ("config", "acc", "sd", "delta", "CI95", "p", "d_z", "B", "ITR"))
    out = []
    for lab, _, _ in ROWS:
        v = vals[lab]; m = v.mean(); sd = v.std(ddof=1); b, r = itr(m)
        if lab == "KDBase":
            print("%-22s %8.2f %6.2f %8s %18s %7s %6s %6.3f %6.2f" % (lab, m, sd, "--", "--", "--", "--", b, r))
            out.append(dict(config=lab, acc=m, sd=sd, B=b, ITR=r)); continue
        d = v - ref; md = d.mean(); se = d.std(ddof=1) / np.sqrt(5); h = stats.t.ppf(0.975, 4) * se
        p = stats.ttest_rel(v, ref).pvalue; dz = md / d.std(ddof=1)
        print("%-22s %8.2f %6.2f %+8.2f   [%+6.2f, %+6.2f] %7.3f %+6.2f %6.3f %6.2f" % (lab, m, sd, md, md - h, md + h, p, dz, b, r))
        out.append(dict(config=lab, acc=m, sd=sd, delta=md, ci_lo=md - h, ci_hi=md + h, p=p, dz=dz, B=b, ITR=r))
    pd.DataFrame(out).to_csv(os.path.join(R, "effect_sizes_main_table.csv"), index=False)
    print("\nDa ghi results/effect_sizes_main_table.csv")


if __name__ == "__main__":
    main()
