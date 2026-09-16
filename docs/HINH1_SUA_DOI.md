# Các thay đổi cần thực hiện trên Hình 1 (`paper/figs/image1.png`)

Tài liệu này liệt kê chi tiết những chỗ Hình 1 (`fig:khung`, khung
teacher–student tổng thể) không khớp với công thức/ký hiệu thật đã dùng
trong `paper/body.tex` và trong code thực nghiệm (`scripts/train_all.py`).
Với mỗi điểm: nội dung hiện tại trên hình, lý do sai/không khớp (kèm nguồn
đối chiếu), và nội dung đề xuất thay thế. Không có phần nào ở đây yêu cầu
đổi số liệu hay thuật toán đã chạy — chỉ là sửa lại hình cho khớp đúng những
gì bài báo đã mô tả và đã thực thi.

Bối cảnh: `image1.png` là ảnh raster, không có file nguồn (không có
`.drawio`/`.pptx`/`.svg`) trong repo, nên không thể sửa trực tiếp bằng công
cụ text. Tài liệu này dùng để bạn hoặc công cụ vẽ hình dựng lại/sửa hình
theo đúng nội dung liệt kê dưới đây.

Toàn bộ 4 điểm dưới đây đã được xác minh: hình sai, còn văn bản/code đúng.
Điểm về chiều ma trận ($F_T,F_S,Z_T,Z_S$) đã được xử lý xong ở phía văn bản
(đổi `body.tex` sang đúng quy ước cột như hình), không cần sửa gì thêm trên
hình cho điểm đó.

---

## 1. Hộp chú thích "V1–V5" ở cuối hình (xung đột nhãn nghiêm trọng)

**Hiện tại trên hình**, hộp legend cuối cùng (hàng ngang dưới sơ đồ) ghi:

```
V1: KDBase          L_extra = 0
V2: FeatureKD       L_extra = L_feat
V3: RelationalKD    L_extra = L_rel
V4: QRD (V1-V4)     L_extra = L_QRD
V5: QRD (informative)  L_extra = L_QRD (on S)
```

**Vấn đề:** Nhãn "V1"–"V5" ở đây được dùng để đánh số 5 mức ablation loại
tri thức chưng cất. Nhưng trong toàn bộ phần còn lại của bài — Hình 2
(`image2.png`), Thuật toán 1, Mục 3.4 (`sec:bienthe`), Bảng 5/6/9/10 — nhãn
"V1"–"V5" lại chỉ 5 biến thể xây **ma trận quan hệ lượng tử bên trong nhánh
QRD**:

| Nhãn (đúng, dùng xuyên suốt bài) | Ý nghĩa |
|---|---|
| V1 Dense | quan hệ dày đặc, giảm chiều tất định |
| V2 Dense | quan hệ dày đặc, phép chiếu học được |
| V3 Anchor | quan hệ thưa dựa trên tập neo |
| V4 Anchor+kNN | kết hợp quan hệ toàn cục và cục bộ |
| V5 Guided | lựa chọn quan hệ có định hướng theo teacher |

Cả 5 biến thể này **đều dùng $\mathcal{L}_{\mathrm{QRD}}$**, không có biến
thể nào tương ứng riêng lẻ với KDBase/FeatureKD/RelationalKD. Vì vậy câu
"V4: QRD (V1-V4)" trên hình đặc biệt gây hiểu nhầm: nó dùng ký hiệu "V4" để
chỉ *cả nhóm* bốn biến thể V1–V4, trong khi khắp nơi khác trong bài "V4"
luôn chỉ nghĩa là *một* biến thể cụ thể duy nhất (Anchor+kNN).

**Đề xuất sửa:** bỏ hẳn tiền tố "V1:"..."V5:" khỏi hộp legend này, chỉ giữ
tên cấu hình. Nội dung mới:

```
KDBase                         L_extra = 0
FeatureKD                      L_extra = L_feat
RelationalKD                   L_extra = L_rel
QRD (biến thể V1–V4)           L_extra = L_QRD  (I = quan hệ trên q mẫu cố định)
QRD (biến thể V5 Guided)       L_extra = L_QRD  (I = quan hệ trên tập S do teacher chọn)
```

