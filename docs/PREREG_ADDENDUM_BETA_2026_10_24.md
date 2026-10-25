# PREREG ADDENDUM — kiểm tra tính vững theo β (đáp phản biện B, IJRCS)

Ngày lập: 2026-10-24
Người lập: gv_nphuy
Gốc: `docs/PREREG_2026_07_30.md`, mục "Mở rộng kiểm tra tính vững (TÙY CHỌN, chốt trước nếu làm)".
Trạng thái: LẬP TRƯỚC KHI CHẠY. Không sửa sau khi có kết quả. Smoke test (1 seed,
1 fold) chỉ dùng để kiểm tra kỹ thuật, không dùng để đổi bất kỳ mục nào dưới đây.

## Bối cảnh
Phản biện B cho rằng β = 0,02 dùng chung cho ba hàm nhân là không công bằng, vì
Bảng 8 (chẩn đoán gradNormS, fold 0, 5 epoch đầu) cho thấy chuẩn L2 gradient mà
β·L_QRD tạo lên student chênh lệch lớn giữa các hàm nhân:
cosine 7,54e-5 (1×), RBF 1,47e-3 (≈20×), lượng tử 1,51e-2 (≈200×).
Do gradient của β·L_QRD tuyến tính theo β, có thể cân độ lớn giám sát hiệu dụng
bằng cách nhân β của hàm nhân cổ điển với tỉ lệ đo được.

## Hai nhánh thí nghiệm
### Nhánh M — cân độ lớn gradient (so sánh CHÍNH của phụ lục)
Giữ lượng tử ở β = 0,02. Nâng β của hàm nhân cổ điển để gradient ban đầu ngang lượng tử:
- cosine: β = 0,02 × (1,51e-2 / 7,54e-5) ≈ 0,02 × 200 = **4,0**
- RBF:    β = 0,02 × (1,51e-2 / 1,47e-3) ≈ 0,02 × 10,3 ≈ **0,2**
Hai hằng số này chốt ngay bây giờ từ Bảng 8, không hiệu chỉnh lại sau smoke test.

### Nhánh S — lưới β đã nêu trong pre-reg gốc
β ∈ {0,1; 0,5} cho cả ba hàm nhân dưới cùng chiến lược V5 (teacher-guided).
Cùng với số liệu đã có (lượng tử ở 0,01/0,02/0,05; cosine và RBF ở 0,02) tạo thành
đường liều–đáp ứng theo β cho từng hàm nhân.

## Danh sách cấu hình chạy mới (8)
| tag | method | β |
|---|---|---|
| ck_cosine_tg_b4.0 | ck_cosine_tg | 4,0 (nhánh M) |
| ck_rbf_tg_b0.2 | ck_rbf_tg | 0,2 (nhánh M) |
| ck_cosine_tg_b0.1 | ck_cosine_tg | 0,1 |
| ck_cosine_tg_b0.5 | ck_cosine_tg | 0,5 |
| ck_rbf_tg_b0.1 | ck_rbf_tg | 0,1 |
| ck_rbf_tg_b0.5 | ck_rbf_tg | 0,5 |
| qrd_tg_b0.1 | qrd_teacher_guided | 0,1 |
| qrd_tg_b0.5 | qrd_teacher_guided | 0,5 |

Mọi siêu tham số khác giữ như `HP` trong `scripts/run_seeds.py`. PhysionetMI, 5 fold,
30 epoch, seed CỐ ĐỊNH 1,2,3,4,5 (giống pre-reg gốc).

## Số liệu tham chiếu dùng lại (không chạy lại)
- lượng tử β = 0,02: `results/qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv`, tag `qrd_teacher_guided`
- cosine/RBF β = 0,02: `results/seeds2_per_subject.csv`, tag `ck_cosine_tg`, `ck_rbf_tg`
- KDBase: `results/seeds_per_subject.csv`, tag `kd_base`
Điều kiện dùng lại: smoke test chạy lại lượng tử β = 0,02 và cosine β = 0,02 ở
seed 1 fold 0 phải cho đúng accuracy cũ (chênh ≤ 0,01 pp). Nếu không đạt, chạy lại
cả nhánh tham chiếu trong cùng phiên bản code rồi mới so sánh, và ghi rõ lý do.

## Giao thức thống kê (giống pre-reg gốc)
- Đơn vị thống kê: SUBJECT. Gộp: mean có trọng số n trong từng (tag, seed, subject),
  rồi mean qua subject, được một giá trị cho mỗi seed.
- So sánh CHÍNH (một, chốt trước): lượng tử β = 0,02 VS cosine β = 4,0.
  Paired t-test trên 5 seed chung, α = 0,05 hai phía, CI 95%, Cohen's d_z.
- Biên tương đương δ = 0,5 pp. CI nằm trọn trong [−0,5; +0,5] thì kết luận TƯƠNG ĐƯƠNG.
- Quy tắc kết luận giống mục Go/No-Go của pre-reg gốc. p > 0,05 và CI vượt biên
  thì kết luận "không đủ dữ liệu", không kết luận theo chiều nào. p trong [0,05; 0,10]
  ghi nhận là KHÔNG có ý nghĩa.
