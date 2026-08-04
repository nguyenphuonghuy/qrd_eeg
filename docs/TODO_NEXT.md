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

# CẬP NHẬT 2026-08-02 (rà soát logic/bố cục body.tex mới)

## NỢ TRÍCH DẪN (gỡ khỏi comment trong body.tex, cần bổ sung khi có thời gian)
- [ ] Mục "BCI trong điều khiển thiết bị hỗ trợ" (gần \cite{an2024development}):
      5-8 tài liệu về ngoại cốt chi dưới, chi giả, BCI phục hồi chức năng sau
      đột quỵ. Ưu tiên IEEE TNSRE, J Neural Eng, J NeuroEngineering and
      Rehabilitation, 2021-2026.
- [ ] Mục~\ref{sec:rangbuoc} (Ràng buộc thời gian thực): mục tiêu 10-12 trích
      dẫn, còn thiếu so với mục tiêu ban đầu. Nội dung cần thêm: ITR/Wolpaw,
      ngân sách trễ vòng kín, triển khai MCU/edge, kappa trong an toàn vận
      hành. Có thể dùng thêm \cite{wang2020accurate}.
- [ ] Mục "Bộ giải mã học sâu cho tưởng tượng vận động": mục tiêu 12-15 trích
      dẫn, còn thiếu. Nội dung cần thêm: kiến trúc gọn (EEGNet/EEG-TCNet/
      MI-BMInet), kiến trúc dung lượng lớn (ConvNet sâu/transformer/ensemble),
      tổng quát hóa xuyên đối tượng.

# CẬP NHẬT 2026-08-03 (rà soát phản biện IJRCS trên paper/body.tex)

## ĐÃ XONG (sửa theo phản biện, đã verify qua code/log + biên dịch tectonic 2 lần sạch)
- [x] Vấn đề 1: tiêu đề "An Equivalence Result" -> "A Controlled Comparison under
      Real-Time Control Constraints"; sửa tóm tắt + Kết luận, bỏ overclaim
      "chặn tương đương thu được" (CI vượt biên ±0,5pp nên không xác lập được tương đương).
- [x] Vấn đề 2: phân biệt rõ đơn vị GỘP (đối tượng, 515, không độc lập) với đơn vị
      SUY LUẬN (hạt giống, n=5, df=4) ở Mục 4.1 + chú thích Bảng 2/3/5.
- [x] Vấn đề 3: bỏ lập luận "đối chứng dương chứng minh đủ độ nhạy" (Mục 4.4.1 cũ +
      Kết luận), thay bằng MDE thật tính từ dữ liệu (0,86-1,33pp tùy cặp so sánh,
      lớn hơn phần lớn hiệu ứng 0,12-0,51pp đang báo "không ý nghĩa").
- [x] Vấn đề 4: sửa mô tả V1 ("không tham số học được" -> SAI, θ vẫn huấn luyện,
      code xác nhận patch_v1.py không đụng q_weights) và V2 (W_T không phải "học được",
      code xác nhận teacher_proj.requires_grad=False qua check_circuit.log); thêm
      Bảng 1 mới (tab:bienthe_cauhinh) tổng hợp W_T/W_S/θ/tập cặp/tham số cho 5 biến thể.
- [x] Vấn đề 5: sửa lỗi số T=1,875s@160Hz -> ĐÚNG 3,0s@100Hz (bug thật, không chỉ
      thiếu tài liệu, verify qua preprocess_dataset.py: sfreq=100, t_dur=3.0) ở Bảng 4
      (ITR), Bảng 6 (độ trễ), văn Mục 4.4.3; thêm tiểu mục mới "4.2 Tiền xử lý dữ liệu
      và xây dựng fold" trả lời đủ 17 mục reviewer (6 subject loại: 88,90,92,100,104,106;
      bandpass 4-38Hz FIR không notch; CAR; fold tất định GIỐNG NHAU qua mọi seed; teacher
      train riêng từng fold, 120ep, n_subsets=7).

## ĐANG CHỜ — Vấn đề 5 follow-up: V1 (qrd_dense_noproj) vẫn dùng số liệu vô hiệu
Bảng 3/4 hiện dùng 81,34±0,52 cho V1, lấy từ `results/seeds_v1_per_subject.csv`
— dữ liệu chạy TRƯỚC khi sửa mạch lượng tử (xác nhận qua mtime + nội dung
`docs/PREREG_2026_07_30.md` liệt kê file này là "số liệu vô hiệu"). V1 là biến
thể DUY NHẤT trong 7 biến thể lượng tử chưa có bản chạy lại 5-seed sau khi sửa
mạch (6 biến thể còn lại đã có, xem `results/qrd_seeds_rerun_2026_07_30/`).

- [ ] **JOB 11718** (`jobs/qrd_v1_seeds_rerun.pbs`): `qrd_dense_noproj` × 5 seed
      (1-5) × 5 fold, PhysionetMI, mạch đã sửa. Xếp hàng `Q` sau 11713 (Cho2017,
      walltime trần 96h, đã chạy lâu — có thể chờ rất lâu). Out:
      `results/qrd_v1_rerun_2026_08_03/seeds_v1_rerun_per_subject.csv` (đích 515
      dòng = 5 seed × 103 subject).
- [ ] SAU KHI xong: tính lại mean±std (n=5, cách tính giống các biến thể khác —
      xem cách tính trong lịch sử phiên 2026-08-03, hoặc dò lại bằng
      per-seed-subject-mean rồi std(ddof=1) qua 5 seed), thay số 81,34±0,52 ở
      Bảng~tab:bienthe VÀ cột "5 hạt giống" của Bảng~tab:daohang (V1 Dense hiện
      81.34, hạng 9); tính lại $p$ so với KDBase (paired t-test, n=5, df=4, giống
      cách đã làm cho các biến thể khác trong phiên này). KHÔNG đổi cột "một hạt
      giống" của Bảng~tab:daohang (81.06, đã lấy đúng từ nguồn hợp lệ post-fix
      `results/qrd_rerun_2026_07_30/`, xem phần dò nguồn seed 20200220 ở dưới).

## ĐANG CHỜ — Vấn đề 6 (QUAN TRỌNG NHẤT, có thể đổi kết luận trung tâm của bài)
Đã verify SẠCH qua code (`scripts/train_all.py`, `run_seeds.py`):
loss KDBase đúng = 0,5·CE+0,5·KD; checkpoint chọn theo val, không rò rỉ test;
teacher fold i khớp đúng student fold i (cùng fold_idx, cùng thuật toán chia fold
tất định). Không có leakage.

PHÁT HIỆN MỚI (chưa viết vào bài, đang chờ ablation xác nhận): `alpha=0,5` áp
dụng ĐỒNG NHẤT cho mọi method kể cả `no_kd` (dict `HP` trong run_seeds.py/run_all.py,
không override theo method). Với no_kd, `kd=None` nên loss thực tế = 0,5×CE (không
phải 1,0×CE chuẩn) -> nghi ngờ baseline bị huấn luyện dưới mức, có thể phóng đại
khoảng cách 18,43pp KD. Bằng chứng gián tiếp: no_kd cực kỳ bất ổn theo seed
(SD giữa 5 seed-mean ≈5,0pp, có seed tụt xuống 58%) trong khi kd_base rất ổn định
(SD≈0,59pp) — xem bảng seed×fold đã tính trong phiên 2026-08-03.

- [ ] **JOB ABLATION 11719** (`jobs/no_kd_alpha1_seeds.pbs`): no_kd với
      `QRD_ALPHA=1.0`, 5 seed × 5 fold, PhysionetMI. Xếp hàng `Q` sau 11713
      (Cho2017, đã chạy 41h/96h trần — có thể chờ rất lâu) và 11718 (V1 seed rerun).
      Out: `results/no_kd_alpha1_2026_08_03/no_kd_alpha1_per_subject.csv`.
      Đã thêm `QRD_ALPHA` env override vào `scripts/run_seeds.py`
      (backup: `run_seeds.py.bak_before_alpha`).
      TIÊU CHÍ: so acc no_kd(alpha=1.0) vs no_kd(alpha=0.5, hiện 63,06%) vs
      kd_base(81,49%). Nếu alpha=1.0 kéo no_kd lên gần kd_base -> khoảng cách
      18,43pp phần lớn là artifact, PHẢI viết lại Bảng 2 + Mục 4.4.1 + Kết luận
      (toàn bộ phần "hiệu ứng KD lớn"). Nếu alpha=1.0 không đổi nhiều -> hiệu ứng
      KD là thật, chỉ cần ghi chú đã kiểm tra.

## NỢ VIẾT (chờ job 11719 xong rồi viết GỘP một lần, không viết rải rác/trước khi có số)
- [x] Viết kết quả ablation alpha=1.0 + kết luận (hiệu ứng KD thật, 6,56pp
      không phải 18,43pp bị phóng đại) vào Mục~\ref{sec:ketqua}/Kết luận —
      xong 2026-08-04, xem chi tiết ở mục "11719" trong checklist đóng phía
      dưới.
- [ ] Bảng accuracy theo seed × fold (no_kd, kd_base) -> vẫn có thể cân nhắc
      thêm vào phụ lục, chưa làm (không bắt buộc).

## Vấn đề 7 — so sánh cosine/RBF vs quantum bị nhiễu (144 chiều thô, 0 tham số học
được, không dùng W_T/W_S) — đã xác nhận qua code (`train_all.py` cũ:
`_cosine_kernel`/`_rbf_kernel` gọi thẳng `_prepare_feats`, không qua `student_proj`).
QUYẾT ĐỊNH: người dùng đồng ý TẠM BỎ QUA cam kết PREREG_2026_07_30.md (không đổi
cách so sánh sau khi biết kết quả) cho riêng vấn đề này, để chạy 1 so sánh MỚI
kiểm soát đúng số chiều + số tham số.

- [x] Sửa `scripts/train_all.py` (backup: `train_all.py.bak_kernelfair`):
      thêm `proj_input` vào `RelationalDistillLoss.__init__`; khi `True`, cosine/RBF
      dùng `student_proj`/`teacher_proj` (W_S học được 580 tham số, W_T đóng băng)
      giống hệt nhánh quantum, thay vì đặc trưng 144 chiều thô. Thêm 2 method mới
      vào `METHOD_TABLE`: `ck_cosine_tg_proj`, `ck_rbf_tg_proj` (giữ nguyên
      `ck_cosine_tg`/`ck_rbf_tg` cũ để đối chiếu, không xóa).
      ⚠️ Còn 1 khác biệt KHÔNG đóng được: quantum có thêm 24 tham số θ (mạch),
      cosine/RBF không có thành phần tương đương (bandwidth RBF vẫn median
      heuristic không học) — cần ghi rõ trong bài khi viết, không claim đã kiểm
      soát 100%.
- [ ] **JOB 11720** (`jobs/kernel_fair_seeds.pbs`): bước 1 tự kiểm tra
      `RelationalDistillLoss(proj_input=True)` (W_S=580 học được, W_T=0, có grad)
      trước khi chạy thật; bước 2 chạy `ck_cosine_tg_proj` + `ck_rbf_tg_proj` × 5
      seed × 5 fold, PhysionetMI. Out:
      `results/kernel_fair_2026_08_03/kernel_fair_per_subject.csv` (đích 1030 dòng).
      Xếp hàng `Q` sau 11713/11718/11719 (11713 đã chạy 41h/96h trần, hàng đợi có
      thể rất dài).
      TIÊU CHÍ: so acc `ck_cosine_tg_proj`/`ck_rbf_tg_proj` (4 chiều, có W_S) với
      `ck_cosine_tg`/`ck_rbf_tg` cũ (144 chiều, 0 tham số) và với V5 quantum
      (81,12%). Nếu số đổi nhiều -> kết luận "3 kernel không phân biệt được" ở
      Mục 4.4.2/Kết luận cần viết lại có điều kiện (chỉ đúng khi kernel cổ điển
      dùng đặc trưng thô); nếu không đổi nhiều -> củng cố thêm kết luận cũ, thêm
      như một robustness check.
- [ ] NỢ VIẾT (sau khi có số, viết gộp cùng lúc với Vấn đề 6):
      thêm công thức cosine/RBF, bandwidth (median heuristic, tính lại mỗi batch),
      bảng xác nhận không gian đầu vào + số tham số cho cả 2 phiên bản (thô và proj)
      vào cuối Mục 3.5 hoặc Mục 4.4.2; nêu rõ residual gap (θ 24 tham số của quantum
      không có tương đương ở kernel cổ điển) như một giới hạn còn lại.

## Vấn đề 12 — Hình 3 (t-SNE) không có script tạo, không kiểm chứng được
Đã kiểm tra toàn bộ project (kể cả 2 file zip) — KHÔNG có script/notebook nào tạo
`figs/image3.png` gốc. Không biết split/subject/seed/perplexity đã dùng. Hình gốc
chỉ có 2 panel (FeatureKD, Informative QRD=V5), khác thang trục (2 lần t-SNE riêng),
và Informative QRD trông tách gần hoàn hảo dù acc chỉ 81,12% — đáng ngờ (có thể lấy
từ train thay vì test). QUYẾT ĐỊNH: làm Phương án B (vẽ lại từ đầu, không chỉ thêm
caveat).

