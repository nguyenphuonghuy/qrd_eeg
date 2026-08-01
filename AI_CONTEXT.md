# AI_CONTEXT — qrd_eeg

| Item | Value |
|---|---|
| Project | qrd_eeg (Quantum/Neighborhood Relational Distillation for MI-EEG) |
| Version | 1.0 |
| Status | Đang dựng — code + design xong; env đang cài; CHƯA chạy end-to-end |
| Last Updated | 2026-07-20 |

Đọc file này CÙNG `hpc_ai/docs/HPC_CONTEXT.md` (sự thật cluster) + `TROUBLESHOOTING.md`
(sự cố) + `docs/DESIGN.md` (thiết kế thí nghiệm đã đóng băng) trước khi hỗ trợ.

---

# 1. Mục tiêu

Distillation quan hệ (relational KD) cho EEG motor imagery, khảo sát vai trò của
quantum encoding. Định vị TRUNG THỰC (xem DESIGN.md):
- Đóng góp chính KHÔNG phải "quantum tăng accuracy" (lý thuyết + dữ liệu chống lại).
- Pha 1 (trọng tâm): neighborhood-structure relational distillation + framing
  "variance regularizer" — giảm variance CROSS-SUBJECT (claim chính C2).
- Pha 2 (optional, high-risk): Riemannian-covariance encoding.
- Mức tham vọng quantum: GIỮ MỞ, kết quả quyết định nhãn cuối.

Teacher = Ensemble-MI (Zoumpourlis 2024). Student = EEGNet. Dataset = PhysionetMI.

---

# 2. Đường dẫn

| Thành phần | Đường dẫn |
|---|---|
| Project root | /gpfs0/users/gv_nphuy/projects/qrd_eeg |
| Env | /gpfs0/users/gv_nphuy/envs/qrd_env  (LƯU Ý: tên qrd_env, KHÁC qrd_eeg — do sự cố NFS/conda khi tạo qrd_eeg, xem mục Known issues) |
| Python | /gpfs0/users/gv_nphuy/envs/qrd_env/bin/python |
| Repo bên thứ ba | external/Ensemble-MI (clone github.com/gzoumpourlis/Ensemble-MI @ b7d8e9f8) |
| conda pkgs cache | /gpfs0/users/gv_nphuy/conda_pkgs (BẮT BUỘC export CONDA_PKGS_DIRS trỏ vào đây — /opt/anaconda3/pkgs read-only) |
| Data (.pkl) | external/Ensemble-MI/preprocessed_data/PhysionetMI/ (103 file, DA sinh — preprocess_dataset.py, cwd=repo) |
| MNE_DATA (raw .edf) | /gpfs0/users/gv_nphuy/datasets/mne_data (BAT BUOC gpfs0; ~/mne_data = local login node, compute node KHONG thay — xem TROUBLESHOOTING 8) |
| Teacher ckpt | checkpoints/teacher_fold00..04.pth (DA train: 84.98%±2.59%, 5 fold x 120ep) |
| Scripts của ta | scripts/{train_all.py, run_all.py, run_riemann.py, run_ensemble.py, setup_env.sh} |
| Design freeze | docs/DESIGN.md |

---

# 3. Môi trường (cách tái lập)

- Python 3.11 (BẮT BUỘC ≥3.11 vì braindecode 1.4.0 yêu cầu).
- torch 2.7.1+cu118, torchvision 0.22.1+cu118 (khớp driver 570; KHÔNG cu13).
- braindecode==1.4.0, moabb==1.5.0, mne, pennylane, scikit-learn, pyriemann,
  openpyxl, pandas.
- Tái lập: `bash scripts/setup_env.sh` (đã nhúng CONDA_PKGS_DIRS + thứ tự torch-trước).
- Cài torch TRƯỚC braindecode/moabb (tránh kéo torch về CUDA sai — TROUBLESHOOTING mục 5).

---

# 4. Dataset & Protocol (đã kiểm chứng qua chẩn đoán)

