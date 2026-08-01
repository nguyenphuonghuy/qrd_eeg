# TODO_NEXT — qrd_eeg (hàng đợi việc, tick dần)
*Cập nhật 2026-07-21. Đọc cùng AI_CONTEXT mục Pha 2 (dòng ~225).*

## ĐANG LÀM
- [ ] **1a. Seed-variance** (bảo vệ đóng góp low-tail — ưu tiên cao).
      wrapper: scripts/run_seeds.py. Job: jobs/{smoke,full}_seeds.pbs.
      Scope FULL đã chọn: 5 seed × 3 run (kd_base, qrd_teacher_guided, qrd_tg_b0.05) × 5 fold (~2.5h).
      Env: QRD_SEEDS, QRD_N_FOLDS, QRD_MAX_EPOCHS. Out: results/seeds_per_subject.csv (method="{tag}_s{seed}").
      TRẠNG THÁI: smoke (2 seed×3 run×3 fold) — kiểm rc=0 VÀ acc khác nhau giữa seed rồi mới full.
      MỤC TIÊU SỐ: min-subject & σ_sub mean±std QUA seed -> "min_sub qrd = 55.6 ± X (5 seed)".

## CHỜ LÀM
- [ ] **1b. Bootstrap CI** cho min-subject / #subj<70% / CV (KHÔNG cần cluster).
      Làm từ per-subject CSV đã có (pivot_all). Biến quan sát 1-điểm thành có thanh sai số.
      Ghép vào T2 hoặc chú thích F2/F3. Claude chạy local được ngay.
- [ ] **2. Dataset thứ hai** (BNCI2014001/2a — đã có trong project kd_full) — QUYẾT ĐỊNH LỚN.
      Vá limitation lớn nhất (kết luận variance đang dựa 1 dataset, 2-class).
      Nếu low-tail robustness tái hiện -> finding mạnh, đáng đăng. Tốn công nhất.

## KHÔNG LÀM (đã cân nhắc, loại)
- Thêm baseline giảm-variance thứ 3 (SWA/MC-dropout) để "cứu" C2:
  ensemble đã chứng minh variance là nội tại subject -> chỉ tái khẳng định, không đổi verdict.
- Quét hyperparameter tìm cấu hình qrd σ nhỏ nhất: p-hacking, phản honest.

## NỢ KHÁC (từ AI_CONTEXT)
- [ ] Ghép Results/Discussion + T1-T2 + F2-F3 vào Overleaf (label fig:f2_dist, fig:f3_paired; \usepackage{booktabs}).
- [ ] T3-T5 / F1,F4,F5 nếu paper cần (DESIGN mục 10).
- [ ] ~80 references.
- [ ] T1 kappa/F1 nếu cần: từ results_all_summary.xlsx (FOLD-level, phải chú thích).

## QUY ƯỚC HẠ TẦNG (rút từ phiên 2026-07-21)
- **walltime FULL = 12h mặc định** (timeout trong script ~11h/39600s).
  Cluster này cấp slot ngay bất kể walltime -> xin rộng KHÔNG mất gì.
  Ước lượng hay hụt (preprocess ~27s/fold cộng dồn; quantum 30ep nặng hơn nhiều so 2ep).
- **Nút thắt thật = job kẹt E giữ slot.** LUÔN `qdel -W force <id>` + xác nhận qstat TRỐNG
  trước mỗi lần submit. Đã kẹt: 11425, 11426, 11428, 11429, 11430.
- Smoke vẫn để walltime ngắn (40 phút) — giúp phát hiện treo sớm.
- Script dài PHẢI ghi kết quả tăng dần (append/ghi lại CSV sau mỗi bước) để job bị cắt
  vẫn dùng được phần đã xong + chạy bù phần thiếu (vd QRD_SEEDS=5).

---
# CẬP NHẬT 2026-07-22 (sau khi 1a xong)

## ĐÃ XONG
- [x] **1a. Seed-variance** — XONG (job 11431). Kết quả BÁC BỎ claim low-tail,
      nhưng sinh ra đóng góp mới mạnh hơn (T3/F4/F5). Xem AI_CONTEXT mục 11-17.