- [x] Sửa `scripts/train_all.py` (backup: `train_all.py.bak_tsnefeat`): thêm
      `return_feats=True` cho `evaluate_full()`, thêm `save_test_feats=True` cho
      `train_method()` — trích đặc trưng 144 chiều THẬT trên tập TEST tại epoch có
      val tốt nhất (không chỉ acc như trước).
- [x] Viết `scripts/extract_tsne_feats.py`: train 4 method (no_kd, kd_base,
      feature_kd, qrd_teacher_guided) đúng 1 lần, fold=0, seed=1, 30 epoch, lưu
      `tsne_feats_{tag}.npz` (feats, labels, subjects, acc, fold, seed).
- [ ] **JOB 11721** (`jobs/tsne_feats.pbs`): xếp hàng `Q` sau 11713/11718/11719/11720.
      Ước ~10 phút thực chạy (3 method cổ điển ~1 phút/method + 1 method quantum
      ~7 phút) sau khi tới lượt. Out: `results/tsne_feats_2026_08_03/tsne_feats_*.npz`.
- [x] Viết sẵn `scripts/plot_tsne.py`: vẽ lại Hình 3 đủ 4 panel, CÙNG sieu tham số
      t-SNE (perplexity=30, random_state=42) và CÙNG thang trục cho cả 4 panel (khác
      hình gốc — mỗi panel trước có thang riêng). Tính thêm **silhouette score trên
      không gian gốc 144 chiều** (không bị t-SNE bóp méo) cho từng panel. Ghi
      `tsne_meta.json` đầy đủ metadata (fold, seed, n_test, n_subject, perplexity,
      random_state, acc, silhouette) để chèn vào chú thích Hình 3 — giải quyết đúng
      yêu cầu "nêu đầy đủ seed/fold/đối tượng/số mẫu/siêu tham số" của reviewer.
      CHẠY ĐƯỢC TRÊN LOGIN NODE (chỉ numpy/sklearn/matplotlib trên mảng nhỏ đã lưu,
      không phải import nặng) — không cần qsub, chạy ngay sau khi job 11721 xong.
- [ ] SAU KHI job 11721 xong: chạy `plot_tsne.py`, kiểm tra hình mới (đặc biệt xem
      accuracy hiển thị trên mỗi panel có khớp % điểm lẫn lộn trực quan không — nếu
      vẫn quá "sạch" so với acc, cần xem lại chứ không chỉnh sửa để đẹp), rồi sửa lại
      chú thích + văn Mục 4.4.5 trong `body.tex` cho khớp hình mới (bỏ claim so với
      student độc lập cũ, thêm silhouette score, thêm đầy đủ metadata, xác nhận
      dùng đúng tập TEST).

## CẬP NHẬT 2026-08-03 (tiếp) — 20 "vấn đề nhỏ" + rà soát toàn bài từ đầu đến cuối

### ĐÃ XONG
- [x] Rà 20 mục nhỏ do reviewer nêu (câu chữ/thuật ngữ/số liệu lặt vặt). Kết quả:
  - **13 mục ĐÚNG, đã sửa**: "bốn"->"năm chiến lược" (Kết luận); tóm tắt "không
    phân biệt được"->"không phát hiện được khác biệt có ý nghĩa"; bỏ câu lặp ý
    cuối Mục "Bộ giải mã học sâu"; Mục 3.4 "bảo đảm tránh"->"giới hạn miền góc"
    (nêu rõ tính đơn ánh chưa chứng minh chặt với nhiều qubit); thêm nguồn/giải
    thích ngưỡng suy biến 0,05; V1/V2 làm rõ đường chéo (i,i) luôn=1 không mang
    tin; V3 xác nhận `shuffle=True` qua code; V4 làm rõ set không đếm trùng +
    tie-break của `torch.topk`; V5 nêu rõ chọn mẫu là heuristic rời rạc
    (`no_grad`); Bảng 3 chú thích rõ p=0,541 là so sánh trực tiếp V1-V2 (khác
    cột p trong bảng vốn so với KDBase) — **phát hiện thêm khi sửa mục này**:
    câu "hai phép chiếu học được, 1.160 tham số" ở Mục 4.4.2 SAI, mâu thuẫn với
    Bảng 1 (chỉ $W_S$ học được, 580 tham số) — đã sửa; Bảng 5 thêm "GPU NVIDIA
    H100"; Bảng 7 thêm ghi chú CPU/thread/version không có trong log (honest
    gap, không bịa); tên dataset thống nhất "PhysionetMI" (bỏ "PhysioNet
    EEGMMIDB" lẻ ở Bảng 1).
  - **3 mục SAI/lỗi thời (phần mềm đọc file cũ), bỏ qua**: "chặn tương đương"
    trong tóm tắt (đã sửa từ trước, Vấn đề 8); Bảng 1 "Trọng số mạch" đã đủ
    hàng; teacher/student đã nhất quán 77 lần, không hề dùng "mô hình giáo
    viên/học sinh".
  - **Bảng 4 "một hạt giống" dò ra nguồn seed=20200220** (KHÔNG phải random —
    verify khớp chính xác 12/12 method): 5 method cổ điển từ
    `results/results_all_per_subject.csv` (chạy gốc 21/7), 7 biến thể lượng tử
    từ `results/qrd_rerun_2026_07_30/results_qrd_rerun_per_subject.csv` (chạy
    lại sau sửa mạch, vì bản gốc bị vô hiệu). Đã thêm đầy đủ vào chú thích Bảng.
- [x] Rà soát body.tex+main.tex từ đầu đến cuối (1803 dòng), đối chiếu chéo toàn
      bộ số liệu Bảng 2-7 với văn bản thảo luận, đếm lại các danh sách liệt kê
      (4 đóng góp, 4 nghiên cứu gần nhất, 12 cấu hình = 5 cổ điển+7 lượng tử).
      Tìm thêm 2 chỗ phi logic, đã sửa: Kết luận vẫn dùng "không phân biệt được
      về mặt thống kê" (sót lại, quên đồng bộ với tóm tắt); câu chuyển ý "Trên
      nền đối chứng đó" vênh giọng với đoạn ngay trước (đã hạ mức tin cậy đối
      chứng dương ở Vấn đề 3) -> bỏ chữ "đối chứng".
      CHƯA ĐỘNG: tóm tắt (main.tex dòng 71) "một đối chứng dương phát hiện được
      hiệu ứng 1,44 điểm" — không sai, chỉ thiếu nuance "gần biên" so với bản
      đầy đủ; để nguyên vì tóm tắt vốn cô đọng, có thể sửa nếu muốn thống nhất
      tuyệt đối.

### CHƯA LÀM — cần quyết định riêng, không phải việc sửa text
- [ ] **Hình 1** (`figs/image1.png`, khung tổng thể): xác nhận đúng phản ánh
      reviewer — dày đặc, chữ nhỏ, toàn tiếng Anh. **Phát hiện thêm (không phải
      ý reviewer)**: hộp chú giải cuối hình dùng "V1: KDBase, V2: FeatureKD, V3:
      RelationalKD, V4: QRD(V1-V4), V5: QRD(informative)" — **xung đột hoàn
      toàn** với ký hiệu V1-V5 dùng trong Mục 3.5 và Hình 2 (5 biến thể quan hệ:
      Dense tất định/học được/Anchor/Anchor+kNN/Guided). Cần đổi tên nhóm trong
      Hình 1 (vd A/B/C/D/E) để tránh trùng ký hiệu.
- [ ] **Hình 2** (`figs/image2.png`, 5 biến thể): tiếng Anh trong khi bài tiếng
      Việt (đúng ý reviewer). Có bug ĐÃ TỰ GHI CHÚ SẴN trong comment LaTeX của
      body.tex (dòng ~903-907, `% GHI CHU BIEN TAP`) từ trước, xác nhận qua ảnh
      thật: ô "Relation index set" của V3/V4 ghi `(i,a)` nhưng công thức thật
      (eq:i-v3/i-v4) là `(a,a')`; trục ghi "N" nên là "q"; chú thích
      "(Frobenius norm)" sai vì công thức \eqref{eq:qrd} là MSE.
      -> Cả hai hình cần vẽ lại bằng công cụ ngoài (không sửa được bằng text);
      cần bạn quyết ưu tiên/công cụ trước khi làm.

### TRẠNG THÁI TỔNG QUAN (để đọc nhanh sau khi context bị nén)
Đang review `paper/body.tex`+`main.tex` theo bản phản biện IJRCS 12 "Vấn đề
lớn" + 20 "vấn đề nhỏ". Đã sửa xong toàn bộ phần TEXT (Vấn đề 1-5, 8-11, 20
mục nhỏ, rà soát cuối). Còn lại:
1. **4 job đang xếp hàng chờ gpu_slot** (11713 Cho2017 đang chạy, chiếm slot,
   walltime trần 96h, có thể còn lâu): 11718 (V1 rerun, Vấn đề 5), 11719
   (no_kd alpha=1.0, Vấn đề 6), 11720 (kernel_fair, Vấn đề 7), 11721 (tsne_feats,
   Vấn đề 12). KHÔNG cần tự ngồi chờ — khi quay lại phiên mới, `qstat -u
   gv_nphuy` để xem tiến độ.
2. Mỗi job xong -> việc VIẾT tương ứng (chi tiết ở mục riêng từng Vấn đề phía
   trên) — viết SAU KHI có số, không đoán trước.
3. Hình 1 và Hình 2 cần vẽ lại (không phải việc text) — chờ quyết định riêng.
Công cụ biên dịch thử: `/gpfs0/users/gv_nphuy/tools/bin/tectonic -X compile
main.tex --outdir <dir> --keep-logs` (đã cài sẵn, không cần cài lại).

## CẬP NHẬT 2026-08-03 (tiếp 2) — rà soát nhận xét về Tài liệu tham khảo

Đối chiếu 86 mục [1]-[86] trong `paper/references.bib` bằng cách biên dịch
thật (tectonic sinh `main.bbl` để lấy đúng thứ tự số hiệu — KHÔNG đoán qua
thứ tự `\cite` trong body.tex vì có thể lệch). Xác nhận số mục = 86, khớp
đúng con số reviewer nêu.

### ĐÃ SỬA (đối chiếu Crossref API + trang arXiv, không đoán)
- Tiêu đề mục cuối "Tài liệu" (do polyglossia vietnamese chỉ định nghĩa vậy)
  -> `\renewcommand{\refname}{Tài liệu tham khảo}` đặt ngay trước
  `\bibliographystyle` trong main.tex (đặt trong preamble bằng `\AddToHook`
  KHÔNG ăn — đã thử, polyglossia ghi đè sau; phải đặt trong body trước khi
  gọi `\bibliography`).
- [37] gou2025neighborhood, [40] mai2025eegskdnet, [43] chen2026exploring,
  [71] behera2026qsvmqnn, [80] nishan2026quantummedkd: bổ sung volume/số/trang
  thật lấy từ Crossref API (`curl api.crossref.org/works/<doi>`) — các DOI này
  đã có sẵn trong .bib nhưng lúc lấy về (tháng 7) bài còn ở dạng early access
  nên thiếu vol/trang; nay Crossref đã có đủ.
- [40] mai2025eegskdnet: tên tạp chí "IEEE access : practical innovations,
  open solutions" (chuỗi Crossref thô) -> đổi thành "IEEE Access".
- [33] hinton2015distilling, [45] liu2025quantum, [81] li2025quantum: đã có
  `doi` (dạng `10.48550/arXiv.XXXX`) trong .bib nhưng IEEEtran.bst KHÔNG in
  trường `doi` ra bbl (xác nhận bằng test biên dịch) -> thêm trường
  `note = {arXiv:XXXX.XXXXX}` (IEEEtran.bst CÓ in `note`) để số arXiv hiện
  ra trong danh mục.
- [73] park2026qdiver, [77] yan2026distilling: .bib gốc không có doi/arXiv id
  nào cả -> tìm thật qua WebSearch, xác nhận đúng bài (tiêu đề + tác giả khớp
  100%) trên arXiv: 2603.28122 và 2603.21586 -> thêm `doi`+`note` như trên.
- [38] huang2024enhancing, [39] wu2026multilevel, [42] chen2024qeegnet,
  [46] liu2025quantumtrain (4 tài liệu liên quan trực tiếp đóng góp, theo yêu
  cầu riêng của reviewer): đã có đủ vol/số/trang, chỉ thêm `note` in DOI ra
  ngoài vì lý do tương tự (bst không tự in `doi`).
