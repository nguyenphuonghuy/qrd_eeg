# QRD-EEG: controlled multi-seed evaluation of relational knowledge distillation for motor imagery decoding

Code, job scripts, logs, fold assignments, teacher checkpoints, and per-seed
results for the manuscript *"A Controlled Multi-Seed Evaluation of Relational
Knowledge Distillation for Motor Imagery Decoding with Classical and Quantum
Kernels"* (under revision at the International Journal of Robotics and Control
Systems).

The study distils an Ensemble-MI teacher into a compact EEGNet student and
varies two design axes of relational distillation: the relation-formation
strategy (five variants, V1–V5) and the similarity kernel (cosine, RBF,
quantum). The quantum kernel is used only during training and never appears in
the deployed student. Every comparison uses subject-wise 5-fold
cross-validation, five fixed seeds, and the seed as the unit of inference.
PhysionetMI (103 subjects) is the confirmatory dataset; Cho2017 (49 subjects)
is an exploratory replication.

Code comments and internal notes are partly in Vietnamese (without
diacritics), for historical reasons.

## 1. Repository layout

```
scripts/              Training and analysis code
                        train_all.py   training logic and METHOD_TABLE (all methods)
                        run_seeds.py   multi-seed runs, configured by environment variables
                        run_all.py     single fixed seed (20200220), many methods
                        analyze_*.py, effect_sizes_main_table.py,
                        posthoc_mde_and_cho_ci.py   statistical analyses in the paper
jobs/                 PBS job scripts actually used to produce every result
logs/                 Logs of those jobs
results/              Per-subject CSV files (one row per seed x fold x subject)
results/fold_assignment_{physionet,cho2017}.csv   subject-to-fold assignment
checkpoints/          Ensemble-MI teacher checkpoints, 5 folds, PhysionetMI
checkpoints_cho2017/  Teacher checkpoints, 5 folds, Cho2017
external_patches/     Patch applied to the upstream Ensemble-MI repository
docs/                 Frozen design and analysis plans (see Section 5)
paper/                LaTeX sources (Vietnamese body.tex, English body_en.tex,
                      IJRCS submission in paper/ijrcs_submission/)
```

## 2. Environment

Python 3.11 with the versions below (exact lock file:
`requirements-lock_2026-10-03.txt`).

| Package | Version |
|---|---|
| torch | 2.7.1 (+cu118) |
| pennylane | 0.45.1 |
| mne | 1.12.1 |
| braindecode | 1.4.0 |
| moabb | 1.5.0 |
| scikit-learn | 1.9.0 |
| numpy | 2.4.4 |
| pandas | 3.0.3 |
| scipy | 1.17.1 |

