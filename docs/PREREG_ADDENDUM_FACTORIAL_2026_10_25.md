# PREREG ADDENDUM — thí nghiệm giai thừa hàm nhân × chiến lược quan hệ (đáp phản biện B, IJRCS)

Ngày lập: 2026-10-25
Người lập: gv_nphuy
Trạng thái: LẬP TRƯỚC KHI CHẠY. Không sửa sau khi có kết quả. Đây là phân tích KHÁM PHÁ,
không thay thế các so sánh đã chốt trong `PREREG_2026_07_30.md` và `PREREG_ADDENDUM_BETA_2026_10_24.md`.

## Bối cảnh
Phản biện B: "Research gap assumes relation-formation strategy and kernel type are separable
without theoretical justification for independence." Bài hiện chỉ đổi từng trục một
(hàm nhân chỉ so ở chiến lược V5), nên chưa kiểm được tương tác hàm nhân × chiến lược.
Đợt cũ `kernel_v234_seeds` (cosine/RBF × V2–V4) bị timeout ở seed 4 và không được dùng.

## Thiết kế
Giai thừa đầy đủ 3 hàm nhân × 4 chiến lược, PhysionetMI, 5 fold, 30 epoch, seed CỐ ĐỊNH 1–5,
β = 0,02 danh nghĩa cho mọi ô (giống thiết kế bảng chính), mọi siêu tham số khác như `HP` trong `run_seeds.py`.

| | dense (V2) | anchor (V3) | global_local (V4) | teacher_guided (V5) |
|---|---|---|---|---|
| lượng tử | `qrd_dense` MỚI | `qrd_anchor` MỚI | `qrd_global_local` MỚI | `qrd_tg_b0.02` đợt β |
| cosine | `ck_cosine_dense` MỚI | `ck_cosine_anchor` MỚI | `ck_cosine_global_local` MỚI | `ck_cosine_tg_b0.02` đợt β |
| RBF | `ck_rbf_dense` MỚI | `ck_rbf_anchor` MỚI | `ck_rbf_global_local` MỚI | `ck_rbf_tg_b0.02` đợt β |

Ba ô V5 dùng lại từ đợt β (job 17704, 17706), cùng mã, cùng môi trường (OMP_NUM_THREADS=8, cùng loại node),
cùng seed. Chín ô mới chạy trong cùng cấu hình môi trường đó. Huấn luyện GPU vẫn không tất định
nên mọi ô đều mang nhiễu chạy lại; điều này được ghi rõ khi báo cáo.

Lưu ý định nghĩa: như ở bảng chính, cosine và RBF đo trên đặc trưng thô 144 chiều, hàm nhân lượng tử
đo trên không gian đã chiếu qua $W_S$/$W_T$. "Hàm nhân" trong thiết kế này là hàm nhân kèm không gian đầu vào của nó.

## Giao thức thống kê (chốt trước)
- Đơn vị: giá trị mỗi seed = mean qua 103 đối tượng (acc có trọng số n trong từng đối tượng), giống các phân tích khác.
- Kiểm định CHÍNH (một): tương tác hàm nhân × chiến lược trong ANOVA hai nhân tố lặp lại theo seed
  (cả hai nhân tố là nội-seed), F với bậc tự do (6, 24), α = 0,05.
- Phụ (mô tả, không hiệu chỉnh đa so sánh): hiệu ứng chính của hàm nhân, hiệu ứng chính của chiến lược;
  với từng chiến lược, chênh lệch lượng tử − cosine và lượng tử − RBF (paired t, CI 95%, d_z).
- Quy tắc diễn giải:
  - p_tương tác ≥ 0,05: "không thấy bằng chứng về tương tác ở mức công suất của thiết kế 5 seed".
    KHÔNG được diễn giải thành "hai trục độc lập" (vắng bằng chứng không phải bằng chứng vắng mặt).
  - p_tương tác < 0,05: báo cáo có tương tác, mô tả kiểu tương tác từ bảng 12 ô, không suy rộng.
- Kèm MDE hậu nghiệm cho các chênh lệch theo từng chiến lược.

## CAM KẾT
- KHÔNG thêm seed, KHÔNG thêm ô, KHÔNG đổi β sau khi nhìn kết quả.
- Báo cáo TOÀN BỘ 12 ô trong bài (phụ lục) và kết quả kiểm định tương tác ở phần chính.
- Kết quả là khám phá, không dùng để đổi kết luận của các so sánh đã chốt.

## Tài nguyên dự kiến
6 ô cổ điển ≈ 2 job × ~5,2 h; 3 ô lượng tử ≈ 3 job × ~5 h; tổng ≈ 25 h GPU, chạy tuần tự.
Output: `results/factorial_2026_10_25/`. Phân tích: `scripts/analyze_factorial.py` (viết trước khi có kết quả).

## Nhật ký vận hành (ghi TRƯỚC khi có kết quả, không đổi thiết kế thống kê)
- 2026-10-25: GPU dùng chung chậm (~770 s/lượt thay vì ~150 s). Job cosine 17755 (timeout 10,5 h) sẽ dừng trước khi xong seed 4.
  Thay các job đang chờ: 17774 `factorial_cosine_s45.pbs` (cosine, seed 4–5, file `factorial_cosine_s45_per_subject.csv`),
  17775 `factorial_rbf_v2.pbs` (walltime 24 h), 17776–17778 `factorial_q{dense,anchor,gl}_v2.pbs` (walltime 16 h).
- Quy tắc gộp chốt trước: ô cosine lấy seed 1–3 từ `factorial_cosine_per_subject.csv` (job 17755) và seed 4–5 từ
  `factorial_cosine_s45_per_subject.csv` (job 17774). Mọi dòng seed ≥ 4 của job 17755 bị bỏ. Đã cài trong `scripts/analyze_factorial.py`.
- Seed, ô thí nghiệm, β, kiểm định chính và quy tắc diễn giải không đổi.