- [72] dutta2026duoqepinet:
  - Tên tác giả "S, Sridevi" / "P, Anandan" / "B, Indira" bị BibTeX tách
    given/family sai khiến in ra "S. S", "A. P", "I. B" — ĐÃ ĐỐI CHIẾU
    Crossref, xác nhận Crossref cũng ghi family=chỉ 1 chữ như vậy (quy ước
    tên Nam Ấn Độ, không phải lỗi nhập liệu) -> KHÔNG bịa họ, chỉ bọc ngoặc
    nhọn `{Sridevi S.}`/`{Anandan P.}`/`{Indira B.}` để BibTeX in nguyên cụm,
    tránh rút gọn gây hiểu lầm là lỗi OCR.
  - Ngày "Dec. 2026" (tương lai so với hiện tại 2026-08-03): Crossref xác
    nhận `published-online = 2026-03-31` (đã xuất bản thật, trước ngày hiện
    tại), còn `published-print = 2026-12` chỉ là ngày gộp số in ấn (tạp chí
    EPJ Quantum Technology xuất bản liên tục). Đã đổi `month` trong .bib từ
    `dec` sang `mar` (ngày online-first, đúng ngày trích dẫn được) và thêm
    `note` ghi rõ cả hai mốc để không ai hiểu nhầm là bài chưa công bố.
- Đã biên dịch lại 2 lần bằng tectonic, không phát sinh lỗi/"undefined",
  `main.pdf`+`main.log` trong `paper/` đã được ghi đè bằng bản mới.

### CHƯA LÀM — cần quyết định của người dùng, không phải lỗi để tự sửa
- [29] zoumpourlis2024motor (teacher Ensemble-MI): reviewer đúng là Mục
  `sec:kientruc` mô tả kiến trúc teacher còn phụ thuộc citation, chưa đủ chi
  tiết tái lập độc lập (số nhánh cụ thể, kernel size, công thức loss
  collaborative learning, optimizer/lr lúc huấn luyện teacher...). Đây là mở
  rộng NỘI DUNG kỹ thuật (có thể dài), không phải sửa lỗi bib -> cần hỏi
  người dùng có muốn thêm phụ lục/đoạn mô tả kiến trúc chi tiết hơn không,
  và thêm tới mức nào cho vừa khuôn khổ bài báo Tạp chí điều khiển.
- 86 tài liệu "khá dài so với quy mô bài báo Tạp chí" — nhận xét hợp lý
  nhưng việc CẮT tài liệu nào (đặc biệt các công trình lượng tử ngoài EEG)
  là quyết định về phạm vi tổng quan tài liệu, ảnh hưởng nội dung Mục giới
  thiệu/liên quan -> chưa tự ý xoá, cần người dùng chỉ định cụ thể muốn bỏ
  nhóm nào.
- Reviewer yêu cầu "kiểm tra lại TOÀN BỘ metadata" — mới đối chiếu Crossref/
  arXiv cho đúng các mục reviewer nêu tên cụ thể (13 mục) chứ chưa quét hết
  86 mục; nếu muốn rà toàn bộ cần thêm một lượt kiểm tra nữa.

## CẬP NHẬT 2026-08-04 — rà văn phong (câu dài/AI-style) + Vấn đề lớn 1 (review IJRCS)

