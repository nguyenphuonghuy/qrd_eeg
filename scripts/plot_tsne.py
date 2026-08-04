################################################################
# scripts/plot_tsne.py  (qrd_eeg)
# Van de 12: ve lai Hinh 3 tu dac trung test THAT (results/tsne_feats_*/*.npz).
# 4 panel (no_kd, kd_base, feature_kd, qrd_teacher_guided), cung fold/seed,
# cung sieu tham so t-SNE (perplexity, random_state) cho ca 4 -> cong bang.
# Silhouette score tinh tren KHONG GIAN GOC 144 chieu (khong bi t-SNE bop meo).
# Chay tren login node duoc: chi numpy/sklearn/matplotlib tren du lieu nho.
################################################################
import os, json
import numpy as np
from sklearn.manifold import TSNE
from sklearn.metrics import silhouette_score
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

IN_DIR  = "/gpfs0/users/gv_nphuy/projects/qrd_eeg/results/tsne_feats_2026_08_03"
OUT_FIG = "/gpfs0/users/gv_nphuy/projects/qrd_eeg/paper/figs/image3.png"
OUT_META = "/gpfs0/users/gv_nphuy/projects/qrd_eeg/results/tsne_feats_2026_08_03/tsne_meta.json"

PANELS = [
    ("no_kd",             "(A) Không chưng cất"),
    ("kd_base",           "(B) KDBase"),
    ("feature_kd",        "(C) FeatureKD"),
    ("qrd_teacher_guided","(D) V5 Guided (lượng tử)"),
]
PERPLEXITY = 30
RANDOM_STATE = 42
LABEL_NAMES = {0: "Left hand", 1: "Right hand"}
COLORS = {0: "#d9605a", 1: "#5a8fd9"}

def main():
    meta = {"perplexity": PERPLEXITY, "random_state": RANDOM_STATE, "panels": {}}
    fig, axes = plt.subplots(2, 2, figsize=(11, 10))
    axes = axes.ravel()

    xy_all = []
    results = {}
    for tag, _ in PANELS:
        f = os.path.join(IN_DIR, f"tsne_feats_{tag}.npz")
        d = np.load(f, allow_pickle=True)
        feats, labels, subjects = d["feats"], d["labels"], d["subjects"]
        acc = float(d["acc"]); fold = int(d["fold"]); seed = int(d["seed"])
        sil = silhouette_score(feats, labels)
        tsne = TSNE(n_components=2, perplexity=PERPLEXITY, random_state=RANDOM_STATE,
                    init="pca", learning_rate="auto")
        xy = tsne.fit_transform(feats)
        results[tag] = dict(xy=xy, labels=labels, acc=acc, sil=sil,
                             n=feats.shape[0], n_subj=len(np.unique(subjects)))
        xy_all.append(xy)
        meta["panels"][tag] = dict(fold=fold, seed=seed, acc=acc, silhouette_144d=sil,
                                    n_test_trials=int(feats.shape[0]),
                                    n_subjects=int(len(np.unique(subjects))),
                                    feat_dim=int(feats.shape[1]))
        print(f"{tag}: acc={acc:.2f} silhouette(144d)={sil:.4f} n={feats.shape[0]}")

    xy_cat = np.concatenate(xy_all, axis=0)
    xlim = (xy_cat[:, 0].min() - 5, xy_cat[:, 0].max() + 5)
    ylim = (xy_cat[:, 1].min() - 5, xy_cat[:, 1].max() + 5)

    for ax, (tag, title) in zip(axes, PANELS):
        r = results[tag]
        for cls in (0, 1):
            m = r["labels"] == cls
            ax.scatter(r["xy"][m, 0], r["xy"][m, 1], s=22, alpha=0.7,
                       c=COLORS[cls], edgecolors="k", linewidths=0.3,
                       label=LABEL_NAMES[cls])
        ax.set_xlim(xlim); ax.set_ylim(ylim)
        ax.set_title(f"{title}\nacc={r['acc']:.1f}%, silhouette (144D)={r['sil']:.3f}", fontsize=10)
        ax.set_xlabel("t-SNE dim 1"); ax.set_ylabel("t-SNE dim 2")
        ax.legend(fontsize=8, loc="upper right")
        ax.grid(alpha=0.3)

    fig.suptitle(f"Đặc trưng student trên tập test (fold=0, seed=1), "
                 f"t-SNE perplexity={PERPLEXITY}, random_state={RANDOM_STATE}, cùng thang trục",
                 fontsize=11)
    fig.tight_layout(rect=[0, 0, 1, 0.96])
    fig.savefig(OUT_FIG, dpi=150)
    with open(OUT_META, "w") as fp:
        json.dump(meta, fp, indent=2)
    print("Da ghi:", OUT_FIG)
    print("Metadata:", OUT_META)

if __name__ == "__main__":
    main()