- So sánh phụ (mô tả, không hiệu chỉnh đa so sánh, không dùng làm claim chính):
  lượng tử β = 0,02 VS RBF β = 0,2; từng cấu hình mới VS KDBase; bảng liều–đáp ứng.

## CAM KẾT
- KHÔNG thêm seed, KHÔNG thêm giá trị β ngoài danh sách trên sau khi nhìn kết quả.
- Báo cáo TOÀN BỘ 8 cấu hình trong bài hoặc phụ lục, kể cả cấu hình bất lợi.
- KHÔNG dùng nhánh S để chọn β "tốt nhất" cho từng hàm nhân rồi so sánh lại.
- Nếu thứ tự giữa các hàm nhân đổi theo β, báo cáo đúng như vậy. Đó là kết quả.
- Hạn chế ghi sẵn: tỉ lệ cân bằng đo ở fold 0, 5 epoch đầu, có thể trôi trong quá
  trình huấn luyện. Nhánh M cân độ lớn gradient lúc đầu, không bảo đảm cân suốt quá trình.

## NHẬT KÝ THỰC HIỆN (chỉ ghi lại diễn biến, không sửa các mục chốt ở trên)
- 2026-10-24, smoke job 17679: lỗi do đặt QRD_N_FOLDS=1 (init_dataset mất split val).
  Sửa bằng biến mới QRD_FOLDS (chỉ chọn fold chạy, vẫn chia 5 fold). Không ảnh hưởng kết quả.
- 2026-10-24, smoke job 17683 (seed 1, fold 0): kỹ thuật ĐẠT (rc=0, 80 dòng, không NaN).
  Tái lập KHÔNG ĐẠT: cosine β=0,02 cho 81,67 (cũ 82,67), lượng tử β=0,02 cho 80,67 (cũ 81,11).
  Nguyên nhân: cudnn.benchmark=True không tất định, và job mới giới hạn OMP_NUM_THREADS=8
  (job cũ dùng mặc định toàn bộ lõi node). Theo mục "Điều kiện dùng lại", chạy lại TOÀN BỘ
  nhánh tham chiếu trong cùng cấu hình: lượng tử β=0,02, cosine β=0,02, RBF β=0,02 và KDBase.
  Mọi so sánh của phụ lục chỉ dùng số liệu của đợt chạy mới này. Số liệu smoke không dùng trong phân tích.

## KẾT QUẢ (2026-10-25, ghi sau khi chạy; không sửa các mục chốt ở trên)
Job 17704–17709 xong, rc=0, đủ dòng, không NaN. Phân tích: `scripts/analyze_beta_addendum.py`
→ `results/beta_robust_2026_10_24/analysis_beta_addendum.txt` (+ `_per_seed.csv`).
Kiểm cách tính: chạy cùng script trên số liệu cũ cho đúng các số trong bản thảo (81,12 / 81,63 / 81,61 / 81,49).

**So sánh CHÍNH** lượng tử β=0,02 − cosine β=4,0: chênh −0,16 pp, CI 95% [−0,514; +0,195], p = 0,279, d_z = −0,56.
Theo quy tắc chốt trước: p > 0,05 và CI vượt biên ±0,5 pp (cận dưới −0,514 vượt −0,5 khoảng 0,014 pp)
→ **KHÔNG ĐỦ DỮ LIỆU**, không kết luận theo chiều nào. Không được làm tròn thành "tương đương".

So sánh phụ (mô tả, không hiệu chỉnh đa so sánh):
- lượng tử 0,02 − RBF 0,2: +0,13 pp, CI [−0,45; +0,72], p = 0,56.
- Cùng β danh nghĩa 0,02 trong đợt mới: lượng tử − cosine −0,06 pp (p = 0,85), lượng tử − RBF −0,07 pp (p = 0,71).
- So với KDBase (đợt mới): 10/11 cấu hình p > 0,05. Riêng cosine β=0,5 −0,38 pp, p = 0,044 (một trong 11 phép so sánh
  không hiệu chỉnh, kỳ vọng khoảng 0,55 dương tính giả ở α = 0,05). Không dùng làm claim.
- Liều–đáp ứng: mọi cấu hình nằm trong 81,32–81,87%, không thấy xu hướng theo β ở hàm nhân nào.

Đối chiếu tái lập (đợt mới − số liệu cũ trong bản thảo, cùng cấu hình, cùng seed 1–5):
lượng tử +0,33; cosine −0,12; RBF −0,09; KDBase +0,22 pp. Nguyên nhân như đã ghi ở Nhật ký
(cudnn.benchmark không tất định, số luồng CPU khác). Độ lệch giữa hai lần chạy cùng cấu hình có cùng cỡ với
khác biệt giữa các phương pháp. Khoảng cách lượng tử − cosine −0,51 pp trong bản thảo còn −0,06 pp khi chạy lại cùng β.
