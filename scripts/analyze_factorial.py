"""Phan tich thi nghiem giai thua ham nhan x chien luoc (docs/PREREG_ADDENDUM_FACTORIAL_2026_10_25.md).

Kiem dinh CHINH: tuong tac ham nhan x chien luoc trong ANOVA hai nhan to lap lai theo seed
(ca hai nhan to noi-seed), F(6, 24), alpha = 0.05. Phu: hieu ung chinh, chenh lech
luong tu - cosine / luong tu - RBF theo tung chien luoc (paired t, CI 95%, d_z, MDE hau nghiem).
Viet TRUOC khi co ket qua.

Dung: .stats_venv/bin/python3 -I scripts/analyze_factorial.py [--selftest]
"""
import os
import sys
import numpy as np
import pandas as pd
from scipy import stats

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RES = os.path.join(ROOT, "results")
OUT = os.path.join(RES, "factorial_2026_10_25", "analysis_factorial.txt")
SEEDS = [1, 2, 3, 4, 5]
KERNELS = ["quantum", "cosine", "rbf"]
STRATS = ["dense", "anchor", "global_local", "teacher_guided"]
CELLS = {  # (kernel, strategy) -> (file, tag)
    ("quantum", "dense"): ("factorial_2026_10_25/factorial_qdense_per_subject.csv", "qrd_dense_b0.02"),
    ("quantum", "anchor"): ("factorial_2026_10_25/factorial_qanchor_per_subject.csv", "qrd_anchor_b0.02"),
    ("quantum", "global_local"): ("factorial_2026_10_25/factorial_qgl_per_subject.csv", "qrd_global_local_b0.02"),
    ("quantum", "teacher_guided"): ("beta_robust_2026_10_24/beta_q002_per_subject.csv", "qrd_tg_b0.02"),
    ("cosine", "dense"): ([("factorial_2026_10_25/factorial_cosine_per_subject.csv", [1, 2, 3]),
                             ("factorial_2026_10_25/factorial_cosine_s45_per_subject.csv", [4, 5])], "ck_cosine_dense_b0.02"),
    ("cosine", "anchor"): ([("factorial_2026_10_25/factorial_cosine_per_subject.csv", [1, 2, 3]),
                             ("factorial_2026_10_25/factorial_cosine_s45_per_subject.csv", [4, 5])], "ck_cosine_anchor_b0.02"),
    ("cosine", "global_local"): ([("factorial_2026_10_25/factorial_cosine_per_subject.csv", [1, 2, 3]),
                             ("factorial_2026_10_25/factorial_cosine_s45_per_subject.csv", [4, 5])], "ck_cosine_global_local_b0.02"),
    ("cosine", "teacher_guided"): ("beta_robust_2026_10_24/beta_ref_classical_per_subject.csv", "ck_cosine_tg_b0.02"),
    ("rbf", "dense"): ("factorial_2026_10_25/factorial_rbf_per_subject.csv", "ck_rbf_dense_b0.02"),
    ("rbf", "anchor"): ("factorial_2026_10_25/factorial_rbf_per_subject.csv", "ck_rbf_anchor_b0.02"),
    ("rbf", "global_local"): ("factorial_2026_10_25/factorial_rbf_per_subject.csv", "ck_rbf_global_local_b0.02"),
    ("rbf", "teacher_guided"): ("beta_robust_2026_10_24/beta_ref_classical_per_subject.csv", "ck_rbf_tg_b0.02"),
}


def per_seed(path, tag):
    # path: mot file (lay seed 1-5) hoac danh sach (file, [seed]) -- o cosine gop seed 1-3 tu job 17755
    # (bi timeout) voi seed 4-5 tu job chay bu 17774; dong seed 4 dang do cua 17755 bi bo. Quy tac chot 2026-10-25 truoc khi co ket qua.
    parts = [(path, SEEDS)] if isinstance(path, str) else path
    df = pd.concat([pd.read_csv(os.path.join(RES, f)).loc[lambda d: d.seed.isin(sd)] for f, sd in parts])
    assert not df.duplicated(["tag", "seed", "fold", "subject"]).any(), (tag, "trung dong")
    df = df[(df.tag == tag) & (df.seed.isin(SEEDS))].assign(w=lambda d: d.acc * d.n)
    g = df.groupby(["seed", "subject"], as_index=False)[["w", "n"]].sum()
    assert (g.groupby("seed").subject.nunique() == 103).all(), (path, tag)
    g["a"] = g.w / g.n
    s = g.groupby("seed").a.mean()
    assert list(s.index) == SEEDS, (tag, list(s.index))
    return s.values