## HỦY
- [~] **1b. Bootstrap CI** — HỦY. Sinh ra để bảo vệ claim low-tail; claim đó đã bị
      seed-variance bác bỏ. Bootstrap trên hiệu ứng không tồn tại chỉ ra CI của nhiễu.

## ĐANG LÀM / SẮP LÀM (đã quyết: làm CẢ HAI)
- [ ] **1c. MỞ RỘNG SEED ra 9 method còn lại** (vá lỗ hổng "T3 chỉ 3/14 method").
      9 method: no_kd, feature_kd, rkd_classical, ck_cosine_tg, ck_rbf_tg,
                qrd_dense, qrd_anchor, qrd_global_local, qrd_tg_b0.01
      × 5 seed × 5 fold ≈ 7.7h. Job: jobs/full_seeds2.pbs (ĐÃ SOẠN, CHƯA SUBMIT).
      ⚠️ CHƯA XÁC NHẬN đã chạy lệnh sửa run_seeds.py nhận env QRD_RUNS/QRD_SEEDS_OUT.
         Phải kiểm: grep -nE "QRD_RUNS|QRD_SEEDS_OUT" scripts/run_seeds.py
      Out: results/seeds2_per_subject.csv (dích 45 combo, 4635 dòng) -> ghép với
      seeds_per_subject.csv thành ma trận 12 method × 5 seed cho T3 đầy đủ.
- [ ] **2. Dataset thứ hai** (tính khái quát).
      ⚠️ KHÔNG DÙNG BNCI2014001/2a: chỉ 9 subject -> quá yếu cho phân tích cross-subject
         (sức mạnh hiện tại đến từ n=103); và 2a thường dùng within-subject.
      NÊN: Cho2017 (52 subj) hoặc Lee2019/OpenBMI (54 subj).
      Chi phí thật KHÔNG ở chạy job mà ở: dựng tiền xử lý + train teacher mới (120ep×5fold)
      + gỡ lỗi path/import. Ước 2-4 phiên.
      VIỆC ĐẦU TIÊN (recon, rẻ): xem repo hỗ trợ dataset nào sẵn / có dùng MOABB không:
        cd external/Ensemble-MI
        grep -rnE "PhysionetMI|BNCI|Cho2017|Lee2019|moabb|dataset_name" src/*.py preprocess_dataset.py | head -30
        grep -nE "add_argument|dataset|def main" preprocess_dataset.py | head -20
      Nếu backend là MOABB -> rẻ hơn nhiều. Nếu hardcode PhysionetMI -> đắt, cân nhắc lại.

## NỢ VIẾT (sau khi có số)
- [ ] **VIẾT LẠI results_discussion.tex theo khung mới** (bản cũ CÒN chứa claim low-tail đã bị bác).
- [ ] Ghép T1-T3 + F2-F5 vào Overleaf; sửa DESIGN mục 9/10 lần nữa cho khớp khung mới.
- [ ] ~80 references.

# CẬP NHẬT 2026-07-30 (lỗi mạch lượng tử)

## ĐANG LÀM
- [ ] Chạy check_circuit.pbs, xác nhận 3 tiêu chí:
      sai khác kernel vs tích cosine > 0.05; requires_grad=True; grad != 0
- [ ] Nếu đạt: chạy lại 7 cấu hình quantum (xem PREREG_2026_07_30.md)

## CHỜ LÀM
- [ ] Tính lại Bảng 2,3,4,5,6 từ số liệu mới
- [ ] Cập nhật công thức trạng thái trong bài (mục 3.4) theo mạch mới
- [ ] Thêm Remark về tính không suy biến của mạch vào mục 3.4
- [ ] Sửa mô tả "trọng số cố định" -> "huấn luyện được" (mục 3.4, 4.3, Bảng 1)
- [ ] Quyết có chạy mở rộng tính vững không (beta, n_qubits, qrd_batch)

## NỢ VIẾT
- [ ] Ghi rõ trong phần Giới hạn: kết quả cũ đã bị vô hiệu, lý do
