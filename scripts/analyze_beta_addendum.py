"""Phan tich thi nghiem beta theo docs/PREREG_ADDENDUM_BETA_2026_10_24.md.

Don vi thong ke: subject. Gop: mean co trong so n trong tung (tag, seed, subject),
roi mean qua subject -> mot gia tri moi seed. So sanh: paired t-test tren 5 seed
chung, alpha = 0.05 hai phia, CI 95%, Cohen's d_z. Bien tuong duong delta = 0.5 pp.

Chi dung so lieu dot chay moi (results/beta_robust_2026_10_24). So lieu cu chi
duoc in rieng de doi chieu tai lap, khong dung trong so sanh.

Dung: .stats_venv/bin/python3 -I scripts/analyze_beta_addendum.py
"""
import os
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "results", "beta_robust_2026_10_24")
OUT_TXT = os.path.join(RES, "analysis_beta_addendum.txt")
OUT_CSV = os.path.join(RES, "analysis_beta_addendum_per_seed.csv")
DELTA = 0.5
SEEDS = [1, 2, 3, 4, 5]

# tag -> (ham nhan, beta)
CONFIGS = {
    "qrd_tg_b0.02": ("quantum", 0.02), "qrd_tg_b0.1": ("quantum", 0.1), "qrd_tg_b0.5": ("quantum", 0.5),
    "ck_cosine_tg_b0.02": ("cosine", 0.02), "ck_cosine_tg_b0.1": ("cosine", 0.1),
    "ck_cosine_tg_b0.5": ("cosine", 0.5), "ck_cosine_tg_b4.0": ("cosine", 4.0),
    "ck_rbf_tg_b0.02": ("rbf", 0.02), "ck_rbf_tg_b0.1": ("rbf", 0.1),
    "ck_rbf_tg_b0.2": ("rbf", 0.2), "ck_rbf_tg_b0.5": ("rbf", 0.5),
    "kd_base_ref": ("kdbase", None),
}
NEW = ["ck_cosine_tg_b4.0", "ck_rbf_tg_b0.2", "ck_cosine_tg_b0.1", "ck_cosine_tg_b0.5",
       "ck_rbf_tg_b0.1", "ck_rbf_tg_b0.5", "qrd_tg_b0.1", "qrd_tg_b0.5"]


def per_seed(df):
    """Gia tri moi seed: mean qua subject cua acc co trong so n trong (tag, seed, subject)."""
    df = df.assign(w=df.acc * df.n)
    g = df.groupby(["tag", "seed", "subject"], as_index=False)[["w", "n"]].sum()
    g["acc_s"] = g.w / g.n
    return g.groupby(["tag", "seed"]).acc_s.mean().unstack("seed")


def paired(a, b):
    d = np.asarray(a, float) - np.asarray(b, float)
    n = len(d); m = d.mean(); sd = d.std(ddof=1); se = sd / np.sqrt(n)
    t, p = stats.ttest_rel(a, b)
    h = stats.t.ppf(0.975, n - 1) * se
    return dict(diff=m, ci_lo=m - h, ci_hi=m + h, t=t, p=p, dz=m / sd if sd > 0 else np.nan, n=n)


def verdict(r):
    if -DELTA <= r["ci_lo"] and r["ci_hi"] <= DELTA:
        return "TUONG DUONG (CI nam tron trong +/-0.5 pp)"
    if r["p"] < 0.05:
        return "KHAC BIET CO Y NGHIA (p < 0.05), chieu: %s" % ("dau > sau" if r["diff"] > 0 else "dau < sau")
    if r["p"] <= 0.10:
        return "KHONG CO Y NGHIA (p trong [0.05; 0.10]); CI vuot bien -> KHONG DU DU LIEU"
    return "KHONG DU DU LIEU (p > 0.05, CI vuot bien +/-0.5 pp)"


def fmt(name, r):
    return ("%-44s diff=%+.3f pp  CI95=[%+.3f, %+.3f]  t=%+.3f  p=%.4f  d_z=%+.3f  (n=%d)"
            % (name, r["diff"], r["ci_lo"], r["ci_hi"], r["t"], r["p"], r["dz"], r["n"]))