### ĐÃ XONG (văn bản, không cần chờ gì)
- Rà toàn bộ `body.tex`+`main.tex` tìm câu quá dài, cụm đệm kiểu AI ("Cần lưu
  ý rằng"/"Cần nhấn mạnh rằng"/"Tổng hợp lại"/"Đáng chú ý"/"Nói cách khác"),
  lặp cấu trúc "Thứ nhất/thứ hai" giữa Giới thiệu và Mục 2.3, và dấu `:` dẫn
  nguyên một mệnh đề chủ-vị (calque văn phong tiếng Anh, ví dụ "X: Y là câu
  hoàn chỉnh") — đã sửa toàn bộ (~19 chỗ dấu `:` + nhiều câu dài tách đôi).
  Đã biên dịch lại nhiều lần, `main.pdf` cập nhật, không lỗi/undefined.
- **Vấn đề lớn 1 (review IJRCS)**: xác minh qua cả văn bản lẫn code
  (`scripts/train_all.py`, class `RelationalDistillLoss`) rằng reviewer ĐÚNG:
  θ (mạch vướng víu lượng tử) dùng CHUNG cho cả nhánh teacher và student,
  KHẢ HUẤN, và không có `detach`/`no_grad` nào chặn gradient ở nhánh teacher
  trong `forward()` (dòng `Kt = self._kernel(t_feats, "teacher")`) — trong
  khi chính code đã có sẵn comment cảnh báo đúng rủi ro này cho $W_T$ cổ điển
  ("mục tiêu quan hệ teacher PHẢI CỐ ĐỊNH... nếu teacher_proj khả huấn thì
  L_QRD có nghiệm tầm thường") nhưng KHÔNG áp dụng phòng ngừa tương tự cho θ.
  Đã sửa Mục 3.1 (giới hạn phạm vi câu "student là thành phần duy nhất được
  cập nhật tham số"), Mục 3.4/`sec:qrd` (thêm ~180 từ giải thích chính xác +
  rủi ro co-adaptation + lý do có thể của thiết kế dùng chung, gắn nhãn rõ là
  đánh đổi chưa kiểm chứng), và Kết luận (thêm vào đoạn giới hạn).

### ĐANG CHỜ — Job 11727 (đối chứng theta_mode, Vấn đề lớn 1)
- **Job 11727** (`theta_mode_ablation`, xếp `Q` sau 11713/11718/11719/11720/
  11721), walltime 16h, log `logs/theta_mode_ablation.log`.
- Code: đã thêm tham số `theta_mode` vào `RelationalDistillLoss`
  (`scripts/train_all.py`, backup gốc `train_all.py.bak_before_thetamode`):
  `shared` (mặc định cũ, θ chung khả huấn) / `shared_fixed` (θ chung, đóng
  băng) / `split` (θ_T đóng băng riêng, θ_S khả huấn, khởi tạo giống θ_T lúc
  t=0). Thêm 2 method vào `METHOD_TABLE`: `qrd_dense_theta_fixed`,
  `qrd_dense_theta_split` (giữ nguyên `sel="dense"`, chỉ đổi theta_mode).
- Bước 1 trong job: sanity-check cơ chế theta_mode (không cần dataset) —
  xác nhận đúng θ nào đổi/không đổi sau 1 bước optimizer, `requires_grad`
  đúng kỳ vọng cho cả 3 mode. Dừng job (exit 3) nếu FAIL.
- Bước 2: chạy `qrd_dense_theta_fixed` + `qrd_dense_theta_split`, mỗi cái
  5 seed × 5 fold, PhysionetMI → `results/theta_mode_ablation_2026_08_04/
  theta_mode_ablation_per_subject.csv` (dự kiến 1030 dòng = 2×515).
  **Nhánh `shared` KHÔNG chạy lại** — tái dùng `qrd_dense_s1..s5` đã có sẵn
  trong `results/qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv`
  (chính là số liệu V2 Dense 81,49±0,78 đang dùng trong Bảng `tab:bienthe`).
- **SAU KHI xong**: tổng hợp 3 cột (shared/fixed/split) mean±std trên 5 seed,
  paired t-test giữa các cặp (n=5, df=4). Nếu `shared` và `split` không khác
  biệt có ý nghĩa → rủi ro co-adaptation nêu ở Mục 3.4 có thể hạ mức nghiêm
  trọng (nhưng vẫn giữ nguyên đoạn giải thích cơ chế, chỉ thêm số liệu thực
  nghiệm). Nếu khác biệt rõ → cần viết thêm phát hiện này vào Kết quả +
  Kết luận, có thể phải xem lại lựa chọn dùng chung θ trong thiết kế chính.
  Viết SAU KHI có số, không đoán trước.

---
## CẬP NHẬT 2026-08-04 (tiếp) — Vấn đề lớn 2 + 3 (review IJRCS), phát hiện hàng đợi HPC

### ĐÃ XONG — Vấn đề lớn 2 (khởi tạo $W_T$ chưa biện minh đủ)
- Xác minh qua code: trước khi sửa, TOÀN BỘ mô tả $W_T$ trong bài chỉ có một
  câu "được khởi tạo và giữ cố định" — không nói cơ chế khởi tạo, không nói
  có đổi theo seed hay không, không có phân tích độ nhạy, không có cơ sở lý
  thuyết cho phép chiếu ngẫu nhiên 144→4. Reviewer ĐÚNG.
- Đã sửa Mục 3.4/`sec:qrd` (thêm đoạn giải thích $W_T$/$W_S$ dùng
  `nn.Linear` mặc định của PyTorch, không chuẩn hóa, phụ thuộc gián tiếp
  luồng RNG toàn cục nên nhiều khả năng khác nhau giữa 5 hạt giống nhưng
  chưa đo trực tiếp, và không viện dẫn Johnson–Lindenstrauss hay cơ sở lý
  thuyết nào khác) và Kết luận (thêm câu vào đoạn giới hạn).
- Code: thêm tham số `teacher_proj_seed=None` vào `RelationalDistillLoss`
  (`scripts/train_all.py`, backup `train_all.py.bak_before_wtsens`) — khi
  đặt một số nguyên, $W_T$ được khởi tạo lại từ một `torch.Generator` RIÊNG
  với đúng công thức mặc định của `nn.Linear` (Kaiming-uniform), độc lập
  với seed huấn luyện. Mặc định `None` giữ nguyên hành vi cũ (không đổi kết
  quả các method hiện có). Thêm 5 method vào `METHOD_TABLE`:
  `qrd_dense_wt1`..`qrd_dense_wt5` (giống hệt `qrd_dense`, chỉ khác
  `teacher_proj_seed` = 90001..90005).
- **CHƯA kiểm chứng bằng thực nghiệm** (job `cpu_queue_probe.pbs` định làm
  việc này đã bị xóa trước khi chạy do dọn dẹp thử nghiệm hàng đợi — xem
  bên dưới). Chỉ mới `py_compile` sạch, chưa chạy runtime thật.
- **CHƯA có job đo độ nhạy $W_T$** (`jobs/wt_sensitivity.pbs` chưa tạo).
  Kế hoạch đã thảo luận: chạy `qrd_dense_wt1..5` ở MỘT seed huấn luyện cố
  định (không quét 5 seed huấn luyện) × 5 fold (25 fold-run), so phương sai
  do riêng $W_T$ với phương sai do seed huấn luyện đã có (0,734 điểm %,
  Bảng T3). Cần làm cùng lúc: bước sanity-check `teacher_proj_seed` (tái
  lập được theo seed, 5 giá trị seed cho 5 $W_T$ khác nhau từng đôi một,
  `requires_grad=False`) như một bước trong job, mô phỏng cách job 11727 đã
  làm với `theta_mode`.

### ĐÃ XONG — Vấn đề lớn 3 (β=0,02 chưa chứng minh công bằng giữa 3 kernel)
- Xác minh qua code: `beta_qrd=0,02` dùng CHUNG cho cả 3 kernel (quantum,
  cosine, RBF) tại `train_all.py` (dòng gọi `loss = loss + beta_qrd *
  rel_loss(...)`), lý do duy nhất trong bài là "cả 3 bị chặn trong [0,1]"
  — đúng nhưng không đảm bảo cùng độ lớn gradient/loss hiệu lực. Phân tích
  độ nhạy β hiện có (Bảng `tab:daohang`, β∈{0,01;0,02;0,05}) CHỈ áp dụng
  cho quantum (`qrd_teacher_guided`), đúng như `docs/DESIGN.md` dòng 100
  quy định phạm vi Nhóm B ban đầu — không phải bỏ sót ngẫu nhiên mà là giới
  hạn thiết kế có chủ đích, giờ cần nêu rõ. Reviewer ĐÚNG.
- Người dùng chọn phương án khắc phục: **sửa văn bản + đo diagnostic nhẹ**
  (không mở rộng ma trận β-sensitivity sang cosine/RBF, không đổi công thức
  chuẩn hóa loss — hai phương án đó bị từ chối vì tốn compute/rủi ro cao
  hơn nhiều).
- Đã sửa Mục 3.4/`sec:qrd` (thêm đoạn phân tích: cùng khoảng [0,1] không
  đảm bảo cùng gradient scale, RBF tự chuẩn theo median mỗi batch còn
  quantum fidelity có xu hướng tập trung gần biên do hình học Hilbert),
  Mục 4.4/`sec:cauhinh` (thêm câu trỏ chéo), và Kết luận (thêm câu vào đoạn
  giới hạn, cạnh câu về $W_T$).
- Code: thêm `raw_loss` (giá trị $\mathcal{L}_{\mathrm{QRD}}$ TRƯỚC khi nhân
  β) vào `last_diag` trong `RelationalDistillLoss.forward()` — LUÔN tính,
  kernel-agnostic, không tốn thêm chi phí (backup `train_all.py.bak_before_
  betadiag`). Thêm cơ chế `grad_norm_student` — opt-in qua biến môi trường
  `QRD_GRAD_DIAG=1`, chỉ chạy ở batch đầu mỗi epoch: backward RIÊNG của
  `beta_qrd * rel_term` lên `student.parameters()` (dùng `retain_graph=True`
  để không phá đồ thị dùng cho backward chính ngay sau đó, `zero_grad`
  trước/sau để tách khỏi gradient CE/KD/feat/rkd). Không đổi công thức loss
  dùng để tối ưu — chỉ đo, không ảnh hưởng kết quả huấn luyện khi
  `QRD_GRAD_DIAG` không đặt.
- **Job 11731** (`beta_fairness_diag`, smoke test tự submit, walltime 30
  phút, log `logs/beta_fairness_diag.log`) — chạy `run_all.py --methods
  qrd_dense,ck_cosine_tg,ck_rbf_tg --folds 0 --epochs 5 --skip_teacher`
  với `QRD_GRAD_DIAG=1`, in ra `rawL=` và `gradNormS=` mỗi epoch cho cả 3
  kernel. Kết quả ghi `results/beta_fairness_diag_2026_08_04/`.
  **SAU KHI xong**: đối chiếu `rawL`/`gradNormS` giữa 3 kernel. Nếu lệch
  nhau nhiều bậc độ lớn → viết rõ vào Mục 4.4/Kết luận rằng β=0,02 tạo mức
  giám sát hiệu lực khác nhau giữa các kernel, cân nhắc có cần chú thích
  thêm hay đề xuất hướng chuẩn hóa cho công trình sau; nếu tương đương →
  ghi nhận như một xác nhận thực nghiệm bổ sung cho lập luận "bị chặn
  [0,1]" hiện có. Đây chỉ là dữ liệu CHẨN ĐOÁN (1 fold, 5 epoch, không phải
  kết quả báo cáo chính) — không dùng để thay thế Bảng kết quả chính.

### PHÁT HIỆN HẠ TẦNG HPC (không liên quan trực tiếp bài báo, nhưng quan
### trọng cho việc lập kế hoạch job)
- `testq` xác nhận qua thực nghiệm KHÔNG có node phục vụ (`Can Never Run`),
  giống hệt `workq` dù tài liệu `hpc_ai/docs/HPC_CONTEXT.md` chỉ cảnh báo
  rõ ràng về `workq`.
- Hàng `sharedgpu` TỰ GÁN `gpu_slots=1` mặc định cho mọi job kể cả khi
  không khai trong `select=` — phải khai tường minh `gpu_slots=0` mới né
  được giới hạn `gpu_slots` per-user (`qmgr -c "list server"`:
  `max_run_res.gpu_slots = [u:PBS_GENERIC=1]`).
- Giới hạn per-user THẬT SỰ đang chặn job mới (kể cả job CPU nhỏ,
  `gpu_slots=0`) là **`max_run_res.mem = [u:PBS_GENERIC=64gb]`** — tổng bộ
  nhớ CỘNG DỒN của mọi job đang CHẠY (không phải đang Q) cho gv_nphuy. Job
  11713 một mình xin đủ `mem=64gb`, chiếm trọn trần → không job nào khác
  (CPU hay GPU, nhỏ hay lớn) chạy được cho tới khi 11713 kết thúc hoặc giải
  phóng bớt bộ nhớ. Không có "đường tắt" nào khác.
  → mọi job mới (11727, 11731, 11732...) đều xếp hàng `Q` bình thường, kể
  cả job rất nhỏ.
  **SỬA LẠI ƯỚC TÍNH**: ước tính ban đầu "~45h nữa" SAI vì chỉ tính từ
  walltime còn lại (96h - đã chạy), KHÔNG xem log tiến độ thực tế. Job
  11713 (`cho_qrd_all6_rerun`) hóa ra KHÔNG liên quan job đơn lẻ mà chính
  là job chạy KIỂM CHỨNG DATASET THỨ HAI (Cho2017) — xem mục Vấn đề lớn 5
  bên dưới — và khi kiểm tra log trực tiếp thì job đang ở method CUỐI
  (`qrd_tg_b0.05`), seed CUỐI (5), gần xong fold cuối → thực tế chỉ còn
  vài chục phút, không phải ~45h. BÀI HỌC: luôn ưu tiên đọc log tiến độ
  thực tế thay vì suy ra ETA thuần từ walltime còn lại.

---
## CẬP NHẬT 2026-08-04 (tiếp) — Vấn đề lớn 4 (review IJRCS): candidate pool V5 vs V1–V4

### ĐÃ XONG — xác minh + sửa văn bản
- Xác minh qua code: V1–V4 (`sel="dense"/"anchor"/"global_local"`) lấy
  `s_feats[:q]` — 16 phần tử ĐẦU của batch 64 theo VỊ TRÍ (không có tiêu
  chí chọn). V5 (`sel="teacher_guided"`) gọi `select_informative_idx` tính
  điểm trên TOÀN BỘ 64 mẫu rồi `torch.topk` thật sự. Reviewer ĐÚNG: V5
  khác V1–V4 không chỉ ở tiêu chí chọn mà còn ở candidate pool.
- Phát hiện thêm: bài TỰ MÂU THUẪN — Mục 3.5 (`sec:bienthe`, dòng ~989-1000,
  1163-1177) đã mô tả khá trung thực sự khác biệt candidate pool, nhưng
  câu tóm tắt sớm hơn ở Mục 3.1 (`sec:tongquan`, dòng 649-653 cũ) khẳng
  định quá mạnh: "chỉ khác ở tập chỉ số đầu vào... mọi khác biệt quan sát
  được đều quy về cách chọn quan hệ" — không đúng cho V5. Đã sửa câu này,
  caption Bảng `tab:bienthe` (dòng ~1440), đoạn diễn giải kết quả V5 (dòng
  ~1486-1491, nơi V5 cho kết quả THẤP NHẤT trong nhóm — nay đã thêm cảnh
  báo confound ngay tại điểm diễn giải này), và Kết luận.
- Biên dịch tectonic sạch, không undefined.

### SỬA HƯỚNG "đối chứng tối thiểu" — QUAN TRỌNG, đọc kỹ trước khi dùng lại ý này
- Phương án đầu tiên tôi đề xuất ("guided_pool16": áp tiêu chí entropy+
  disagreement nhưng giới hạn candidate pool còn đúng 16 mẫu như V1-V4) BỊ
  LỖI LOGIC: nếu pool=16 và vẫn chọn ra q=16, thì "top-16 trong pool 16"
  chọn ra toàn bộ pool — không có phép loại bỏ nào xảy ra, tiêu chí guided
  hoàn toàn vô nghĩa, kết quả sẽ thoái hóa trùng V2. Đã tự phát hiện và sửa
  TRƯỚC khi triển khai code (không có công chạy lãng phí).
- Đối chứng ĐÚNG (đã chọn, đúng đề xuất #1 của reviewer): **random_pool64**
  — giữ NGUYÊN candidate pool N=64 giống hệt V5, chỉ thay tiêu chí
  entropy+disagreement bằng chọn ngẫu nhiên (`torch.randperm`). Tách được
  đóng góp của "kích thước pool" khỏi đóng góp của "tiêu chí chọn": nếu
  `random_pool64` ≈ V2 (pool=16) → khác biệt V5 chủ yếu do pool; nếu
  `random_pool64` ≈ V5 (pool=64, có tiêu chí) → khác biệt chủ yếu do tiêu
  chí. 3 đối chứng còn lại của reviewer (entropy-only, disagreement-only,
  và "guided_pool16" — nay biết là vô nghĩa) KHÔNG làm, theo phạm vi user
  đã chọn ("sửa văn bản + 1 đối chứng tối thiểu").

### Code đã thêm (CHƯA chạy job thật, chỉ `py_compile` sạch)
- `scripts/train_all.py`: hàm `select_random_idx(n, q, device)` —
  `torch.randperm(n)[:q]` trong `torch.no_grad()`. Nhánh mới trong vòng lặp
  huấn luyện: `elif cfg["sel"] == "random_pool64": idx =
  select_random_idx(x.shape[0], q, device=device); sf, tf, mask =
  s_feats[idx], t_feats[idx], None`. Method mới trong `METHOD_TABLE`:
  `qrd_random_pool64` (`kernel="quantum"`, `sel="random_pool64"`, mọi tham
  số khác giống hệt `qrd_dense`/V2). Không backup `.bak` riêng cho đợt sửa
  này (đã có nhiều `.bak_before_*` từ Vấn đề 1-3 + git tracking đủ để
  rollback nếu cần).

### ĐANG CHỜ XÁC NHẬN — job `jobs/pool64_control.pbs` (CHƯA submit)
- Đây là JOB THẬT (~2,8h ước tính: 5 seed × 5 fold × 30 epoch, quantum
  ~13,6s/epoch từ log tham chiếu), không phải smoke test → theo quy tắc dự
  án PHẢI trình bày kế hoạch và chờ xác nhận trước khi `qsub`.
- Kế hoạch: `-q sharedgpu`, `ncpus=8 mem=64gb gpu_slots=1`, walltime 6h
  (dư dả). Bước 1: sanity-check `select_random_idx` (pool thật sự =64 chứ
  không phải =16, tập chỉ số đổi giữa các lần gọi) — dừng job (exit 3) nếu
  FAIL. Bước 2: `run_seeds.py` với `QRD_RUNS="random_pool64:
  qrd_random_pool64:0.02"`, `QRD_SEEDS="1,2,3,4,5"`, PhysionetMI → ghi
  `results/pool64_control_2026_08_04/pool64_control_per_subject.csv` (dự
  kiến 515 dòng). V5 (`qrd_teacher_guided`) và V2 (`qrd_dense`) KHÔNG chạy
  lại — tái dùng số liệu đã có trong Bảng `tab:bienthe`/`seeds_per_subject.csv`.
- **SAU KHI xong**: so `random_pool64` (mean±std 5 seed) với V2 (81,49±0,78)
  và V5 (81,12±0,71) bằng paired t-test (n=5, df=4) từng cặp. Viết phát
  hiện vào đoạn diễn giải V5 ở Mục 4.4 (đã chừa sẵn chỗ, dòng ~1486-1491)
  và cập nhật/rút câu giới hạn tương ứng ở Kết luận. Viết SAU KHI có số,
  không đoán trước.

---
## CẬP NHẬT 2026-08-04 (tiếp) — Vấn đề lớn 5 (review IJRCS): chỉ một bộ dữ liệu

### PHÁT HIỆN QUAN TRỌNG — job 11713 CHÍNH LÀ kiểm chứng dataset thứ hai
- User xác nhận: job 11713 (`cho_qrd_all6_rerun`, đã chạy suốt phiên, là
  nguyên nhân chặn toàn bộ hàng đợi qua giới hạn `mem=64gb` per-user) KHÔNG
  phải job không liên quan — đây CHÍNH LÀ lần chạy kiểm chứng trên bộ dữ
  liệu MI thứ hai (**Cho2017**, LOSO 49 đối tượng) mà reviewer đề xuất ở
  Vấn đề lớn 5. Script: `jobs/cho/qrd_all6_rerun.pbs`. Chạy lại 6 method
  liên quan kernel lượng tử (`qrd_dense/anchor/global_local/teacher_guided`
  + `qrd_tg_b0.01/0.05`) × 5 seed, RERUN vì mạch lượng tử từng bị lỗi suy
  biến (xem `docs/PREREG_2026_07_30.md`, đã sửa bằng data re-uploading).
  6 method cổ điển (no_kd/kd_base/feature_kd/rkd_classical/ck_cosine_tg/
  ck_rbf_tg) đã có sẵn kết quả Cho2017 từ TRƯỚC (không cần rerun, không bị
  ảnh hưởng bởi lỗi mạch lượng tử) — xem `results/cho_*_per_subject.csv`,
  `results/cho_all12.csv`, `results/results_all_cho_per_subject.csv`.
- **Bài (`body.tex`/`main.tex`) CHƯA hề nhắc "Cho2017" ở đâu cả** (đã grep
  xác nhận) — nghĩa là kết quả Cho2017 CHƯA được tích hợp vào bài, dù đã
  gần chạy xong. Đây là việc còn dang dở, không phải đã hoàn tất.
- Tại thời điểm phát hiện (log `logs/cho/qrd_all6_rerun.log`), job đang ở
  method CUỐI (`qrd_tg_b0.05`), seed CUỐI (5), vừa xong fold 3/5 → gần
  xong toàn bộ, ước tính còn ~20-30 phút (không phải ~45h như ước tính sai
  trước đó dựa trên walltime).

### ĐÃ XONG — sửa văn bản (thu hẹp phạm vi phát biểu, không chờ Cho2017)
User chọn "chỉ thu hẹp phát biểu" (không mở job dataset-2 riêng, vì hóa ra
đã có sẵn và gần xong). Đã sửa 5 chỗ để mọi phát biểu neo rõ "PhysionetMI,
bài toán hai lớp" thay vì "giải mã tưởng tượng vận động" chung chung:
- Mục 2.7/`sec:dinhvi` (đoạn "ca kiểm chứng khắt khe nhất"): làm rõ câu
  "phạm vi rộng hơn đáng kể" chỉ áp dụng cho TRỤC LỰA CHỌN KHÔNG GIAN BIỂU
  DIỄN (kernel cổ điển vs lượng tử), không mở rộng sang dataset/bài toán
  khác — thêm câu chốt lại phạm vi PhysionetMI/hai lớp.
- Kết luận, đoạn mở đầu: thêm "trên bộ dữ liệu PhysionetMI và bài toán
  phân biệt hai lớp" ngay câu đầu.
- Kết luận, đoạn "hệ quả" (khuyến nghị thiết kế hệ thống): thêm "Trong
  phạm vi bài toán tưởng tượng vận động hai lớp trên PhysionetMI đã khảo
  sát" ở đầu đoạn.
- Kết luận, đoạn giới hạn: thêm câu chỉ rõ "mọi phát biểu trong bài, kể cả
  câu tổng kết ở Đóng góp và đầu Mục Kết luận, cần đọc trong phạm vi đó",
  và thêm câu THÔNG BÁO Cho2017 đang chạy dở, kết quả sẽ bổ sung khi xong.
- Kết luận, đoạn "hướng phát triển tiếp theo": sửa "kiểm chứng trên bộ dữ
  liệu thứ hai" (viết như việc CHƯA làm) thành "hoàn tất kiểm chứng... đang
  tiến hành (Cho2017)" — khớp với thực tế.
- Tóm tắt (`main.tex`): thêm "(bộ dữ liệu PhysionetMI)" + "hai lớp" vào câu
  mô tả bài toán kiểm định.
- Biên dịch tectonic sạch, không undefined.

### CHỜ LÀM SAU KHI JOB 11713 XONG (việc lớn nhất còn lại của cả phiên)
- Đọc `results/cho_qrd_all6_rerun_per_subject.csv` (6 method quantum, 5
  seed) + số liệu cổ điển đã có sẵn (`results/cho_*_per_subject.csv`) →
  ghép thành bảng đầy đủ 12 cấu hình trên Cho2017, tương tự Bảng
  `tab:bienthe`/`tab:tongthe` đã làm cho PhysionetMI.
  **CẢNH BÁO**: các method quantum trong `results/cho_qrd_dense_per_subject.csv`,
  `results/cho_qrd_anchor_per_subject.csv`, v.v. (KHÔNG có hậu tố `_rerun`)
  là số liệu TỪ TRƯỚC KHI SỬA MẠCH LƯỢNG TỬ — theo `PREREG_2026_07_30.md`
  mục "Số liệu bị vô hiệu", các số liệu `kernel="quantum"` sinh trước
  2026-07-30 KHÔNG được dùng trong bài. CHỈ dùng
  `cho_qrd_all6_rerun_per_subject.csv` cho 6 method quantum trên Cho2017.
- So sánh kết quả Cho2017 với kết luận đã báo cáo trên PhysionetMI: có tái
  lập được xu hướng "chưng cất giúp lớn, khác biệt giữa cơ chế/kernel dưới
  ngưỡng phát hiện" không? Viết phát hiện vào một mục mới hoặc phụ lục,
  KHÔNG p-hacking/không chọn cách trình bày đẹp hơn cho Cho2017.
  Vì đây LÀ so sánh xác nhận tính khái quát (không phải so sánh chính đã
  tiền đăng ký với biên tương đương), cần làm rõ trong bài đây là kết quả
  KHÁM PHÁ (exploratory), không phải kiểm định xác nhận (confirmatory).
- Sau khi có bảng Cho2017: cân nhắc RÚT BỚT các câu "giới hạn phạm vi" vừa
  thêm ở trên nếu kết quả tái lập tốt (nhưng KHÔNG xóa hoàn toàn — vẫn chỉ
  2 dataset, không phải khái quát đầy đủ). Nếu KHÔNG tái lập, đây là phát
  hiện quan trọng cần viết rõ, không giấu.
- Sau khi 11713 xong, giới hạn `mem=64gb` per-user sẽ giải phóng → 7 job
  đang `Q` (11718, 11719, 11720, 11721, 11727, 11731, 11732) sẽ bắt đầu
  chạy. Không cần thao tác gì thêm, PBS tự xếp lịch.

---
## CẬP NHẬT 2026-08-04 (tiếp) — Vấn đề lớn 10 (review IJRCS): "6.180 quan sát" gây hiểu nhầm cỡ mẫu

### ĐÃ XONG
- Xác nhận đúng: Tóm tắt (`main.tex`) ghi "tổng cộng 6.180 quan sát ở mức
  đối tượng" (= 12 cấu hình × 103 đối tượng × 5 hạt giống), trong khi
  Mục~4.1 (`sec:dulieu`) đã nói rõ 515 kết quả/cấu hình KHÔNG độc lập và
  đơn vị suy luận thống kê là HẠT GIỐNG, $n=5$, $df=4$. Con số 6.180 đứng
  một mình trong tóm tắt dễ khiến người đọc tưởng cỡ mẫu kiểm định lớn.
- Đã sửa: đổi "quan sát" → "kết quả", thêm ngay sau đó "các kết quả này
  không độc lập với nhau, và mọi kiểm định thống kê trong bài thực hiện ở
  mức hạt giống, $n=5$." Biên dịch tectonic sạch, không undefined.

---
## CẬP NHẬT 2026-08-04 (tiếp) — Job 11713 (Cho2017) xong, đã đưa vào bài

### ĐÃ XONG
- Job 11713 hoàn tất (`rc=0`), 1470 dòng (6 method quantum × 5 seed × 49
  đối tượng). Hàng đợi giải phóng, 7 job còn lại (11718...11732) bắt đầu
  chạy tuần tự.
- Tính thống kê bằng script thuần Python (không import torch/mne/pandas
  nặng — an toàn chạy trực tiếp trên login node), paired t-test tự cài
  (incomplete-beta, đã kiểm tra khớp bảng t-critical chuẩn ở df=4). Script
  lưu tại `/tmp/.../scratchpad/analyze_cho2017_precise.py` (không phải
  đường dẫn bền vững — nếu cần chạy lại, viết lại từ logic mô tả ở đây).
- Đã viết **Mục 4.4.6 mới** "Kiểm chứng khám phá trên bộ dữ liệu thứ hai
  (Cho2017)" (`sec:cho2017`, sau "Phân tích định tính không gian đặc
  trưng", trước Kết luận) — mô tả dataset (49/52 đối tượng sau loại 3 đối
  tượng 32/46/49 theo danh sách teacher, cùng bài toán hai lớp), Bảng
  `tab:cho2017` (11/12 method, thiếu V1 vì không nằm trong đợt chạy lại
  sau lỗi mạch), và 5 đối chiếu định tính với PhysionetMI:
  1) hiệu ứng chưng cất tái lập (+5,24pp, p=0,006, biên độ nhỏ hơn 18,43pp
     do teacher Cho2017 yếu hơn: 75,07±4,16% so với 84,98±2,59%);
  2) khác biệt giữa cơ chế < nhiễu hạt giống nhưng biên mỏng hơn (tỷ lệ
     0,84 so với 0,58 trên PhysionetMI);
  3) FeatureKD kém hơn KDBase tái lập gần như nguyên (-1,38pp p=0,003 so
     với -1,44pp p=0,016); RelationalKD≈KDBase tái lập (+0,03pp p=0,864
     so với +0,12pp p=0,754);
  4) so sánh kernel chính (lượng tử vs cosine, V5) ĐỔI CHIỀU DẤU giữa 2
     dataset (Cho: +0,28pp p=0,389; PhysionetMI: -0,51pp) nhưng cả hai CI
     đều rộng và phủ 0 — không mâu thuẫn, càng củng cố "chưa có bằng chứng
     khác biệt hệ thống";
  5) hai kết quả KHÔNG có đối chiếu trực tiếp trên PhysionetMI (cosine vs
     KDBase p=0,030; V5 β=0,01 vs KDBase p=0,018) chỉ báo cáo, không gọi
     là "không tái lập" vì không có phép so sánh gốc tương ứng.
  Toàn mục gắn nhãn rõ **KHÁM PHÁ, không tiền đăng ký, không thay thế**
  phép kiểm định chính đã chốt trên PhysionetMI.