Ghi chú thêm nên có trong hình hoặc caption: "V1–V4 và V5 Guided là 5 biến
thể xây dựng $\mathcal{I}$ trong nhánh QRD, xem Hình [số hiệu của Hình 2]."
— để người đọc không nhầm hộp này với Hình 2.

---

## 2. Nhãn độ đo "Disagreement $d_i$" trong khối V5 (sai về bản chất thuật toán)

**Hiện tại trên hình:** ô "Disagreement $d_i$" ghi chú "($\ell_2$
distance)".

**Vấn đề:** Đây không phải độ đo thật đã dùng. `body.tex` \eqref{eq:js}
(dòng ~1096–1101) định nghĩa $d_i$ bằng **phân kỳ Jensen–Shannon**:

$$d_i = \tfrac{1}{2}\mathrm{KL}(p_T \| m_i) + \tfrac{1}{2}\mathrm{KL}(p_S \| m_i), \qquad m_i = \tfrac12(p_T+p_S)$$

và văn bản còn giải thích rõ lý do *không* dùng $L_2$: "So với chuẩn $L_2$,
phân kỳ Jensen–Shannon có ưu điểm là đối xứng, bị chặn, và phù hợp với việc
so sánh hai phân bố xác suất." Đối chiếu code thật, `scripts/train_all.py`
dòng 223 (`_js_divergence`) xác nhận đây đúng là công thức đã chạy để tạo
ra số liệu V5 Guided trong bài — không có phiên bản $\ell_2$ nào từng được
dùng.

**Đề xuất sửa:** đổi nhãn trong ô thành:

```
Disagreement d_i
(Jensen–Shannon divergence)
```

---

## 3. Công thức điểm số $s_i$ trong khối V5 (sai công thức)

**Hiện tại trên hình:** `Score s_i = u_i + λ·d_i`.

**Vấn đề:** Công thức thật trong bài, \eqref{eq:score} (dòng ~1109–1113):

$$s_i = w_e\,u_i + w_d\,d_i, \qquad w_e = w_d = 0{,}5$$

không có hệ số $\lambda$ nào — cả hai số hạng đều có trọng số cố định
$0{,}5$, không phải một hệ số $\lambda$ chỉ nhân riêng $d_i$. Đối chiếu
`scripts/train_all.py` dòng 230 và dòng 366
(`entropy_weight=0.5, disagreement_weight=0.5`) xác nhận đây là giá trị đã
dùng thật, khớp với Bảng cấu hình (`tab:cauhinh`, hàng "$w_e$, $w_d$" =
"0,5 và 0,5"). Không có $\lambda$ trong toàn bộ code hay bài.

**Đề xuất sửa:** đổi công thức trong ô thành:

```
Score  s_i = w_e·u_i + w_d·d_i,  w_e = w_d = 0,5
```

---

## 4. Công thức hàm mất mát tổng ở góc dưới hình (đơn giản hoá làm mất thông tin, mâu thuẫn với Bảng cấu hình)

**Hiện tại trên hình:**

$$\mathcal{L}_{total} = \alpha\mathcal{L}_{CE} + (1-\alpha)\mathcal{L}_{KD} + \beta\mathcal{L}_{extra}, \qquad \mathcal{L}_{extra} \in \{\mathcal{L}_{feat}, \mathcal{L}_{rel}, \mathcal{L}_{QRD}\}$$

**Vấn đề:** Công thức thật, \eqref{eq:total} (dòng ~739–744):

$$\mathcal{L} = \alpha\,\mathcal{L}_{\mathrm{CE}} + (1-\alpha)\,\mathcal{L}_{\mathrm{KD}} + \gamma_{f}\,\mathcal{L}_{\mathrm{feat}} + \gamma_{r}\,\mathcal{L}_{\mathrm{rel}} + \beta\,\mathcal{L}_{\mathrm{QRD}}$$

