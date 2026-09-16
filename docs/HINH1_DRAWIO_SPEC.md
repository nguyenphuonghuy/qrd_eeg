# Bản đặc tả dựng lại Hình 1 bằng draw.io

Mục đích: dựng lại `fig:khung` (khung teacher–student QRD) hoàn toàn thủ
công trong draw.io (không dùng công cụ AI sinh ảnh), theo đúng nội dung đã
được đối chiếu và xác nhận khớp với `body.tex` qua nhiều vòng kiểm tra.
Tài liệu này là bản đặc tả đầy đủ — người dựng hình không cần đoán lại nội
dung, chỉ cần theo đúng bố cục/màu/font/nội dung liệt kê dưới đây.

---

## 1. Canvas và xuất file

- Tỉ lệ khung: theo ảnh hiện tại (1536×1024 px, tỉ lệ ~3:2), giữ nguyên tỉ
  lệ này để không phải đổi `width=\linewidth` trong `body.tex`.
- Vẽ ở kích thước lớn trong draw.io (ví dụ khung 1600×1050 pt) rồi xuất
  **PDF vector** (khuyến nghị, không bao giờ mờ khi in) hoặc PNG ở
  **300 DPI trở lên, tối thiểu 3000 px chiều ngang** nếu bắt buộc phải
  dùng raster.
- Xuất qua **File → Export as → PDF** (chọn "Crop to selection" nếu chỉ
  vẽ trong một khung) hoặc **PNG** với tuỳ chọn "Zoom 300%" trở lên trước
  khi export để tránh răng cưa ở chữ nhỏ.

---

## 2. Nguyên tắc phong cách (flat, tối giản — tránh "trông như AI vẽ")

- **Không** dùng gradient fill, **không** đổ bóng (drop shadow), **không**
  hiệu ứng 3D/glossy cho bất kỳ khối nào (kể cả khối "backbone" — vẽ bằng
  các hình chữ nhật xếp chồng phẳng màu đơn sắc, không tô 3D).
- Viền khối: độ dày đều nhau, **2px**, bo góc nhẹ **rounded corner
  arcSize ≈ 6–8** (không bo tròn quá, không vuông gắt).
- Toàn bộ mũi tên: nét đơn, độ dày **1.5–2px**, đầu mũi tên kiểu "classic"
  đơn giản (không mũi tên 3D/block).
- Nền tổng thể: trắng tuyệt đối, không texture.
- Khoảng cách giữa các khối đều nhau, căn lưới (dùng lưới draw.io, snap to
  grid 10px) để các khối thẳng hàng — đây là điểm dễ lộ "vẽ tay ẩu" nhất
  nếu không căn.

---

## 3. Bảng màu (đơn sắc theo nhóm chức năng, dùng xuyên suốt)

| Nhóm | Viền (border) | Nền (fill) | Dùng cho |
|---|---|---|---|
| Xanh dương | `#1565C0` | `#E3F2FD` | Teacher Network, KD Base, tiêu đề "Teacher Network (fixed)" |
| Xanh lá | `#2E7D32` | `#E8F5E9` | Student Network, Feature-level KD, Deployment (Inference), tiêu đề tương ứng |
| Cam | `#E65100` | `#FFF3E0` | Classical Relational KD |
| Tím | `#6A1B9A` | `#F3E5F5` | Quantum Relational Distillation (QRD), $\mathcal{L}_{QRD}$, hộp V5-only, 2 hộp legend cuối cùng |
| Xanh dương nhạt (khung ngoài) | `#1565C0` | trắng/không tô | Khung bao "Distillation Modules", khung bao "Teacher/Student" phía trái |
| Tím nhạt (khung ngoài) | `#7B1FA2` | trắng/không tô | Khung bao "Training Procedure", "Deployment" |
| Xám chữ | — | `#212121` | Toàn bộ text thường |
| Xám mũi tên | — | `#424242` | Mũi tên luồng dữ liệu chính (nét liền, đen/xám đậm) |
| Xanh lá (nét đứt) | — | `#2E7D32` | Mũi tên "Update student parameters" (nét đứt xanh lá) |
| Đen (nét đứt) | — | `#212121` | Mũi tên "Backpropagation" (nét đứt đen) |

Không thêm màu nào ngoài bảng trên. Mỗi khối chỉ dùng đúng 1 màu viền + 1
màu nền tương ứng theo nhóm.

---

## 4. Font và cách gõ công thức toán

- Font chữ thường (nhãn khối, mô tả): **Helvetica** hoặc **Arial**, sans-serif.
  - Tiêu đề khối lớn (vd "Teacher Network (fixed)"): đậm (bold), 16–18pt.
  - Tiêu đề khối con (vd "(i) KD Base (logits-level)"): đậm, 13–14pt.
  - Nhãn thường trong khối: thường (regular), 11–12pt.