def main():
    frames = [pd.read_csv(os.path.join(RES, f)) for f in sorted(os.listdir(RES))
              if f.endswith("_per_subject.csv")]
    df = pd.concat(frames, ignore_index=True)
    assert set(df.tag) == set(CONFIGS), sorted(set(df.tag) ^ set(CONFIGS))
    assert df.isna().sum().sum() == 0
    S = per_seed(df)[SEEDS]
    assert S.notna().all().all() and S.shape == (len(CONFIGS), 5)
    S.to_csv(OUT_CSV)

    L = []
    L.append("PHAN TICH THI NGHIEM BETA (PREREG ADDENDUM 2026-10-24)")
    L.append("Don vi: subject; gia tri moi seed = mean qua 103 subject; paired t-test tren seed 1-5.\n")
    L.append("== Do chinh xac moi cau hinh (mean +/- sd qua 5 seed) ==")
    for tag in sorted(CONFIGS, key=lambda k: (CONFIGS[k][0], CONFIGS[k][1] or 0)):
        v = S.loc[tag]
        L.append("  %-22s %-8s beta=%-5s %.2f +/- %.2f   seeds=%s" % (
            tag, CONFIGS[tag][0], CONFIGS[tag][1], v.mean(), v.std(ddof=1),
            " ".join("%.2f" % x for x in v)))

    L.append("\n== SO SANH CHINH (chot truoc): luong tu beta=0.02 VS cosine beta=4.0 ==")
    r = paired(S.loc["qrd_tg_b0.02"], S.loc["ck_cosine_tg_b4.0"])
    L.append("  " + fmt("quantum(0.02) - cosine(4.0)", r))
    L.append("  KET LUAN THEO QUY TAC: " + verdict(r))

    L.append("\n== So sanh phu (mo ta, khong hieu chinh da so sanh) ==")
    r2 = paired(S.loc["qrd_tg_b0.02"], S.loc["ck_rbf_tg_b0.2"])
    L.append("  " + fmt("quantum(0.02) - rbf(0.2)", r2) + "  -> " + verdict(r2))
    for a, b in [("qrd_tg_b0.02", "ck_cosine_tg_b0.02"), ("qrd_tg_b0.02", "ck_rbf_tg_b0.02")]:
        rr = paired(S.loc[a], S.loc[b])
        L.append("  " + fmt("%s - %s (cung beta danh nghia, dot moi)" % (a, b), rr))
    L.append("  -- Moi cau hinh moi va tham chieu so voi KDBase (kd_base_ref, dot moi) --")
    for tag in NEW + ["qrd_tg_b0.02", "ck_cosine_tg_b0.02", "ck_rbf_tg_b0.02"]:
        L.append("  " + fmt("%s - KDBase" % tag, paired(S.loc[tag], S.loc["kd_base_ref"])))

    L.append("\n== Bang lieu-dap ung theo beta (dot moi) ==")
    for k in ["quantum", "cosine", "rbf"]:
        tags = sorted([t for t in CONFIGS if CONFIGS[t][0] == k], key=lambda t: CONFIGS[t][1])
        L.append("  %-8s " % k + "  ".join("b=%s: %.2f" % (CONFIGS[t][1], S.loc[t].mean()) for t in tags))

    # Doi chieu tai lap voi so lieu cu (chi in, khong dung de so sanh)
    L.append("\n== Doi chieu voi so lieu cu dung trong ban thao (KHONG dung trong phan tich tren) ==")
    old = {
        "qrd_teacher_guided": os.path.join(ROOT, "results", "qrd_seeds_rerun_2026_07_30", "seeds_quantum_rerun_per_subject.csv"),
        "ck_cosine_tg": os.path.join(ROOT, "results", "seeds2_per_subject.csv"),
        "ck_rbf_tg": os.path.join(ROOT, "results", "seeds2_per_subject.csv"),
        "kd_base": os.path.join(ROOT, "results", "seeds_per_subject.csv"),
    }
    pair_new = {"qrd_teacher_guided": "qrd_tg_b0.02", "ck_cosine_tg": "ck_cosine_tg_b0.02",
                "ck_rbf_tg": "ck_rbf_tg_b0.02", "kd_base": "kd_base_ref"}
    for tag, path in old.items():
        o = pd.read_csv(path); o = o[(o.tag == tag) & (o.seed.isin(SEEDS))]
        so = per_seed(o).loc[tag][SEEDS]; sn = S.loc[pair_new[tag]]
        L.append("  %-20s cu %.2f +/- %.2f | moi %.2f +/- %.2f | moi-cu %+.2f pp" % (
            tag, so.mean(), so.std(ddof=1), sn.mean(), sn.std(ddof=1), sn.mean() - so.mean()))

    txt = "\n".join(L)
    open(OUT_TXT, "w", encoding="utf-8").write(txt + "\n")
    print(txt)
    print("\nDa ghi:", OUT_TXT, "va", OUT_CSV)


if __name__ == "__main__":
    main()