- PhysionetMI (eegmmidb) qua MOABB. 103 subject (loại 88,90,92,100,104,106).
- Nhị phân left_hand(0)/right_hand(1); 64 kênh; bandpass 4-38Hz; CAR; resample 100Hz.
- Window 3.0s = 300 mẫu (PATCH t_dur 4.0->3.0). EEGNet n_out_time=9 => feat-dim 144.
- LOSO 5-fold (use_folds): 62 train / 21 val / 20 test subject. Mỗi subject vào test
  đúng 1 lần => per-subject acc well-defined trên đủ 103 subject.
- Batch có sẵn 'subject' (custom_dataset __getitem__) => per-subject metrics không cần
  sửa repo.

---

# 5. Quyết định thí nghiệm quan trọng

- BỎ 5 teacher checkpoint cũ (từ notebook Colab), TRAIN TEACHER MỚI trên HPC.
  Lý do: teacher chỉ là kết quả train của repo (tái tạo được); train mới trên chính
  data regenerate + env HPC => teacher-data-student TỰ KHỚP, bỏ mọi rủi ro tương thích.
- Đơn vị thống kê = SUBJECT (không phải fold). Report mean±std trên 103 subject.
  Significance: Wilcoxon paired theo subject (n=103). Variance: Levene vs no_kd.
  (Giải quyết dứt lỗi Wilcoxon-5-fold của bản thảo cũ.)
- Tham số CỐ ĐỊNH theo chuẩn cộng đồng (Cách 3, xem DESIGN mục 6):
  alpha=0.5, T=4.0, beta_qrd=0.02 (+sensitivity {0.01,0.05}), gamma_feat=gamma_rkd=1.0,
  n_qubits=4, n_q_layers=2. Backbone kế thừa nguyên teacher gốc.
- Quantum circuit: random-FROZEN (không train) ở Pha 1 — trung thực coi là fixed
  quantum feature map, so sánh sòng phẳng với cosine/RBF.

---

# 6. Patch repo external/Ensemble-MI (ghi rõ để tái lập)

Clone @ b7d8e9f8 rồi áp 2 patch:
- preprocess_dataset.py : 't_dur': 4.0 -> 3.0   (khớp moabb 1.5.0 chia trial 3s)
- models/eegnet.py + models/ensemble.py : n_out_time = 12 -> 9   (feat 16x9=144)
Lệnh: sed -i "s/'t_dur': 4.0/'t_dur': 3.0/" preprocess_dataset.py ;
      sed -i "s/n_out_time = 12/n_out_time = 9/" models/eegnet.py models/ensemble.py

---

# 7. Scripts của ta (trong scripts/, KHÔNG sửa external/)

- train_all.py : trainer hợp nhất mọi method (teacher/no_kd/kd_base/feature_kd/
  rkd_classical/qrd_*/ck_*). Đọc repo qua sys.path (ENSEMBLE_MI_DIR). Có per-subject
  metrics + kernel-dump (bật bằng QRD_KERNEL_DUMP) + fix braindecode _raw.
- run_all.py : driver ma trận method x fold; xuất results_all.xlsx + _per_subject.csv
  + beta-sensitivity. Biến env: ENSEMBLE_MI_DIR, QRD_TEACHER_DIR, QRD_OUT_DIR.
- run_riemann.py : baseline Covariances->TangentSpace->LDA (pyriemann), per-subject.
- run_ensemble.py : baseline no-KD x 5 seed + ensemble logits (bảo vệ C2 variance).
- setup_env.sh : cài env một lệnh.
- CHƯA TEST: run_riemann/run_ensemble viết theo API đã verify nhưng chưa chạy —
  điểm rủi ro: shape batch['eeg'] cho Covariances/EEGNet, use_subsets. Chỉnh sau khi chạy.

---

# 8. Ma trận chạy (DESIGN mục 5)

Ladder KD: teacher, no_kd, kd_base, feature_kd, rkd_classical, qrd_dense, qrd_anchor,
qrd_global_local, qrd_teacher_guided, ck_cosine_tg, ck_rbf_tg.
Sensitivity: qrd_teacher_guided x beta {0.01,0.05}.
Baseline: run_ensemble.py (deep_ensemble_nokd), run_riemann.py (riemann_ts_lda).