- **Công thức toán** ($\mathcal{L}_{QRD}$, $\mathbb{R}^{N\times N}$,
  $w_e = w_d = 0{,}5$, v.v.): draw.io hỗ trợ gõ LaTeX trực tiếp trong nhãn
  qua MathJax. Bật tính năng này ở **Extras → Mathematical Typesetting**
  (tick chọn), sau đó gõ công thức trong dấu `$...$` ngay trong ô nhãn của
  khối — draw.io sẽ tự render đúng ký hiệu toán thay vì phải gõ tay bằng
  ký tự Unicode xấp xỉ. Toàn bộ công thức liệt kê ở Mục 5 dưới đây viết
  sẵn theo cú pháp LaTeX để dán trực tiếp vào draw.io theo cách này.

---

## 5. Nội dung chi tiết từng khối (đã xác nhận khớp `body.tex`)

Bố cục tổng thể chia 4 cột chính theo chiều ngang: **(A) Input/Teacher/
Student** (trái) — **(B) Distillation Modules** (giữa, khối lớn nhất) —
**(C) Loss tổng + 2 hộp legend** (dưới khối B, trải ngang từ trái sang
giữa) — **(D) Training Procedure / Deployment** (phải).

### (A) Cột trái

**Khối "Input"** (hình chữ nhật viền xám/đen nhạt, không cần màu nhóm):
```
Input
EEG-MI mini-batch
X = {x_i}_{i=1}^N
(C channels × T time)
Batch size: N
```
Mũi tên đen đi ra hai nhánh: lên "Teacher Network", xuống "Student Network".

**Khối "Teacher Network (fixed)"** (viền xanh dương `#1565C0`, tiêu đề
xanh dương đậm):
- Backbone: hình 3–4 hình chữ nhật dẹt xếp cạnh nhau kiểu bậc thang, **tô
  phẳng 1 màu xanh dương** (không gradient/3D), nhãn dưới: `Backbone (e.g., Ensemble-MI)`.
- Mũi tên sang khối tròn nhỏ xếp dọc, nhãn `Global Pooling`.
- Từ Global Pooling tách 2 nhánh:
  - `Logits (softmax)`, `$Z_T \in \mathbb{R}^{C \times N}$`, vẽ vài cột
    thanh (bar) nhỏ minh hoạ.
  - `Features`, `$F_T \in \mathbb{R}^{d \times N}$`, vẽ lưới ô vuông nhỏ
    minh hoạ vector đặc trưng.

**Khối "Student Network (trainable)"** (viền xanh lá `#2E7D32`, tiêu đề
xanh lá đậm) — bố cục giống hệt khối Teacher, đổi:
- Backbone nhãn: `Backbone (e.g., EEGNet)`.
- `Logits (softmax)`, `$Z_S \in \mathbb{R}^{C \times N}$`.
- `Features`, `$F_S \in \mathbb{R}^{d \times N}$`.
- Có thêm dấu trừ nhỏ (`−`) cạnh Global Pooling của Student, nối bằng nét
  đứt xanh lá xuống khối "Update student parameters $\theta_S$" ở dưới
  cùng cột trái.

**Khối "Ground-truth labels"** (dưới, viền xám/tím nhạt):
```
Ground-truth labels
y = {y_i}_{i=1}^N ∈ {1,…,C}^N
① ② ③ ⋯ Ⓒ
```
Mũi tên tím đi từ khối này lên khối $\mathcal{L}_{CE}$ ở giữa-dưới.

**Khối "Update student parameters $\theta_S$ (teacher parameters fixed)"**:
hình chữ nhật viền xám nhạt, nối bằng mũi tên **nét đứt xanh lá** hai
chiều với đáy Student Network (cập nhật gradient) và nối bằng mũi tên nét
đứt đen từ khối "Total Training Objective" (đường "Backpropagation" vòng
từ phải sang, xem Mục C).

### (B) Khối lớn "Distillation Modules (training-time only)"

Khung ngoài viền xanh dương nhạt `#1565C0`, không tô nền (hoặc nền
`#FAFAFA` rất nhạt), tiêu đề đậm ở trên cùng: `Distillation Modules
(training-time only)`. Bên trong xếp dọc 4 khối con, mỗi khối là một hàng
ngang riêng:

**(i) KD Base (logits-level)** — viền xanh dương `#1565C0`, nền `#E3F2FD`:
```
[Z_T (teacher logits)]  [Z_S (student logits)]
        ↓                       ↓
   Temperature T, Softmax  (vẽ 2 đường phân bố chuông chồng nhau, 1 nét
   liền xanh, 1 nét đứt xanh lá)
        ↓
   [L_KD (KL Divergence)]
```