The teacher architecture, data pipeline, and Riemannian alignment come from the
upstream [Ensemble-MI](https://github.com/gzoumpourlis/Ensemble-MI) repository
(Zoumpourlis and Patras), which is not redistributed here. Clone it at commit
`b7d8e9f` and apply the patch in `external_patches/`:

```bash
git clone https://github.com/gzoumpourlis/Ensemble-MI.git external/Ensemble-MI
cd external/Ensemble-MI
git checkout b7d8e9f
git apply ../../external_patches/ensemble_mi_b7d8e9f.patch
export ENSEMBLE_MI_DIR=$(pwd)
```

The patch sets the trial window to 3.0 s (upstream: 4.0 s), adjusts the
corresponding temporal output size of EEGNet (`n_out_time` 12 -> 9), selects
the dataset through `QRD_DATASET`, and fixes two compatibility issues (pandas
`append`, missing `subset` key in validation/test batches).

All scripts must be run with `$ENSEMBLE_MI_DIR` as the working directory,
because the upstream code locates `preprocessed_data/` through `os.getcwd()`.
PhysionetMI and Cho2017 are downloaded by MOABB on first use and cached as
`.pkl` files, which are not tracked in git.

## 3. Reproducing the experiments

`run_seeds.py` produces every multi-seed number in the paper. It is configured
through environment variables:

| Variable | Meaning | Default |
|---|---|---|
| `QRD_SEEDS` | comma-separated seeds | `1,2,3,4,5` |
| `QRD_FOLDS` | subset of folds to run (split still uses 5 folds) | all |
| `QRD_MAX_EPOCHS` | student epochs | `30` |
| `QRD_RUNS` | `tag:method[:beta],...` | three QRD methods |
| `QRD_DATASET` | `PhysionetMI` or `Cho2017` | `PhysionetMI` |
| `QRD_OUT_DIR`, `QRD_SEEDS_OUT` | output directory and CSV name | `results/`, `seeds_per_subject.csv` |
| `QRD_TEACHER_DIR` | teacher checkpoint directory | `checkpoints/` |
| `QRD_ALPHA` | cross-entropy weight alpha | `0.5` |
| `QRD_OVERWRITE` | set to `1` to overwrite an existing output CSV | unset |

Example (V1–V5 with the quantum kernel, five seeds, PhysionetMI):

```bash
cd "$ENSEMBLE_MI_DIR"
export QRD_TEACHER_DIR=/path/to/qrd_eeg/checkpoints
export QRD_OUT_DIR=/path/to/qrd_eeg/results/repro QRD_SEEDS_OUT=v1_v5.csv
export QRD_RUNS="qrd_dense_noproj:qrd_dense_noproj,qrd_dense:qrd_dense,qrd_anchor:qrd_anchor,qrd_global_local:qrd_global_local,qrd_teacher_guided:qrd_teacher_guided"
python /path/to/qrd_eeg/scripts/run_seeds.py
```

Each file in `jobs/` records the exact variables used for one experiment. The
`#PBS` headers are specific to our cluster; the body of each script runs on any
machine with a GPU. GPU training uses non-deterministic cuDNN kernels, so reruns
deviate by up to about 0.4 percentage points from the published numbers (see
the reproducibility table and Appendix C of the paper).

## 4. Results files

Every `*_per_subject.csv` has the columns `method, tag, seed, fold, subject,
acc, n`. Each subject is in the test set of exactly one fold. A per-seed value
is the mean over subjects of the n-weighted accuracy; all tests in the paper are
paired over the five per-seed values (n = 5, df = 4).

`results/fold_assignment_*.csv` lists, for each subject, its block (subjects in
code order split into five consecutive blocks), the test fold index used by the
code, and the validation block. The code's fold `k` uses block `4 - k` as the
test set and the next block cyclically as the validation set; the remaining
three blocks form the training set. The split does not depend on the seed.

| Experiment | Results | Analysis script |
|---|---|---|
| Main table (12 configurations) | `seeds_per_subject.csv`, `seeds2_per_subject.csv`, `qrd_seeds_rerun_2026_07_30/`, `qrd_v1_rerun_2026_08_03/`, `no_kd_alpha1_2026_08_03/` | `effect_sizes_main_table.py` |
| Gradient-matched beta experiment | `beta_robust_2026_10_24/` | `analyze_beta_addendum.py` |
| Kernel x strategy factorial | `factorial_2026_10_25/` | `analyze_factorial.py` |
| Minimum detectable effects, Cho2017 CIs | as above, `cho_*` | `posthoc_mde_and_cho_ci.py` |
| Design controls (theta, W_T, projected kernels, pool64) | `theta_mode_ablation_2026_08_04/`, `wt_fixed_control_2026_08_05/`, `kernel_fair_2026_08_03/`, `pool64_control_2026_08_04/` | in the job logs |
| Seeds 6–10 extension | `seeds6to10_extension_2026_08_09/` | in the job logs |
| Qubit scaling | `qubit_scaling_smoke_2026_08_05/`, `qubit_v2_full_2026_08_05/` | in the job logs |
| Raspberry Pi 4 latency | `pi4_latency/` | `bench_pi4.py`, `run5_pi4.sh` |

Statistical scripts use only pandas, numpy, and scipy and run on a CPU.

## 5. Analysis plans

`docs/DESIGN.md` is the experimental design. `docs/PREREG_2026_07_30.md`,
`docs/PREREG_ADDENDUM_BETA_2026_10_24.md`, and
`docs/PREREG_ADDENDUM_FACTORIAL_2026_10_25.md` are internal analysis plans
written before the corresponding runs. They were not registered on a public
registry. The first plan entered version control on 2026-08-02, after its runs
had finished; the two addenda and the factorial merging rule were committed and
pushed before their results were examined (commits `2b39c81` and `e43a347`).

## 6. Building the paper

```bash
cd paper/
tectonic main_en.tex          # English version
tectonic main.tex             # Vietnamese version (XeLaTeX, polyglossia)
cd ijrcs_submission && tectonic IJRCS_submission.tex
```

The IJRCS version inputs `../body_en.tex` and uses `IEEEtran_doi.bst`, a copy
of IEEEtran.bst that prints DOIs.

## Citation

The manuscript is under revision; citation details will be added after
publication.