---

# 9. Known issues (đã gặp — bài học, chi tiết ở TROUBLESHOOTING)

- conda pkgs cache /opt/anaconda3/pkgs READ-ONLY với user => conda create lỗi link
  package + rollback. FIX: export CONDA_PKGS_DIRS=/gpfs0/users/gv_nphuy/conda_pkgs.
- conda create trên /gpfs0 RẤT CHẬM (thao tác nhiều file nhỏ qua NFS): ~150 file/phút,
  một env cơ bản mất ~15-30 phút (có khi hơn). ĐANG TIẾN chứ không kẹt — đo bằng
  find|wc -l cách nhau 60s: >0 file/60s = đang chạy, cứ chờ. KHÔNG ngắt.
- Tiến trình conda/rm treo trạng thái D (uninterruptible), kill -9 không được — tự
  thoát khi NFS phản hồi. Đừng chờ, dùng tên env khác để né.
- braindecode 1.4.0 cần Python >=3.11 (env 3.10 KHÔNG cài được -> phải dựng 3.11).
- moabb 1.5.0 chia trial PhysionetMI = 3s (300 mẫu) => phải t_dur=3.0, n_out_time=9.
- import torch/moabb/mne trên login node dễ TREO (NFS cold-read) — verify import phải
  chạy QUA PBS (compute node), không trên login node.
- MPS treo init CUDA — mọi PBS GPU phải export CUDA_MPS_PIPE_DIRECTORY=/dev/null.
- Submit mọi job qua sharedgpu (workq = can never run).
- pooch tải dataset hay treo — nếu gặp, tải bằng urllib (mẫu kd_full/scripts/download_bnci.py).

---

# 10. Lệnh thường dùng

```bash
export CONDA_PKGS_DIRS=/gpfs0/users/gv_nphuy/conda_pkgs   # luon export truoc conda/pip
PROJ=/gpfs0/users/gv_nphuy/projects/qrd_eeg
PY=/gpfs0/users/gv_nphuy/envs/qrd_env/bin/python
# smoke test (sau khi co env + data + teacher):
export ENSEMBLE_MI_DIR=$PROJ/external/Ensemble-MI
export QRD_TEACHER_DIR=$PROJ/checkpoints
cd $PROJ && $PY scripts/run_all.py --folds 0 --epochs 3 --methods no_kd,kd_base,qrd_teacher_guided,ck_rbf_tg --skip_teacher
```

---

# 11. Trạng thái & bước tiếp (cập nhật mỗi phiên)

XONG: cấu trúc dự án, clone+patch repo, DESIGN.md, train_all/run_all/run_riemann/
run_ensemble (syntax OK, CHƯA test), setup_env.sh, AI_CONTEXT.md.
ĐANG: cài env qrd_env (conda create chậm do NFS).
TIẾP THEO (thứ tự): (1) bash setup_env.sh; (2) verify import QUA PBS; (3) regenerate
data QUA PBS; (4) train teacher; (5) GPU smoke test run_all.py 1 fold; (6) full run;
(7) code việc 5 (cost/FLOPs) + phân tích per-subject/variance.


## CẬP NHẬT 2026-07-21 (phiên train teacher)
TRẠNG THÁI: env + verify + data + teacher đã XONG. Sẵn sàng chạy student/KD.

XONG:
- (1) env qrd_env đủ. FIX: torchaudio bị kéo cu13 (2.11.0) khi cài braindecode →
  cài lại torchaudio==2.7.1+cu118. Bộ ba torch/vision/audio 2.7.1+cu118, pip check sạch.
- (2) verify import QUA PBS: 8/8 lib OK, cuda.is_available()=True (H100).
- (3) DATA: 103 .pkl tại external/Ensemble-MI/preprocessed_data/PhysionetMI/.
  BÀI HỌC (TROUBLESHOOTING mục 8): raw phải ở /gpfs0 (không phải ~/mne_data = local
  login node), sửa cả ~/.mne/mne-python.json (đè env). Data:
  /gpfs0/users/gv_nphuy/datasets/mne_data.
