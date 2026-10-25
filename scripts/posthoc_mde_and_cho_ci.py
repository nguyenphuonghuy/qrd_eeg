"""Phan tich hau nghiem (dap Reviewer A, B, C), chi doc CSV co san:
(a) CI 95% va Cohen's d_z cho bang Cho2017 (so voi KDBase);
(b) hieu ung toi thieu phat hien duoc (MDE) o cong suat 80%, alpha = 0.05 hai phia,
    paired t-test n = 5, dung do lech chuan chenh lech ghep cap QUAN SAT (hau nghiem,
    khong phai tinh truoc). Tinh bang phan phoi t khong trung tam.

Dung: .stats_venv/bin/python3 -I scripts/posthoc_mde_and_cho_ci.py
"""
import os
import numpy as np
import pandas as pd
from scipy import stats, optimize

R = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
SEEDS = [1, 2, 3, 4, 5]


def per_seed(path, tag, n_subj):
    df = pd.read_csv(os.path.join(R, path))
    df = df[(df.tag == tag) & (df.seed.isin(SEEDS))].assign(w=lambda d: d.acc * d.n)
    g = df.groupby(["seed", "subject"], as_index=False)[["w", "n"]].sum()
    g["a"] = g.w / g.n
    assert (g.groupby("seed").subject.nunique() == n_subj).all(), (path, tag)
    s = g.groupby("seed").a.mean()
    assert list(s.index) == SEEDS, (tag, list(s.index))
    return s.values


def mde(sd, n=5, alpha=0.05, power=0.80):
    """Hieu ung (cung don vi voi sd) dat cong suat `power` cho paired t-test hai phia."""
    df = n - 1; tc = stats.t.ppf(1 - alpha / 2, df)
    def pw(nc):
        lower = np.nan_to_num(stats.nct.cdf(-tc, df, nc))  # duoi am, khong dang ke khi nc > 0
        return stats.nct.sf(tc, df, nc) + lower - power
    nc = optimize.brentq(pw, 1e-6, 10.0)
    return nc * sd / np.sqrt(n)


def compare(a, b):
    d = a - b; m = d.mean(); sd = d.std(ddof=1); se = sd / np.sqrt(len(d))
    h = stats.t.ppf(0.975, len(d) - 1) * se
    return m, m - h, m + h, stats.ttest_rel(a, b).pvalue, m / sd, sd


PHY = [  # (nhan, tag, file)
    ("No KD", "no_kd", "no_kd_alpha1_2026_08_03/no_kd_alpha1_per_subject.csv"),
    ("KDBase", "kd_base", "seeds_per_subject.csv"),
    ("FeatureKD", "feature_kd", "seeds2_per_subject.csv"),
    ("RelationalKD", "rkd_classical", "seeds2_per_subject.csv"),
    ("V1 Dense", "qrd_dense_noproj", "qrd_v1_rerun_2026_08_03/seeds_v1_rerun_per_subject.csv"),
    ("V2 Dense", "qrd_dense", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V3 Anchor", "qrd_anchor", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V4 Anchor+kNN", "qrd_global_local", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V5 quantum", "qrd_teacher_guided", "qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv"),
    ("V5 cosine", "ck_cosine_tg", "seeds2_per_subject.csv"),
    ("V5 RBF", "ck_rbf_tg", "seeds2_per_subject.csv"),
]
CHO = [
    ("No KD", "no_kd", "cho_no_kd_alpha1_2026_08_04/cho_no_kd_alpha1_per_subject.csv"),
    ("KDBase", "kd_base", "cho_kd_base_per_subject.csv"),
    ("FeatureKD", "feature_kd", "cho_feature_kd_per_subject.csv"),
    ("RelationalKD", "rkd_classical", "cho_rkd_classical_per_subject.csv"),
    ("V1 Dense", "qrd_dense_noproj", "cho_qrd_v1_per_subject.csv"),
    ("V2 Dense", "qrd_dense", "cho_qrd_all6_rerun_per_subject.csv"),
    ("V3 Anchor", "qrd_anchor", "cho_qrd_all6_rerun_per_subject.csv"),
    ("V4 Anchor+kNN", "qrd_global_local", "cho_qrd_all6_rerun_per_subject.csv"),
    ("V5 Guided", "qrd_teacher_guided", "cho_qrd_all6_rerun_per_subject.csv"),
    ("V5 beta=0.01", "qrd_tg_b0.01", "cho_qrd_all6_rerun_per_subject.csv"),
    ("V5 beta=0.05", "qrd_tg_b0.05", "cho_qrd_all6_rerun_per_subject.csv"),
    ("Cosine", "ck_cosine_tg", "cho_ck_cosine_tg_per_subject.csv"),
    ("RBF", "ck_rbf_tg", "cho_ck_rbf_tg_per_subject.csv"),
]


def table(rows, n_subj, title, kernel_pairs):
    V = {lab: per_seed(f, tag, n_subj) for lab, tag, f in rows}
    ref = V["KDBase"]; out = []
    print("\n== %s ==" % title)
    print("%-16s %7s %5s %7s %17s %7s %6s %6s %6s" % ("config", "acc", "sd", "delta", "CI95", "p", "d_z", "sd_d", "MDE80"))
    for lab, _, _ in rows:
        v = V[lab]
        if lab == "KDBase":
            print("%-16s %7.2f %5.2f" % (lab, v.mean(), v.std(ddof=1))); out.append(dict(config=lab, acc=v.mean(), sd=v.std(ddof=1))); continue
        m, lo, hi, p, dz, sdd = compare(v, ref); M = mde(sdd)
        print("%-16s %7.2f %5.2f %+7.2f  [%+6.2f, %+6.2f] %7.4f %+6.2f %6.2f %6.2f" % (lab, v.mean(), v.std(ddof=1), m, lo, hi, p, dz, sdd, M))
        out.append(dict(config=lab, acc=v.mean(), sd=v.std(ddof=1), delta=m, ci_lo=lo, ci_hi=hi, p=p, dz=dz, sd_diff=sdd, mde80=M))
    for a, b in kernel_pairs:
        m, lo, hi, p, dz, sdd = compare(V[a], V[b]); M = mde(sdd)
        print("%-16s %13s %+7.2f  [%+6.2f, %+6.2f] %7.4f %+6.2f %6.2f %6.2f" % ("%s-%s" % (a, b), "", m, lo, hi, p, dz, sdd, M))
        out.append(dict(config="%s - %s" % (a, b), delta=m, ci_lo=lo, ci_hi=hi, p=p, dz=dz, sd_diff=sdd, mde80=M))
    return pd.DataFrame(out)


def main():
    a = table(PHY, 103, "PhysionetMI (so voi KDBase) + MDE hau nghiem", [("V5 quantum", "V5 cosine"), ("V5 quantum", "V5 RBF"), ("V1 Dense", "V2 Dense")])
    b = table(CHO, 49, "Cho2017 (so voi KDBase) + MDE hau nghiem", [("V5 Guided", "Cosine"), ("V5 Guided", "RBF")])
    a.assign(dataset="PhysionetMI").to_csv(os.path.join(R, "posthoc_mde_physionet.csv"), index=False)
    b.assign(dataset="Cho2017").to_csv(os.path.join(R, "posthoc_cho2017_ci_mde.csv"), index=False)
    print("\nDa ghi results/posthoc_mde_physionet.csv va results/posthoc_cho2017_ci_mde.csv")


if __name__ == "__main__":
    main()