def rm_anova_2way(Y):
    """Y: mang (n_seed, a, b). ANOVA hai nhan to noi-chu-the. Tra ve dict hieu ung -> (F, df1, df2, p)."""
    n, a, b = Y.shape
    gm = Y.mean()
    mA = Y.mean(axis=(0, 2)); mB = Y.mean(axis=(0, 1)); mS = Y.mean(axis=(1, 2))
    mAB = Y.mean(axis=0); mSA = Y.mean(axis=2); mSB = Y.mean(axis=1)
    ssA = n * b * ((mA - gm) ** 2).sum()
    ssB = n * a * ((mB - gm) ** 2).sum()
    ssAB = n * ((mAB - mA[:, None] - mB[None, :] + gm) ** 2).sum()
    ssSA = b * ((mSA - mS[:, None] - mA[None, :] + gm) ** 2).sum()
    ssSB = a * ((mSB - mS[:, None] - mB[None, :] + gm) ** 2).sum()
    resid = Y - mSA[:, :, None] - mSB[:, None, :] - mAB[None, :, :] + mS[:, None, None] + mA[None, :, None] + mB[None, None, :] - gm
    ssSAB = (resid ** 2).sum()
    out = {}
    for name, ss, dfe, sse in [("kernel", ssA, (a - 1) * (n - 1), ssSA),
                               ("strategy", ssB, (b - 1) * (n - 1), ssSB),
                               ("interaction", ssAB, (a - 1) * (b - 1) * (n - 1), ssSAB)]:
        df1 = {"kernel": a - 1, "strategy": b - 1, "interaction": (a - 1) * (b - 1)}[name]
        F = (ss / df1) / (sse / dfe)
        out[name] = (F, df1, dfe, stats.f.sf(F, df1, dfe))
    return out


def paired(x, y):
    d = x - y; m = d.mean(); sd = d.std(ddof=1); h = stats.t.ppf(0.975, len(d) - 1) * sd / np.sqrt(len(d))
    return m, m - h, m + h, stats.ttest_rel(x, y).pvalue, m / sd if sd > 0 else np.nan, sd


def report(Y):
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from posthoc_mde_and_cho_ci import mde
    L = ["THI NGHIEM GIAI THUA HAM NHAN x CHIEN LUOC (KHAM PHA, prereg 2026-10-25)",
         "Gia tri moi seed = mean qua 103 doi tuong; seed 1-5; beta = 0.02.\n",
         "== Do chinh xac 12 o (mean +/- sd qua seed) =="]
    L.append("%-10s " % "" + " ".join("%18s" % s for s in STRATS))
    for i, k in enumerate(KERNELS):
        L.append("%-10s " % k + " ".join("%11.2f +/- %4.2f" % (Y[:, i, j].mean(), Y[:, i, j].std(ddof=1)) for j in range(len(STRATS))))
    A = rm_anova_2way(Y)
    L.append("\n== KIEM DINH CHINH: tuong tac ham nhan x chien luoc ==")
    F, d1, d2, p = A["interaction"]
    L.append("  F(%d, %d) = %.3f, p = %.4f" % (d1, d2, F, p))
    L.append("  DIEN GIAI THEO QUY TAC: " + ("CO TUONG TAC (p < 0.05), mo ta kieu tuong tac tu bang 12 o, khong suy rong."
                                          if p < 0.05 else "KHONG THAY BANG CHUNG VE TUONG TAC o muc cong suat cua thiet ke 5 seed (khong phai bang chung doc lap)."))
    L.append("\n== Phu (mo ta) ==")
    for name in ["kernel", "strategy"]:
        F, d1, d2, p = A[name]; L.append("  hieu ung chinh %-9s F(%d, %d) = %.3f, p = %.4f" % (name, d1, d2, F, p))
    for j, s in enumerate(STRATS):
        for k2 in ["cosine", "rbf"]:
            m, lo, hi, p, dz, sd = paired(Y[:, 0, j], Y[:, KERNELS.index(k2), j])
            L.append("  %-15s quantum - %-6s %+.3f [%+.3f, %+.3f] p=%.4f d_z=%+.2f MDE80=%.2f" % (s, k2, m, lo, hi, p, dz, mde(sd)))
    return "\n".join(L)


def main():
    if "--selftest" in sys.argv:
        rng = np.random.default_rng(0)
        Y = 81.5 + rng.normal(0, 0.4, (5, 1, 1)) + rng.normal(0, 0.3, (5, 3, 4))
        print(report(Y))
        Y2 = Y.copy(); Y2[:, 0, 3] -= 2.0  # tuong tac gia lap lon
        print("\n[selftest] tuong tac gia lap:", rm_anova_2way(Y2)["interaction"])
        return
    Y = np.stack([np.stack([per_seed(*CELLS[(k, s)]) for s in STRATS], axis=1) for k in KERNELS], axis=1)
    txt = report(Y)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    open(OUT, "w", encoding="utf-8").write(txt + "\n")
    print(txt); print("\nDa ghi", OUT)


if __name__ == "__main__":
    main()