- Đã lấp placeholder ở Kết luận (đoạn giới hạn) bằng kết quả thật, sửa
  đoạn "hướng phát triển tiếp theo" (không còn nói "sẽ kiểm chứng" mà nói
  "nên tiền đăng ký và lặp lại phép kiểm định CHÍNH" trên dataset 2 — phân
  biệt rõ với khảo sát khám phá đã làm).
  Thêm 1 câu vào Tóm tắt (`main.tex`) nhắc Cho2017.
- Thêm bibtex `cho2017eeg` vào `references.bib` cho bộ dữ liệu Cho2017.
  **CẢNH BÁO ghi rõ trong file**: chi tiết (volume/số trang/DOI) ghi theo
  trí nhớ, chưa đối chiếu được vì môi trường không có internet — PHẢI
  kiểm tra lại trước khi nộp bài.
  Nhân tiện sửa luôn 2 chỗ `;` nối mệnh đề độc lập lỡ lọt vào `main.tex`
  trong lúc viết (cùng lỗi đã sửa toàn bộ `body.tex` ở mục trước).
- Biên dịch tectonic nhiều lần, sạch, không lỗi/undefined mỗi lần.

### CHƯA LÀM / CẦN NGƯỜI DÙNG KIỂM TRA
- **Xác minh chi tiết bibtex `cho2017eeg`** (tên tác giả, volume, DOI) trên
  Google Scholar/GigaScience trước khi nộp — Claude không có internet để
  tự kiểm.
- Cân nhắc thêm Hình minh họa hoặc rút gọn Mục 4.4.6 nếu bài vượt giới hạn
  trang của IJRCS (chưa kiểm tra số trang hiện tại).
- Việc "tiền đăng ký + lặp lại kiểm định chính trên dataset 2" (nêu ở
  hướng phát triển) là việc LỚN, chưa lên kế hoạch cụ thể — chỉ mới nêu
  hướng, không phải cam kết thực hiện trong bản nộp này.

---
## CẬP NHẬT 2026-08-04 (tiếp) — Bảng đối chiếu song song PhysionetMI/Cho2017

### Bối cảnh quyết định (quan trọng, đừng lặp lại hướng đã từ chối)
- User hỏi có nên **ghép** dữ liệu Cho2017 thẳng vào các bảng cũ
  (`tab:tongthe`, `tab:bienthe`) để "bài trông ổn hơn" không. Đã TỪ CHỐI
  hướng này và giải thích lý do, user đồng ý: (1) đơn vị suy luận $n=5$
  hạt giống giả định các hạt giống là lần rút độc lập CÙNG một quy trình,
  hạt giống Cho2017 và PhysionetMI không thỏa; (2) so sánh chính (lượng
  tử vs cosine, biên ±0,5pp) đã tiền đăng ký RIÊNG cho PhysionetMI, gộp
  thêm Cho2017 sau khi biết cả 2 kết quả là data dredging; (3) teacher 2
  bên khác hẳn (84,98% vs 75,07%) nên thang accuracy không cùng ý nghĩa;
  (4) V1 không có trên Cho2017, ghép vào sẽ chắp vá.
  **KHÔNG bao giờ tự ý gộp raw rows của 2 dataset vào chung một kiểm định
  $t$/bảng kết quả chính nếu có yêu cầu tương tự sau này** — đây là ranh
  giới đã được xác nhận rõ ràng với user.

### ĐÃ XONG — Bảng đối chiếu song song (thay vì gộp)
- Thêm **Bảng `tab:sosanh2dataset`** trong Mục 4.4.6 (`sec:cho2017`), ngay
  sau câu dẫn, TRƯỚC 5 đoạn diễn giải chi tiết đã có — đối chiếu $\Delta$
  (so KDBase) + $p$ của PhysionetMI và Cho2017 song song theo hàng, cột
  cuối "Cùng chiều" (Có/Không), lấy toàn bộ số liệu từ các bảng ĐÃ CÓ sẵn
  trong bài (`tab:bienthe`, `tab:tongthe`, Mục~\ref{sec:ketqua}), không
  tính toán gì mới ngoài những gì đã báo cáo trước đó.
  V1 Dense: cột Cho2017 để "---" (không có số liệu), không suy diễn.
- Thêm đoạn văn ngay sau bảng: 5/12 hàng đổi chiều dấu (V2 Dense, nhân
  cosine, nhân RBF, cả 2 so sánh kernel trực tiếp), tất cả đều có
  $|\Delta| < 0{,}5$pp ở ít nhất 1 bên (vùng nhiễu hạt giống dễ đảo dấu),
  CHỈ riêng hàng cosine có $p=0{,}030$ đáng chú ý (đã bàn ở đoạn dưới), 4
  hàng còn lại không có ý nghĩa ở bên nào — đọc kỹ số trước khi viết diễn
  giải, không phóng đại cũng không giấu.
- Biên dịch tectonic sạch nhiều lần. Nhân tiện dọn nốt 2 chỗ `;` nối mệnh
  đề độc lập lỡ lọt vào đoạn văn Mục 4.4.6 khi viết thêm (đã áp dụng đúng
  nguyên tắc trong memory `feedback_vietnamese_punctuation_calque`).

---
## CẬP NHẬT 2026-08-04 (tiếp) — QUAN TRỌNG: sửa số liệu V1 SAI đã có sẵn trong bài (không phải job mới)

### PHÁT HIỆN (đọc kỹ trước khi đụng lại V1/PhysionetMI)
- Job `qrd_v1_seeds_rerun` (11718, đã submit từ trước phiên hiện tại, hoàn
  tất trong phiên này) chạy `qrd_dense_noproj` (V1) × 5 seed × 5 fold trên
  PhysionetMI với MẠCH LƯỢNG TỬ ĐÃ SỬA. Kết quả:
  `results/qrd_v1_rerun_2026_08_03/seeds_v1_rerun_per_subject.csv`
  (515 dòng, `rc=0`).