- (4) TEACHER: train bằng repo run_experiment.py (run_all.py chỉ NẠP+eval, KHÔNG train).
  5 fold x 120 epoch, n_subsets=7. Mean 84.98% ± 2.59%
  (fold: 84.56/80.78/87.83/84.13/87.62). 5 ckpt → checkpoints/teacher_fold00..04.pth
  (gốc repo: net_best_<ts>_fold_XX.pth).

TIẾP THEO:
- (5) GPU SMOKE run_all.py: 1 fold, ít epoch, --skip_teacher, vài method. Verify
  student/KD pipeline + teacher ckpt nạp được. Bọc đủ: CUDA_MPS_PIPE_DIRECTORY=/dev/null,
  MNE_DATA + MNE_DATASETS_EEGBCI_PATH=/gpfs0/.../datasets/mne_data, cwd=external/Ensemble-MI,
  log ghi sống (exec>LOG).
- (6) FULL RUN ma trận method (DESIGN mục 5). (7) cost/FLOPs + per-subject/variance (C2).

NHẮC HẠ TẦNG (đã trả giá phiên này, xem TROUBLESHOOTING 7-8):
- Trần 1 gpu_slot + 64gb mem/user. Job hay kẹt E giữ slot → qdel -W force, xác nhận
  qstat trống TRƯỚC khi submit job mới.
- Data PBS phải trên /gpfs0; mne config đè env.
- Smoke: n_folds=5 + fold_range=[0] (KHÔNG n_folds=1 → vỡ split).
- "Applying preprocessors" braindecode CHẬM qua NFS (nhiều phút), không phải treo.

## CẬP NHẬT 2026-07-21 (smoke run_all — PASS)
(5) GPU SMOKE run_all.py: PASS (fold 0, 3ep, rc=0, xuất results_all.xlsx). Pipeline
student/KD verified. LƯU Ý số acc ~52% + std=nan là do smoke (3ep, 1 fold) — KHÔNG
đánh giá method; chờ full run 30ep/5fold.

2 BUG ĐÃ FIX trong scripts/ (run_all/train_all CHƯA test trước đó → smoke lộ ra):
- run_all.py: import "from src.train_all" SAI (train_all ở scripts/, không ở repo src/).
  FIX: thêm scripts/ vào sys.path (_SELF) + đổi thành "from train_all import".