**(ii) Feature-level KD** — viền xanh lá `#2E7D32`, nền `#E8F5E9`:
```
[F_T (teacher features)]  [F_S (student features)]
        ↓
   Alignment in feature space ℝ^d
   (vẽ vài chấm xanh dương → vài chấm xanh lá, mũi tên cong nhỏ nối từng
   cặp chấm gần nhau minh hoạ alignment)
        ↓
   [L_feat (MSE)]
```

**(iii) Classical Relational KD (Euclidean / Cosine)** — viền cam
`#E65100`, tiêu đề chữ cam, nền `#FFF3E0`:
```
[F_T (teacher features)]         [F_S (student features)]
        ↓                                ↓
   Relation matrix (classical)
        ↓                                ↓
   $R_T^{(C)} \in \mathbb{R}^{N\times N}$   $R_S^{(C)} \in \mathbb{R}^{N\times N}$
   (vẽ 2 lưới ô vuông nhỏ màu xanh dương/xanh lá minh hoạ ma trận)
        ↓ (2 mũi tên hội tụ)
   [L_rel (Frobenius Norm)]
```

**(iv) Quantum Relational Distillation (QRD)** — viền tím `#6A1B9A`, tiêu
đề chữ tím, nền `#F3E5F5`. Đây là khối phức tạp nhất, chia 2 hàng con:

Hàng trên (song song teacher/student):
```
[F_T (teacher features)] → Projection/Encoding $\phi(\cdot)$ →
   Quantum Mapping (PQC) [vẽ mạch lượng tử cách điệu: 4 đường ngang song
   song = 4 qubit, vài ô vuông nhỏ trên mỗi đường minh hoạ cổng lượng tử]
   → Quantum relation matrix $R_T^{(Q)} \in \mathbb{R}^{N\times N}$

[F_S (student features)] → Projection/Encoding $\phi(\cdot)$ →
   (cùng khối Quantum Mapping — vẽ 2 mũi tên từ 2 nhánh Projection cùng đi
   vào 1 khối PQC chung, thể hiện $\theta$ dùng chung cho cả hai nhánh)
   → Quantum relation matrix $R_S^{(Q)} \in \mathbb{R}^{N\times N}$
```
Cả 2 ma trận quan hệ → mũi tên hội tụ → `[L_QRD (Frobenius Norm)]`.

Hàng dưới, khung con viền tím nét đứt, nhãn tiêu đề: `Variant V5 only
(informative sample selection)`:
```
Inputs: $Z_T, Z_S$
   ↓
[Uncertainty $u_i$ (teacher entropy)]  +  [Disagreement $d_i$
(Jensen–Shannon divergence)]
   ↓
[Score $s_i = w_e u_i + w_d d_i$,  $w_e = w_d = 0{,}5$]
   ↓
[Top-K selection $S$ (informative samples)]
   ↓
[Compute QRD on selected samples $S$]  → (mũi tên nét đứt tím lên khối
$R_T^{(Q)}, R_S^{(Q)}$ ở hàng trên, thể hiện $S$ thay cho $q$ mẫu cố định)
```

### (C) Hàng loss thành phần + Total Training Objective + 2 hộp legend

Ngay dưới khối B, 5 khối nhỏ xếp ngang, mỗi khối 1 màu theo nhóm tương
ứng, có mũi tên đi thẳng xuống khối "Total Training Objective":

```
[L_CE (Cross-Entropy)      [L_KD          [L_feat (from   [L_rel (from    [L_QRD (from
 Input: Z_S, y]  (tím)      (from KD Base)] Feature KD)     Relational KD)  QRD variants)
                            (xanh dương)    (optional)]     (optional)]     (optional)]
                                            (xanh lá)       (cam)           (tím)
```
Mỗi khối có mũi tên đen đi thẳng xuống, **chạm và cắm vào viền trên** của
khối "Total Training Objective" (không dừng ở một đường tách rời — lỗi đã
gặp ở bản trước, chú ý khi vẽ).

**Khối "Total Training Objective (configured by experiment)"** (viền xám
đậm, nền trắng/xám rất nhạt, khối to nằm ngang):
```
$\mathcal{L}_{total} = \alpha\mathcal{L}_{CE} + (1-\alpha)\mathcal{L}_{KD}
  + \gamma_f\mathcal{L}_{feat} + \gamma_r\mathcal{L}_{rel} + \beta\mathcal{L}_{QRD}$

(Set $\gamma_f$, $\gamma_r$, or $\beta$ = 0 when the corresponding
component is not used)
```
Hai mũi tên nét đứt đi ra từ khối này:
- Sang trái, nét đứt xanh lá, tới khối "Update student parameters $\theta_S$".
- Sang phải, nét đứt đen, nhãn `Backpropagation`, vòng lên/về phía trái
  (thể hiện lan truyền ngược cập nhật student).