- Đối chiếu phát hiện: **số V1 đang dùng trong TOÀN BỘ bài (81,34±0,52)
  đến từ `results/seeds_v1_per_subject.csv`** — đúng file mà
  `docs/PREREG_2026_07_30.md` mục "Số liệu bị vô hiệu" đã liệt kê tên
  tường minh là dữ liệu quantum SINH TRƯỚC KHI SỬA MẠCH, KHÔNG được dùng
  trong bài. Đã verify bằng script thuần Python: file `seeds_v1_per_subject.csv`
  cho đúng 81,34±0,52 (khớp số cũ trong bài tới 2 chữ số); file rerun mới
  cho **81,90±0,71**.
  → Đây là một **lỗi số liệu đã tồn tại trong bài TRƯỚC phiên này**, không
  phải chuyện tôi gây ra — nhưng giờ đã sửa. **KHÔNG BAO GIỜ dùng lại
  `results/seeds_v1_per_subject.csv`** cho bất kỳ việc gì liên quan V1.
- File nguồn ĐÚNG cho V1 (PhysionetMI, 5 seed, mạch đã sửa):
  `results/qrd_v1_rerun_2026_08_03/seeds_v1_rerun_per_subject.csv`
  (tag `qrd_dense_noproj`).
- Đã verify TOÀN BỘ phương pháp tính bằng cách tái tạo chính xác mọi số
  liệu cũ đã công bố của các method KHÔNG bị lỗi (KDBase 81,49±0,59,
  FeatureKD Δ=-1,44 p=0,016, RelationalKD Δ=+0,12 p=0,754, qrd_dense
  Δ=0,00 p=1,000, qrd_anchor Δ=-0,24 p=0,351, qrd_global_local Δ=-0,07
  p=0,775, qrd_teacher_guided Δ=-0,37 p=0,231, cosine Δ=+0,14 p=0,609,
  RBF Δ=+0,13 p=0,511, Spearman ρ=0,46 với data cũ) — khớp tuyệt đối với
  số đã in trong bài, nên tin cậy toàn bộ số liệu mới tính cho V1.

### ĐÃ SỬA (toàn bộ chỗ dùng số V1 hoặc số phái sinh từ nó)
1. Bảng `tab:bienthe`: V1 $81{,}34\pm0{,}52$/Δ-0,15/p=0,631 →
   $81{,}90\pm0{,}71$/Δ+0,41/p=0,158.
2. Đoạn "Khối đầu tiên" (V1 vs V2 trực tiếp): Δ 0,15pp p=0,541 (không khác
   biệt) → Δ 0,41pp p=0,085 (**ranh giới ý nghĩa, ĐỔI CHIỀU**: V1 (không
   học) cao hơn V2 (học được), không phải ngược lại). Viết lại cả đoạn
   diễn giải, không còn nói "không đóng góp gì đo được" một cách chắc
   nịch mà nói "chưa cho thấy lợi ích đo được... số liệu hiện có còn gợi ý
   chiều ngược lại" — thận trọng vì p=0,085 vẫn >0,05.
3. Bảng `tab:daohang`: cột "Năm hạt giống" của V1 (81,34 hạng 9 → 81,90
   hạng **1**, in đậm) kéo theo re-rank ĐỒNG HẠNG của 7 hàng khác (V2,
   RBF, cosine, β0,01, V4, RelationalKD, β0,05, KDBase — xem bảng trong
   `body.tex` để đối chiếu số chính xác). Caption: Spearman ρ=0,46
   p=0,14 → **ρ=0,14 p=0,66** (tương quan gần như biến mất, tính lại bằng
   công thức Pearson-trên-hạng thuần Python, verify khớp ρ=0,46 khi dùng
   lại rank cũ trước khi tin số mới).
4. Đoạn văn sau Bảng đảo hạng (Mục 4.4.3): sửa mô tả tương quan ("trung
   bình" → "gần như không"), sửa câu sai "hàm nhân cosine, phương án đạt
   kết quả tốt nhất theo năm hạt giống" (SAI với data mới, V1 mới là tốt
   nhất) → đổi thành ví dụ đảo hạng kịch tính nhất là V1 (hạng 11 một hạt
   giống → hạng 1 năm hạt giống).
5. Bảng `tab:dieukhien` (ITR): V1 κ/B/ITR: 0,627/0,306/6,11 →
   **0,638/0,318/6,35** (tính lại bằng công thức \eqref{eq:itr-bits}, đã
   verify công thức khớp chính xác số KDBase đã in).
6. "Std giữa 12 cơ chế" / "std hạt giống": 0,428/0,734 (tỷ lệ 0,58) →
   **0,459/0,750 (tỷ lệ 0,61)** — sửa ở CẢ Mục 4.4.2 lẫn Kết luận lẫn
   Tóm tắt (`main.tex`).
7. Kết luận: đoạn V1-vs-V2 (0,15pp p=0,541 → 0,41pp p=0,085, đổi chiều),
   đoạn Spearman (ρ=0,46/0,14 → ρ=0,14/0,66, thêm ví dụ V1 đảo hạng kịch
   tính hơn cả V5).
8. Bảng `tab:sosanh2dataset` (Mục 4.4.6, Cho2017): hàng V1 Δ-0,15/p=0,631
   → Δ+0,41/p=0,158 (cột Cho2017 vẫn "---", không có số liệu).
9. **Phát hiện thêm khi rà soát**: câu "tỷ lệ tương ứng trên PhysionetMI
   là 0,58" trong chính đoạn so sánh Cho2017 tôi mới viết cũng bị lỗi lây
   (dùng số cũ) → đã sửa thành 0,61. Bài học: khi một con số gốc bị sửa,
   PHẢI grep lại toàn văn tìm mọi chỗ trích dẫn lại con số đó, kể cả ở
   những mục viết SAU và tưởng như không liên quan.
- Biên dịch tectonic sạch, không undefined, sau khi sửa xong toàn bộ.

### CHƯA SỬA — cần bạn tự quyết hoặc tự tính lại
- Kết luận có câu "hiệu ứng tối thiểu phát hiện được ở công suất 80% dao
  động khoảng 0,86 đến 1,33 điểm phần trăm". Thử tái tạo bằng hệ số suy
  từ FeatureKD (1,33/0,80) áp cho sd_diff của các method khác ra khoảng
  **0,56 đến 1,33** (không khớp cận dưới 0,86 đã in) — có thể phương pháp
  gốc dùng power analysis non-central-t chính xác hơn thay vì hệ số tuyến
  tính đơn giản tôi suy ra, hoặc dùng tập method con khác. KHÔNG tự sửa
  vì không chắc đúng phương pháp gốc. Cần người dùng (hoặc phiên sau có
  script gốc) tính lại bằng đúng công cụ đã dùng ban đầu.
- Nên rà thêm các Hình (fig:bienthe, fig:tsne...) xem có chú thích số nào
  liên quan V1 không — chưa kiểm tra vì hình là ảnh tĩnh (image2.png,
  image3.png), không sửa được qua text, chỉ có thể ghi chú nếu phát hiện
  sai.

---
## CẬP NHẬT 2026-08-04 (tiếp) — QUYẾT ĐỊNH: gộp đánh giá 4 đóng góp, chờ hết job

### Bối cảnh
Đã rà soát 4 đóng góp ở Giới thiệu (`body.tex` dòng ~113-130) đối chiếu
với mọi phát hiện trong phiên. Kết luận nhanh:
- **Đóng góp 1** (lượng tử chỉ ở giai đoạn huấn luyện): đứng vững, không
  cần sửa.