- train_all.py _states(): mạch quantum pennylane chạy CPU nhưng angles/q_weights ở
  cuda → RuntimeError device mismatch. FIX: angles.cpu() (GIỮ grad, không detach, để
  student_proj học qua mạch) + q_weights.cpu(), chạy mạch CPU, states.to(dev0) về GPU.
  (.bak: scripts/*.py.bak)

HỆ QUẢ cho full run: quantum method chậm ~15-18x (18s/ep vs 1s/ep non-quantum, vì
mạch chạy CPU). Full run (5 fold x 30ep x nhiều QRD method) sẽ NHIỀU GIỜ → đặt
walltime rộng, không hoảng khi chạy lâu.

TIẾP: (6) FULL RUN ma trận method đầy đủ (DESIGN mục 5). Lệnh như smoke nhưng bỏ
--folds/--epochs (dùng mặc định 5 fold, 30 epoch) + đủ 11 method + sensitivity.

## CẬP NHẬT 2026-07-21 (full run XONG)
(6) FULL RUN: rc=0, Wall 214.7min, 12 method × 5 fold. Kết quả trong results/
(results_all.xlsx, _summary.xlsx, _per_subject.csv — 103 subj/method).
ACC (std TRÊN FOLD, KHÔNG phải σ_sub): no_kd 58.23 | các method distill ~80.7-81.7
(kd_base 81.08, qrd_teacher_guided 81.62±1.96, ck_rbf_tg 81.52...).
→ KD teacher→student (Ensemble-MI→EEGNet) HIỆU QUẢ MẠNH (58→81, ~+23pp).
→ Ladder distill PHẲNG về acc (<1pp chênh) — ĐÚNG DESIGN, bài KHÔNG đấu acc.
CẢNH BÁO PHÂN TÍCH: cột +/- trong log = std trên 5 FOLD, KHÔNG phải σ_sub (subject).
C2 phải tính σ_sub từ _per_subject.csv (103 subj) + Levene vs no_kd (DESIGN mục 8-9).
TIẾP: phiên phân tích — tính σ_sub, Levene/Wilcoxon per-subject, dựng T1-T5/F1-F5.
Baseline nhóm C (run_ensemble/run_riemann) CHƯA test, làm sau.

## CẬP NHẬT 2026-07-21 (PHA 2 — full run nhóm C XONG + phân tích C2)
(7) FULL nhóm C: rc_riemann=0, rc_ensemble=0 (job 11429, ~1h13, walltime 5h).
    Output: results/riemann_per_subject.csv, results/ensemble_per_subject.csv (103 subj mỗi method).
    - riemann_ts_lda : 58.73% | σ_sub=8.32  -> BÁM no_kd, KHÔNG mạnh.
      => LẬT giả định DESIGN mục 7 dòng 145 (Riemann NGANG/HƠN teacher). Thực tế thua distill ~22pp.
    - deep_ensemble_nokd : 80.24% | σ_sub=11.31 -> ngang distill về acc, σ ≈ kd_base/qrd.
    - Ensemble chỉ giảm σ 4.1% so single-seed (11.79->11.31): "ensemble tầm thường" cũng KHÔNG giảm variance.

(8) VERDICT C2 (đơn vị SUBJECT, n=103):
    - Pre-registered vs no_kd: FAIL. Mọi method distill/ensemble có σ_sub CAO HƠN no_kd (relRed âm).
      Confound: no_kd sát chance (58%) nén acc về sàn -> σ nhỏ cơ học, không phải qrd kém.
    - vs kd_base & vs deep_ensemble (cùng ~80-81% acc, phép so công bằng):
      KHÔNG significant. Levene p>0.45; Pitman-Morgan paired chỉ qrd_tg_b0.05 p=0.037,
      TAN sau Bonferroni (×11≈0.40), dưới ngưỡng 15%.
    => C2 = PARTIAL/diagnostic (đúng dự phòng DESIGN mục 9 dòng 173-174, 234). VẪN CÓ BÀI.

(9) ĐÓNG GÓP THẬT = low-tail robustness (KHÔNG phải giảm σ tổng):
    min-subject: qrd 53-56 > deep_ensemble 48.9 > kd_base 44.4.
    #subj<70%: qrd_tg_b0.05=15 (thấp nhất nhóm high-acc). CV thấp nhất qrd_tg_b0.05=12.89.
    CẢNH BÁO HONEST: F3(b) qrd vs ensemble = 51 lifted / 52 lowered -> KHÔNG thắng ensemble
    trên toàn dân số, chỉ hơn ở ĐUÔI DƯỚI. Không được viết "qrd beats ensemble".

(10) ARTIFACT đã dựng (bản local, chờ ghép Overleaf):
    T1_accuracy.{csv,tex}, T2_variance.{csv,tex} [bảng cốt lõi C2],
    F2_box_violin.{pdf,png}, F3_paired_scatter.{pdf,png} (2 panel: vs no_kd, vs ensemble),
    results_discussion.tex (~1190 từ, honest, no em-dash).
    Label chờ khớp khi chèn hình: fig:f2_dist, fig:f3_paired; bảng: tab:t1_acc, tab:t2_var.
    Cần \usepackage{booktabs}. T1/T2 chỉ có acc-based (per-subject CSV chỉ có acc);
    kappa/F1 ở results_all_summary.xlsx là FOLD-level, phải chú thích nếu dùng.

TIẾP: ghép Results/Discussion + T1-T2 + F2-F3 vào Overleaf; T3-T5/F1,F4,F5 nếu cần; ~80 refs.

## HÀNG ĐỢI VIỆC -> xem docs/TODO_NEXT.md
(1a seed-variance ĐANG LÀM, 1b bootstrap CI, 2 dataset thứ hai; + nợ Overleaf/refs)

## CẬP NHẬT 2026-07-22 (1a SEED-VARIANCE XONG — ĐẢO CHIỀU LỚN)
(11) JOB 11431: rc=0, 75 run (5 seed × 5 fold × 3 method), Elap 5h14, walltime 8h.
     Out: results/seeds_per_subject.csv (1545 dòng; cột method,tag,seed,fold,subject,acc,n).
     Script: scripts/run_seeds.py (wrapper riêng, KHÔNG sửa train_method; truyền seed= xuống).

(12) ⚠️ CLAIM LOW-TAIL BỊ BÁC BỎ — min-subject qua 5 seed:
     kd_base 48.44±4.27 | qrd_teacher_guided 48.44±4.82 | qrd_tg_b0.05 48.89±4.71
     => KHÔNG phân biệt được. Khoảng cách 11pp (qrd 55.6 vs kd_base 44.4) trong run gốc
     CHỈ LÀ NHIỄU SEED: cả hai nằm trong cùng phân phối 48.4±4.8.
     σ_sub cũng vậy: 11.62/11.50/11.55 (±0.4-0.5). Không phân biệt.
     => Mục "What the method does contribute" trong results_discussion.tex PHẢI BỎ.

(13) ✅ KẾT QUẢ MỚI = ĐÓNG GÓP TRUNG TÂM (mạnh hơn claim cũ):
     PHÂN RÃ PHƯƠNG SAI (n=1545): SUBJECT 87.2% | Residual 12.5% | SEED 0.2% | METHOD 0.0%
     (method = 14/205257 SS). Seed giải thích nhiều gấp 32× method.
     Trong biến thiên subject: 93.8% within-fold (cá nhân), chỉ 6.2% between-fold
     => variance là NỘI TẠI của người dùng, không phải artifact chia fold.
     XẾP HẠNG ĐẢO CHIỀU QUA SEED: kd_base thắng seed 1,2,5 | qrd_tg thắng seed 3,4.
     => Chạy single-seed có thể ra kết luận NGƯỢC NHAU. Đây là cảnh báo phương pháp luận.

(14) SÀN NHIỄU (số dùng cho bài): nhiễu seed 0.65pp (trên acc trung bình 5 fold)
     vs khoảng cách method 0.22pp => nhiễu GẤP 2.9×.
     LƯU Ý: 1.56pp là nhiễu trên acc MỘT FOLD đơn lẻ; so sánh công bằng phải dùng 0.65pp.

(15) ARTIFACT MỚI: T3_variance_decomposition.{csv,tex} [bảng cốt lõi MỚI],
     F4_variance_and_seed.{pdf,png} (a: bar phân rã, b: đường acc × seed, xếp hạng đảo chiều),
     F5_minsubject_seeds.{pdf,png} (min-subject ± sai số seed, chồng lấn hoàn toàn).
     Label: tab:t3_vardecomp. Cần \usepackage{booktabs}.

(16) ⚠️ CAVEAT T1/T2 CŨ: 11/14 method vẫn SINGLE-SEED. Với sàn nhiễu 0.65pp,
     mọi so sánh <0.65pp trong T1/T2 KHÔNG đáng tin. Phải ghi rõ hoặc chạy seed mở rộng.
     T3 hiện chỉ phủ 3 method -> khi viết PHẢI nói rõ ma trận seed chạy trên tập con đại diện.

(17) KHUNG BÀI MỚI: "distillation +23pp mạnh & ổn định, NHƯNG mọi biến thể tương đương
     trong giới hạn nhiễu huấn luyện; variance cross-subject là nội tại (87% do subject);
     so sánh single-seed trong EEG-KD không đáng tin". Negative/methodological result có ích.