có **ba hệ số riêng biệt** ($\gamma_f$, $\gamma_r$, $\beta$), không phải một
$\beta$ dùng chung cho cả ba loại "extra". Bảng~\ref{tab:cauhinh} báo cáo
ba giá trị khác nhau và có ý nghĩa khác nhau: $\gamma_f$ (FeatureKD) $=
1{,}0$, $\gamma_r$ (RelationalKD) $= 1{,}0$ (cố định, không quét), còn
$\beta$ (QRD) $= 0{,}02$ là hệ số **được quét độ nhạy riêng**
($\beta \in \{0{,}01; 0{,}05\}$ cho V5 Guided, xem dòng ~1355–1358 của
`body.tex`). Gộp chung thành một $\beta$ trên hình xoá mất sự phân biệt có
thật và quan trọng này.

**Đề xuất sửa:** đổi công thức trong hình thành:

```
L_total = α·L_CE + (1-α)·L_KD + γ_f·L_feat + γ_r·L_rel + β·L_QRD

trong đó hệ số của thành phần không thuộc cấu hình đang xét = 0.
```

Nếu muốn giữ hộp legend gọn (không liệt kê hết 3 ký hiệu mỗi dòng), có thể
thay bằng bảng hệ số kích hoạt cho từng cấu hình, khớp đúng Bảng~\ref{tab:cauhinh}:

| Cấu hình | $\gamma_f$ | $\gamma_r$ | $\beta$ |
|---|---|---|---|
| KDBase | 0 | 0 | 0 |
| FeatureKD | 1,0 | 0 | 0 |
| RelationalKD | 0 | 1,0 | 0 |
| QRD (V1–V4) | 0 | 0 | 0,02 |
| QRD (V5 Guided) | 0 | 0 | 0,02 (quét 0,01 / 0,05) |

---

## 5. (Phụ, mức độ thấp) Ký hiệu $\phi(\cdot)$ trong khối "Projection / Encoding"

**Hiện tại trên hình:** hộp "Projection / Encoding $\phi(\cdot)$" (phi
thường) ngay trước hộp "Quantum Mapping (PQC)".

**Vấn đề nhỏ:** `body.tex` dùng $\Phi(\cdot)$ (Phi hoa) riêng cho phép mã
hóa góc quay vào mạch lượng tử ở \eqref{eq:layer}–\eqref{eq:state}, khác
với phép chiếu tuyến tính $W$ + chặn góc bằng tanh ở \eqref{eq:angles}
($a(x_i) = \pi\tanh(Wf(x_i))$). Hộp trên hình gộp cả hai bước ($W$+tanh và
$\Phi$) làm một, nên **không sai về nội dung**, nhưng ký hiệu $\phi$ thường
dễ bị đọc nhầm là chính $\Phi(\cdot)$ đã dùng cho một phép toán khác trong
văn bản.

**Đề xuất sửa (không bắt buộc):** đổi nhãn hộp thành:

```
Projection (W) + Angle encoding Φ(·)
```

hoặc giữ nguyên như hiện tại nếu muốn ưu tiên gọn nhẹ cho sơ đồ tổng quan —
đây là điểm ưu tiên thấp nhất trong 5 điểm, có thể bỏ qua nếu thời gian
sửa hình hạn chế.

---

## Tóm tắt mức độ ưu tiên

1. **Bắt buộc, nghiêm trọng** — Mục 1: xung đột nhãn V1–V5.
2. **Bắt buộc** — Mục 2: nhãn $d_i$ sai bản chất thuật toán ($\ell_2$ →
   Jensen–Shannon).
3. **Bắt buộc** — Mục 3: công thức $s_i$ sai ($\lambda$ → $w_e, w_d = 0,5$).
4. **Bắt buộc** — Mục 4: công thức $\mathcal{L}_{total}$ làm mất thông tin,
   mâu thuẫn Bảng~\ref{tab:cauhinh}.
5. **Tuỳ chọn** — Mục 5: ký hiệu $\phi$ vs $\Phi$.

Không cần sửa gì thêm về chiều ma trận $F_T,F_S,Z_T,Z_S$ — phía văn bản
(`body.tex`) đã được cập nhật để khớp đúng quy ước xếp theo cột như hình
hiện tại.