- **Đóng góp 2** (5 chiến lược quan hệ, "tách biệt ảnh hưởng không gian
  biểu diễn khỏi cấu trúc quan hệ"): bị ảnh hưởng NHIỀU NHẤT — trục V1-V2
  đổi chiều (p=0,085) sau khi sửa lỗi V1, trục V5 có confound candidate
  pool (Vấn đề lớn 4). Đề xuất mềm câu chữ "cho phép tách biệt" →
  "nhằm tách biệt", nhưng CHƯA sửa, chờ số liệu `pool64_control` (job
  11732, đối chứng `random_pool64`) để biết mức độ nghiêm trọng thực sự.
- **Đóng góp 3** (quy trình đánh giá hướng điều khiển): đứng vững tốt
  nhất, không cần sửa.
- **Đóng góp 4** (chi phí-lợi ích lượng tử vs cosine/RBF): số liệu cốt lõi
  (0,51pp, ~13x chi phí) không đổi, nhưng giả định nền "β công bằng giữa
  3 kernel" chưa kiểm chứng — chờ `beta_fairness_diag` (job 11731).

### QUYẾT ĐỊNH: KHÔNG sửa Đóng góp 2/4 ngay. Gộp lại đánh giá MỘT LẦN
sau khi TẤT CẢ job đang chờ chạy xong, tránh sửa đi sửa lại nhiều lần.

### Việc cần làm khi quay lại phiên sau (checklist đóng)
1. `qstat -u gv_nphuy` — xác nhận queue trống (không còn job nào của dự án
   này đang R/Q).
2. Đọc kết quả từng job theo thứ tự đã submit, đối chiếu tiêu chí đã ghi
   ở mục CHỜ LÀM tương ứng của từng job trong file này:
   - **11719 `no_kd_alpha1`** — ĐÃ XONG (2026-08-04), rc=0, 515 dòng.
     `results/no_kd_alpha1_2026_08_03/no_kd_alpha1_per_subject.csv`. Kết
     quả: no_kd(alpha=1,0)=74,93±2,30 vs no_kd(alpha=0,5, cũ)=63,06±5,03,
     chênh +11,87pp (p=0,0007, n=5) — xác nhận baseline cũ bị huấn luyện
     dưới mức (lỗi: `loss = alpha*ce` áp dụng cả cho no_kd dù không có số
     hạng KD để cân bằng). Hiệu ứng chưng cất đúng: KDBase(81,49) -
     no_kd(74,93) = +6,56pp, 95% CI [4,08; 9,04], p=0,0018 (không phải
     18,43pp như cũ). ĐÃ SỬA trong body.tex/main.tex (9 vị trí: Bảng
     tab:tongthe, prose Mục~\ref{sec:ketqua}, Bảng tab:dieukhien (ITR) +
     prose, Mục~\ref{sec:xephang} (đoạn seed-variance no_kd), Mục
     \ref{sec:cauhinh} (thêm đoạn giải thích lỗi + cách sửa), Kết luận
     (đoạn hiệu ứng chính + đoạn giới hạn), abstract main.tex). Đã compile
     sạch, không "undefined reference" mới.
     **CHƯA GIẢI QUYẾT**: số no_kd trên Cho2017 (Mục~\ref{sec:cho2017},
     67,31%, `jobs/cho/no_kd.pbs`) dùng cùng alpha=0,5 mặc định, KHÔNG có
     override, nên rất có thể cũng bị lỗi tương tự và biên độ 5,24pp trên
     Cho2017 có thể vẫn bị phóng đại. Đã ghi caveat trong bài (Mục
     cho2017 + phần giới hạn Kết luận) nhưng CHƯA chạy job sửa lại. Nếu
     muốn sửa dứt điểm: cần 1 job `no_kd` trên Cho2017 với `QRD_ALPHA=1.0`,
     5 seed × 5 fold × 49 subject (nhỏ hơn PhysionetMI, job 11719 tương tự
     chạy ~51 phút cho 103 subject nên job này ước tính nhanh hơn, nhưng
     chưa đủ chắc chắn ≤30 phút để tự ý qsub — cần hỏi trước theo quy tắc
     project). Đề xuất hỏi người dùng ở lượt tiếp theo.
     **CẬP NHẬT**: người dùng đã xác nhận chạy. Job `cho_no_kd_alpha1`
     submit 2026-08-04, **ID 11735** (`jobs/cho_no_kd_alpha1_seeds.pbs`,
     walltime 2h, QRD_ALPHA=1.0, Cho2017, 5 seed × 5 fold × 49 subject).
     Out: `results/cho_no_kd_alpha1_2026_08_04/cho_no_kd_alpha1_per_subject.csv`
     (đích 245 dòng), log: `logs/cho_no_kd_alpha1_seeds.log`. TIÊU CHÍ khi
     xong: so acc mới với 67,31% (alpha=0,5) đang báo cáo trong Mục
     cho2017; nếu chênh đáng kể → sửa lại đoạn "hiệu ứng chưng cất tái lập"
     (5,24pp) trong Mục~\ref{sec:cho2017} + xóa caveat "chưa được thực
     hiện" ở đó và ở phần giới hạn Kết luận, thay bằng số liệu đã sửa.
   - **11720 `kernel_fair_seeds`** (= "Vấn đề 7" từ phiên trước, đã có ghi
     chú chi tiết ở mục "## Vấn đề 12..." phía trên, dòng ~195-222): chạy
     `ck_cosine_tg_proj`/`ck_rbf_tg_proj` — cosine/RBF tính trên KHÔNG GIAN
     4 CHIỀU đã chiếu qua $W_S$ học được (580 tham số), giống hệt nhánh
     quantum, thay vì đặc trưng thô 144 chiều như `ck_cosine_tg`/`ck_rbf_tg`
     gốc. Mục đích: kiểm soát công bằng số chiều + tham số học được giữa
     kernel lượng tử và kernel cổ điển — đây CHÍNH LÀ input trực tiếp cho
     quyết định sửa Đóng góp 4, độc lập với `beta_fairness_diag`. Ra:
     `results/kernel_fair_2026_08_03/kernel_fair_per_subject.csv` (đích
     1030 dòng). Tiêu chí: so acc phiên bản `_proj` với phiên bản gốc
     (144 chiều) và với V5 quantum (81,12%) — đổi nhiều thì phải viết lại
     có điều kiện; không đổi nhiều thì củng cố kết luận cũ.
   - **11721 `tsne_feats`**: trích đặc trưng THẬT trên tập TEST cho 4
     method (no_kd, kd_base, feature_kd, qrd_teacher_guided) để vẽ lại
     Hình t-SNE bằng `scripts/plot_tsne.py` (đã viết sẵn, chạy được ngay
     trên login node, không cần qsub). Đây là việc vẽ HÌNH, không phải số
     liệu thống kê ảnh hưởng tới 4 Đóng góp — theo đúng chỉ đạo của user
     (2026-08-04): việc rà hình ảnh (Hình 1, Hình 2, Hình 3 t-SNE) dồn hết
     vào bước KIỂM TRA TÍNH NHẤT QUÁN CUỐI CÙNG khi bản thảo đã chốt, KHÔNG
     làm xen giữa lúc còn đang sửa nội dung. Vẫn có thể chạy `plot_tsne.py`
     ngay khi 11721 xong để có sẵn hình mới, nhưng việc SO SÁNH/SỬA chú
     thích + Mục 4.4.5 thì để dành tới bước chốt bản thảo.
   - **11727 `theta_mode_ablation`**: đối chứng Vấn đề lớn 1 (theta_mode
     shared/shared_fixed/split), 5 seed × 5 fold × 2 method, 16h walltime.
     Tiêu chí phân tích đã ghi chi tiết ở mục "CẬP NHẬT 2026-08-04 — rà
     văn phong..." phía trên (paired t-test 3 nhánh).
   - **11731 `beta_fairness_diag`**: đo `rawL=`/`gradNormS=` cho quantum/
     cosine/RBF — quyết định Đóng góp 4 có cần thêm caveat không.
   - **11732 `pool64_control`**: đối chứng `random_pool64` — quyết định
     Đóng góp 2 có cần sửa câu chữ không, và viết bổ sung vào Mục 4.4.2
     (đã chừa sẵn chỗ ở đoạn diễn giải V5, dòng ~1496-1502).
3. Sau khi có đủ số liệu: viết lại Đóng góp 2 và/hoặc 4 MỘT LẦN (không
   sửa rải rác), đối chiếu với toàn bộ Kết luận để nhất quán.
4. Biên dịch tectonic lần cuối, kiểm tra sạch.

---
## CẬP NHẬT 2026-08-04 (tiếp) — rà logic body.tex lần 2 + kết quả job đợt cuối

### ĐÃ XONG — sửa lỗi logic/số liệu trong body.tex (không cần chờ job)
Rà lại toàn bộ `body.tex` từ đầu đến cuối một lần nữa, đối chiếu số liệu
Kết luận với từng bảng, kiểm tra tham chiếu chéo `\ref`/`\eqref`/`\label`.
Biên dịch tectonic 2 lần liên tiếp sau mỗi lần sửa, sạch, không "undefined
reference" mới.
- [x] Mục 4.4.5 (t-SNE), dòng ~1791: câu "phù hợp với khoảng cách 18 điểm
      phần trăm" dùng số 18,43 đã bị bác bỏ (lỗi alpha) thay vì số đã sửa
      6,56 — sót lại khi sửa lỗi alpha trước đó. Đã đổi thành "6,56 điểm
      phần trăm".
- [x] Kết luận, đoạn giới hạn, dòng ~2071 và ~2077: "Cuối cùng" lặp hai lần
      trong cùng một đoạn liệt kê giới hạn (V5 candidate pool, và no_kd
      Cho2017 chưa sửa alpha). Đổi "Cuối cùng" thứ nhất (dòng 2071) thành
      "Bên cạnh đó", giữ "Cuối cùng" thứ hai (dòng 2077, ý thật sự cuối).
- [x] Mục 2.5 "Định vị của nghiên cứu này", dòng ~589-596 (lập luận "ca
      kiểm chứng khắt khe nhất"): điều kiện nhị nguyên "nếu quantum KHÔNG
      tách khỏi đường cơ sở thì kết luận mở rộng phạm vi" không khớp với
      kết quả thực tế của bài, vốn là "chưa đủ dữ liệu để kết luận theo
      bất kỳ chiều nào" (CI vượt biên tương đương, Mục~\ref{sec:ketqua}),
      không phải "xác nhận không tách khỏi". Bài không hề khép lại vòng
      lặp này ở đâu, đúng kiểu để "không bác bỏ H0" ngầm trôi thành "đã
      xác nhận H0" mà các đợt review trước rất khắt khe khi nó xảy ra ở
      phần Kết quả, chỉ là lần này nằm ở phần đặt vấn đề nên lọt qua chính
      các đợt rà soát đó. Đã sửa: mở rộng điều kiện cho khớp cả ba loại
      kết quả bài dùng nhất quán ở nơi khác (khác biệt/tương đương/chưa đủ
      dữ liệu), trỏ tới Mục kết quả, thêm câu chặn không suy ra "không
      gian biểu diễn hoàn toàn không có vai trò" (khẳng định mạnh hơn dữ
      liệu cho phép).

### ĐÃ XONG — kết quả job đợt cuối (đọc log, phân tích bằng script Python
thuần csv+statistics, KHÔNG dùng scipy/pandas trên login node sau khi gặp
sự cố treo, xem cảnh báo hạ tầng bên dưới)
- **11720 `kernel_fair_seeds`**: rc=0, 1030 dòng. `ck_cosine_tg_proj` (4
  chiều, có $W_S$ học được, công bằng với quantum) = 81,25±0,70;
  `ck_rbf_tg_proj` = 81,36±0,91. So với bản gốc 144 chiều (cosine
  81,63±0,63, RBF 81,61±0,58): Δ=-0,38pp (p=0,168) và Δ=-0,25pp (p=0,293),
  không có ý nghĩa. So với V5 quantum (81,12±0,71): cos_proj Δ=+0,13pp
  (p=0,647), rbf_proj Δ=+0,24pp (p=0,312), không có ý nghĩa. Khoảng cách
  quantum-cổ điển CO LẠI (0,49-0,51pp bản gốc → 0,13-0,24pp bản công bằng
  chiều), không nới rộng. KẾT LUẬN cho Đóng góp 4: củng cố thêm kết luận cũ
  ("3 kernel không phân biệt được"), không cần viết lại có điều kiện. Vẫn
  chờ `beta_fairness_diag` (11747) trước khi viết vào bài.
- **11727 `theta_mode_ablation`**: rc=0, 1030 dòng. theta_shared (=V2
  Dense, 81,49±0,78) vs theta_fixed (81,73±0,49): Δ=-0,25pp, p=0,143.
  theta_shared vs theta_split (81,35±0,87): Δ=+0,13pp, p=0,615. theta_fixed
  vs theta_split: Δ=+0,38pp, p=0,215. KHÔNG cặp nào có ý nghĩa. KẾT LUẬN
  cho Đóng góp 2/Mục 3.4: rủi ro co-adaptation do dùng chung θ (nêu ở Mục
  ~926-936) có thể hạ mức nghiêm trọng, nhưng GIỮ NGUYÊN đoạn giải thích cơ
  chế, chỉ THÊM số liệu thực nghiệm này khi viết gộp. Vẫn chờ
  `pool64_control` (11732) trước khi viết vào bài.
- **11721 `tsne_feats` + 11738 `plot_tsne_cpu`**: cả hai rc=0.
  `paper/figs/image3.png` đã được vẽ lại với 4 panel THẬT (no_kd 71,67%,
  kd_base 82,33%, feature_kd 81,78%, qrd_teacher_guided 80,78% — 1 fold, 1
  seed, không phải số 5-seed dùng trong bảng chính) + silhouette 144D +
  cùng thang trục. Metadata đầy đủ ở
  `results/tsne_feats_2026_08_03/tsne_meta.json`. CHƯA sửa chú thích/Mục
  4.4.5 — theo đúng chỉ đạo trước, việc này để dành tới bước KIỂM TRA TÍNH
  NHẤT QUÁN CUỐI CÙNG khi bản thảo đã chốt (cùng lúc với Hình 1, Hình 2).
- **11731 `beta_fairness_diag`**: rc=0 NHƯNG dữ liệu KHÔNG dùng được. Log
  in đủ `rawL=` mỗi epoch nhưng `gradNormS=` không bao giờ xuất hiện, dù
  `QRD_GRAD_DIAG=1` đặt đúng trong job. NGUYÊN NHÂN (bug thật trong code
  chẩn đoán, không phải log bị cắt): `RelationalDistillLoss.forward()`
  (`scripts/train_all.py` dòng ~200) gán lại `self.last_diag = dict(...)`
  MỚI HOÀN TOÀN mỗi lần gọi. Khối chẩn đoán (dòng ~424-435) chỉ ghi
  `grad_norm_student` vào `last_diag` ở batch đầu mỗi epoch, nhưng mọi
  batch sau gọi `forward()` lại và xóa mất key này trước khi tới lúc in
  log cuối epoch (dòng ~443-449). ĐÃ SỬA: chuyển sang lưu vào attribute
  riêng `rel_loss._grad_norm_student_diag`, không bị `forward()` ghi đè,
  đọc riêng ở chỗ in log. Không đổi hành vi khi `QRD_GRAD_DIAG` không đặt
  (backup: git diff, không có `.bak` riêng cho lần sửa này). Đã `py_compile`
  sạch. Người dùng đã xác nhận chạy lại, đè lên
  `results/beta_fairness_diag_2026_08_04/` và `logs/beta_fairness_diag.log`
  cũ (dữ liệu cũ vốn thiếu đúng phần cần dùng). **Job 11747** đã submit,
  cùng lệnh `run_all.py --methods qrd_dense,ck_cosine_tg,ck_rbf_tg --folds 0
  --epochs 5 --skip_teacher`, xếp `Q` sau 11732/11735.

### CẢNH BÁO HẠ TẦNG MỚI — KHÔNG chạy scipy/sklearn/matplotlib trực tiếp
trên login node hôm nay (2026-08-04), dù không nằm trong danh sách cấm rõ
tên (torch/mne/moabb/braindecode) của CLAUDE.md
- Thử `scipy.stats.ttest_rel` trực tiếp trên login node: tiến trình rơi
  vào trạng thái `Dl` (disk-sleep, khóa trang nhớ) sau ~1 phút, giống đúng
  kiểu treo do NFS cold-read. Đã `kill -9` ngay. Thay bằng thuật toán
  incomplete-beta tự cài bằng `math`/`statistics` thuần (đã kiểm chứng
  khớp bảng t-critical chuẩn ở df=4), chạy bằng `python3` hệ thống
  (`/opt/anaconda3/bin/python3`, KHÔNG phải `qrd_env`) để chắc chắn không
  kéo theo thư viện nào từ `qrd_env` trên NFS.
- Thử `scripts/plot_tsne.py` (numpy/sklearn/matplotlib từ `qrd_env`) trực
  tiếp trên login node 3 lần (timeout 100s/280s/550s) đều bị cắt. Soi đúng
  process con (PID con của `timeout`, không phải wrapper) ở lần cuối: trạng
  thái `Dl`, 64 luồng (threadpool BLAS/sklearn), RSS nhỏ bất thường — cùng
  kiểu NFS cold-read. Đã `kill -9`. Chuyển hẳn sang chạy qua `qsub`
  (`jobs/plot_tsne_cpu.pbs`, CPU-only `gpu_slots=0`, walltime 30 phút, dạng
  smoke test tự submit) — chạy thành công ngay khi tới lượt (job 11738).
  BÀI HỌC: quy tắc "không import nặng trên login node" của CLAUDE.md nên
  áp dụng RỘNG HƠN danh sách nêu tên (torch/mne/moabb/braindecode) — bất
  kỳ thư viện có compiled extension lớn (scipy, sklearn, có thể cả
  matplotlib qua các backend) đều có thể gặp NFS cold-read tương tự trên
  cụm này, ít nhất trong điều kiện tải hôm nay (load average ~16).

### QUYẾT ĐỊNH (giữ nguyên, không đổi): chờ TẤT CẢ job xong rồi viết Đóng
góp 2/4 + Kết luận MỘT LẦN, không sửa rải rác theo từng job
- Đóng góp 2 cần gộp `theta_mode_ablation` (xong) + `pool64_control` (đang
  chạy, 11732).
- Đóng góp 4 cần gộp `kernel_fair_seeds` (xong) + `beta_fairness_diag`
  (đang chờ chạy lại, 11747).