**Hai hộp legend dưới cùng**, đặt cạnh nhau theo hàng ngang, viền tím nét
đứt `#6A1B9A`, tiêu đề tím đậm:

Hộp trái, `Ablation settings (loss-level)`:
```
KDBase            FeatureKD         RelationalKD      QRD (V1–V4)              QRD (V5 Guided)
$\mathcal{L}_{extra}=0$  $\mathcal{L}_{extra}=\mathcal{L}_{feat}$  $\mathcal{L}_{extra}=\mathcal{L}_{rel}$  $\mathcal{L}_{extra}=\mathcal{L}_{QRD}$  $\mathcal{L}_{extra}=\mathcal{L}_{QRD}$
                                                        ($\mathcal{I}$: relation on    ($\mathcal{I}$: relation on
                                                         fixed $q$ samples)    teacher-selected $S$)
```
5 ô con xếp ngang trong hộp, mỗi ô viền mảnh xám nhạt, không cần tô màu
riêng (chỉ viền ngoài hộp lớn màu tím).

Hộp phải, `QRD relation construction variants (see Fig. 2)`:
```
V1 Dense              V2 Dense           V3 Anchor            V4 Anchor+kNN        V5 Guided
(deterministic         (learned           (anchor-based        (anchor + kNN        (teacher-guided
 dimensionality         projection)        sparse relation)     hybrid relation)     informative relation)
 reduction)
```
5 ô con xếp ngang, cùng kiểu viền mảnh xám nhạt như hộp trái.

### (D) Cột phải

**Khối "Training Procedure"** (viền tím `#6A1B9A`, tiêu đề tím đậm), 4
bước xếp dọc, mỗi bước 1 khối chữ nhật nối bằng mũi tên đen:
```
1. Forward pass through teacher and student
2. Compute the losses activated by the selected variant
3. Form the total training objective
4. Backpropagate and update the student only
```
Dưới cùng, 1 dòng chú thích chữ tím nghiêng, khung viền tím nhạt:
```
Quantum module (QRD) is used only during training.
```

**Khối "Deployment (Inference)"** (viền xanh lá `#2E7D32`, tiêu đề xanh
lá đậm — **không có icon** cạnh tiêu đề, chỉ chữ), 3 khối dọc nối mũi tên
đen:
```
EEG-MI input (single trial or stream)
   [vẽ 1 đường sóng tín hiệu nhỏ minh hoạ]
        ↓
Trained Student (used alone)
   [vẽ backbone rút gọn 2–3 khối xanh lá, không có phần Teacher]
        ↓
Predicted class (Softmax output)
   [vẽ vài thanh bar nhỏ xanh lá]
```

---

## 6. Danh sách kiểm tra trước khi thay vào bài

Sau khi dựng xong trong draw.io, đối chiếu lại với `body.tex` trước khi
xuất file và thay `figs/image1.png`:

- [ ] $F_T, F_S \in \mathbb{R}^{d\times N}$ dùng **chung một** ký hiệu
      $d$ (không phải $d_T$, $d_S$).
- [ ] $Z_T, Z_S \in \mathbb{R}^{C\times N}$.
- [ ] Backbone teacher ghi đúng "Ensemble-MI" (viết hoa cả M và I).
- [ ] $d_i$ ghi đúng "Jensen–Shannon divergence", không phải $\ell_2$.
- [ ] $s_i = w_e u_i + w_d d_i$, $w_e = w_d = 0{,}5$ — không có $\lambda$.
- [ ] $\mathcal{L}_{total}$ có đủ 3 hệ số riêng $\gamma_f, \gamma_r, \beta$
      (không gộp chung một $\beta$).
- [ ] Hộp "Ablation settings" và hộp "QRD relation construction variants"
      tách riêng, không dùng chung nhãn "V1"–"V5" cho hai nghĩa khác nhau.
- [ ] Không có icon nào trong tiêu đề bất kỳ khối nào.
- [ ] Không có gradient/đổ bóng/hiệu ứng 3D ở bất kỳ khối nào.
- [ ] Xuất PDF vector hoặc PNG ≥ 300 DPI (≥ 3000 px chiều ngang).
- [ ] Sau khi thay file, biên dịch `tectonic main.tex` 2 lần, kiểm tra
      `grep -i "undefined\|^! "` trên log không ra kết quả.