- Ghi kết quả từng job vào mục này ngay khi có, để không phải giữ trong
  đầu qua nhiều phiên, nhưng KHÔNG động vào Đóng góp 2/4/Kết luận trong
  `body.tex` cho tới khi cả 4 job trên (11732, 11735, 11747, và đã có sẵn
  11720/11727) đều có kết quả.

### Việc cần làm khi quay lại phiên sau (checklist cũ, ĐÃ HOÀN TẤT phần đọc
kết quả 11732/11747, xem mục mới ngay dưới; chỉ còn việc số 5/6 và job
11735 chạy lại)
1. ~~`qstat -u gv_nphuy` — xác nhận trống~~ ĐÃ XONG, trống, đọc kết quả.
2. ~~Đọc `logs/beta_fairness_diag.log` (11747)~~ ĐÃ XONG, xem số liệu mục
   dưới.
3. ~~Đọc `pool64_control_per_subject.csv` (11732)~~ ĐÃ XONG, xem số liệu
   mục dưới.
4. Đọc `results/cho_no_kd_alpha1_2026_08_04/` (11735) — CHƯA XONG, job bị
   timeout, xem mục "11735 bị timeout" dưới.
5. Viết gộp Đóng góp 2 (theta_mode + pool64) và Đóng góp 4 (kernel_fair +
   beta_fairness) MỘT LẦN, đối chiếu Kết luận cho nhất quán, sửa số liệu
   Cho2017 no_kd nếu 11735 (chạy lại) cho chênh đáng kể.
6. Biên dịch tectonic 2 lần liên tiếp, kiểm tra sạch.

---
## CẬP NHẬT 2026-08-04 (tiếp) — kết quả 11732/11747, job 11735 bị timeout

### ĐÃ XONG — 11732 `pool64_control` (đối chứng random_pool64, Đóng góp 2)
rc=0, 515 dòng. `random_pool64` (pool=64, KHÔNG tiêu chí, chỉ
`torch.randperm`) = 81,36±0,60. So sánh paired t-test (n=5):
- vs V2 Dense (pool=16, có tiêu chí ngầm là vị trí cố định): Δ=-0,13pp,
  p=0,723, KHÔNG có ý nghĩa.
- vs V5 Guided (pool=64, có tiêu chí entropy+disagreement): Δ=+0,24pp,
  p=0,122, KHÔNG có ý nghĩa (nhưng là phép so sánh gần ngưỡng nhất trong
  đợt này, sd\_diff nhỏ = 0,28).

KẾT LUẬN cho Đóng góp 2/Mục 4.4.2: `random_pool64` (81,36) nằm GIỮA V2
(81,49) và V5 (81,12), không khác biệt có ý nghĩa với CẢ HAI. Đây là kết
quả KHÔNG DỨT KHOÁT theo đúng tiêu chí đã đặt ra trước khi chạy (dòng
~601-605 mục trước): không thể quy khác biệt V2-V5 chủ yếu cho pool size
hay cho tiêu chí chọn, vì đối chứng trung gian không nghiêng rõ về bên
nào. Khi viết vào bài: GIỮ NGUYÊN caveat "confound candidate pool" ở Mục
4.4.2/Kết luận, KHÔNG rút bớt, có thể thêm một câu ghi nhận đã thử đối
chứng nhưng không đủ phân giải để tách hai yếu tố.

### ĐÃ XONG — 11747 `beta_fairness_diag` bản sửa lỗi (Đóng góp 4, Vấn đề
lớn 3) — PHÁT HIỆN QUAN TRỌNG, lệch nhiều bậc độ lớn
rc=0. Sau khi sửa bug `gradNormS` (mục trước), log in đủ cho cả 3 kernel,
5 epoch, fold 0. Trung bình 5 epoch mỗi kernel (tính bằng
`statistics.mean`, không dùng scipy/pandas):

| Kernel | rawL (trung bình) | gradNormS (trung bình) |
|---|---|---|
| quantum (qrd_dense) | 1,41e-01 | 1,51e-02 |
| RBF (ck_rbf_tg) | 3,13e-02 | 1,47e-03 |
| cosine (ck_cosine_tg) | 2,16e-03 | 7,54e-05 |

Tỷ lệ: quantum/cosine ×65 (rawL) và **×200 (gradNormS)**; quantum/RBF ×4,5
(rawL) và ×10,3 (gradNormS); RBF/cosine ×14,5 (rawL) và ×19,5 (gradNormS).

KẾT LUẬN cho Đóng góp 4/Mục 3.4 (Vấn đề lớn 3): đây CHÍNH LÀ trường hợp
"lệch nhau nhiều bậc độ lớn" mà tiêu chí đặt ra trước khi chạy đã dự liệu
(mục "Vấn đề lớn 3" phía trên). Cùng $\beta=0,02$ nhân với $\mathcal{L}_{QRD}$
tạo ra mức giám sát hiệu lực lên student CHÊNH NHAU TỚI HAI BẬC ĐỘ LỚN
giữa quantum và cosine. Đây KHÔNG còn là một caveat mơ hồ ("chưa đo trực
tiếp") mà là một con số cụ thể, ĐÁNG được viết rõ vào Mục 3.4/Kết luận khi
gộp sửa Đóng góp 4 (không chỉ giữ nguyên đoạn hedge cũ mà PHẢI thêm bảng
số này). Cần nêu rõ đây là 1 fold, 5 epoch, dữ liệu CHẨN ĐOÁN (không phải
kết quả báo cáo chính), nhưng chênh lệch quá lớn để chỉ nói "chưa kiểm
chứng được".

### CHƯA XONG — 11735 `cho_no_kd_alpha1_seeds` BỊ TIMEOUT, chỉ chạy được
2/5 seed
Log cho `rc=124` (timeout). File kết quả có 137 dòng, đúng bằng seed 1
(49 subject, ĐỦ) + seed 2 (49, ĐỦ) + seed 3 (39, THIẾU 1 fold cuối) + seed
4,5 (0, CHƯA CHẠY). Nguyên nhân: `timeout 6600` (110 phút) trong
`jobs/cho_no_kd_alpha1_seeds.pbs` quá ngắn so với chi phí thật — mỗi
fold-run Cho2017 no\_kd mất ~468s, 25 fold-run (5 seed×5 fold) cần
~11700s (~3,25h) chưa kể tiền xử lý, vượt xa 6600s đã khai. Đây là lỗi ước
lượng walltime, không phải lỗi code.
KHÔNG dùng 137 dòng này cho bất kỳ tính toán nào (thiếu 3/5 seed, không
đủ n=5 cho kiểm định t). File output KHÔNG có cơ chế resume/skip theo
seed đã xong (`scripts/run_seeds.py` ghi CSV tăng dần nhưng không kiểm
tra combo đã có khi chạy lại, luôn tính lại từ seed đầu) — chạy lại phải
làm lại TOÀN BỘ 5 seed, không nối tiếp được từ 137 dòng đã có.
KẾ HOẠCH chạy lại (job thật, ước tính thật ~3,5-4h, cần xác nhận trước
theo quy tắc project):
- Sửa `jobs/cho_no_kd_alpha1_seeds.pbs`: PBS walltime 02:00:00 → 08:00:00,
  `timeout 6600` → `timeout 27000` (7,5h), thêm `QRD_OVERWRITE=1` (đè lên
  file 137 dòng cũ, vốn không dùng được).
  Giữ nguyên mọi tham số khác (`QRD_DATASET=Cho2017`, `QRD_SEEDS="1,2,3,4,5"`,
  `QRD_RUNS="no_kd:no_kd"`, `QRD_ALPHA=1.0`, `ncpus=8 mem=64gb gpu_slots=1`).
  Output vẫn `results/cho_no_kd_alpha1_2026_08_04/cho_no_kd_alpha1_per_subject.csv`
  (đích 245 dòng = 5 seed × 49 subject), log `logs/cho_no_kd_alpha1_seeds.log`.
- CHƯA submit, chờ xác nhận người dùng ở phiên tiếp theo (đã hỏi trong
  chat, xem lịch sử phiên 2026-08-04).

---
## CẬP NHẬT 2026-08-04 (tiếp) — sửa văn phong "kể lỗi", thêm job alpha sweep

### ĐÃ XONG — bỏ văn phong tự sự "tác giả mắc lỗi" trong body.tex
User chỉ ra: câu "Lỗi mạch lượng tử suy biến, phát hiện sau khi có kết quả
PhysionetMI ban đầu... buộc phải chạy lại..." (Mục 4.5.6, Cho2017) đọc như
tường trình lỗi cá nhân, không nên xuất hiện trong bài. Nguyên tắc áp
dụng: KHÔNG tường thuật quy trình phát hiện/sửa lỗi (thứ tự thời gian, "bị
buộc phải") khi nó không mang thông tin khoa học; CHỈ giữ lại disclosure
khi gắn với con số/kết luận cụ thể đã đổi (vd hiệu ứng chưng cất 18,43→
6,56pp) — đó là trung thực khoa học bắt buộc, không phải "kể lỗi".
- [x] Mục 4.5.6 (Cho2017): bỏ "Lỗi... phát hiện sau khi... buộc phải chạy
  lại", thay bằng câu trung tính nêu thẳng 6 cấu hình dùng mạch đã sửa
  (Mục~\ref{sec:qrd}), không kể timeline phát hiện lỗi.
- Đã rà toàn bộ các chỗ có chữ "lỗi"/"đã sửa"/"buộc phải"/"bị vô hiệu"
  trong body.tex (grep, 8 vị trí). Phân loại: 2 vị trí thuộc loại "kể
  lỗi timeline" (đã sửa); còn lại là disclosure số liệu cần thiết
  (Mục~\ref{sec:cauhinh}, Mục~\ref{sec:ketqua}, Kết luận, chú thích Bảng
  tab:daohang) hoặc không liên quan (VD "bắt buộc phải truy cập phần cứng
  lượng tử" ở Mục~\ref{sec:qml}, nói về ràng buộc thiết kế của công trình
  khác, không phải lỗi của bài này) — CHƯA sửa các vị trí này, đang chờ
  quyết định dưới.

### ĐANG CHỜ — cách trình bày hiệu ứng chưng cất PhysionetMI (18,43 vs 6,56)
User muốn thay khung "phát hiện lỗi alpha, đã sửa" bằng một BẢNG ĐỘ NHẠY
ALPHA minh bạch cho `no_kd`: liệt kê alpha ∈ {0; 0,25; 0,5; 0,75; 1,0} và
accuracy tương ứng, chỉ rõ alpha=1,0 là giá trị dùng cho baseline chính
(lý do: no_kd không có số hạng KD để cân bằng, alpha=1,0 là giá trị duy
nhất cho đủ trọng số số hạng CE duy nhất nó có — không phải "chọn đẹp nhất
sau khi biết kết quả"). Đã có sẵn alpha=0,5 (63,06±5,03%, dữ liệu cũ) và
alpha=1,0 (74,93±2,30%, `results/no_kd_alpha1_2026_08_03/`). Còn thiếu
alpha=0; 0,25; 0,75.

- [x] **Job 11754** (`jobs/no_kd_alpha_sweep.pbs`): PhysionetMI, `no_kd`,
  alpha ∈ {0,0; 0,25; 0,75}, mỗi giá trị 5 seed × 5 fold, chạy tuần tự
  trong 1 job (`QRD_ALPHA` đổi giữa 3 lần gọi `run_seeds.py`, mỗi lần ghi
  CSV riêng: `no_kd_alpha0.0_per_subject.csv`, `no_kd_alpha0.25_...`,
  `no_kd_alpha0.75_...`, cùng trong `results/no_kd_alpha_sweep_2026_08_04/`).
  Walltime 6h, ước tính thật ~2,5-3h (no_kd nhẹ, ~51 phút/giá trị alpha
  theo tham chiếu job 11719). Đã submit, xếp `Q` sau 11753 (Cho2017 no_kd
  alpha=1.0, đang chạy).
  **LƯU Ý**: đây là lần thứ hai user đề xuất chạy thêm alpha cho no_kd.
  Lần đầu (mục đích "tìm alpha tốt nhất") đã bị từ chối vì p-hacking; lần
  này mục đích khác (bảng minh bạch thay văn phong kể lỗi, không chọn
  "đẹp nhất") nên hợp lý hơn — ĐỪNG lặp lại việc từ chối máy móc nếu có
  đề xuất tương tự lần ba, đọc kỹ MỤC ĐÍCH trước khi quyết.
- [ ] SAU KHI xong: dựng bảng 5 điểm alpha trong Mục~\ref{sec:cauhinh}
  (thay đoạn hiện tại đang kể "lỗi... phát hiện... sửa"), sửa lại mọi nơi
  trích số 18,43/6,56 (Mục~\ref{sec:ketqua} dòng ~1477-1479, Mục~\ref{sec:xephang}
  dòng ~1683-1689, Kết luận dòng ~2059-2061) cho khớp khung trình bày mới
  (nêu số theo alpha, không nói "đã sửa"). CHƯA quyết được có cần đổi luôn
  cách trình bày ở Mục~\ref{sec:cho2017} (Cho2017 no_kd alpha=1.0, đang
  chờ job 11753) theo cùng khung hay không — hỏi lại khi cả 11753 và
  11754 đều xong.
