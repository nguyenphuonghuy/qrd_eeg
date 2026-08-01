# DESIGN — qrd_eeg

| Item | Value |
|---|---|
| Project | qrd_eeg (Quantum Relational Distillation for MI-EEG) |
| Version | 1.0 (design freeze trước khi chạy) |
| Status | Approved — chờ chuyển sang điều chỉnh code |
| Repo bên thứ ba | external/Ensemble-MI @ b7d8e9f8 (patched: t_dur=3.0, n_out_time=9) |

Tài liệu này ĐÓNG BĂNG thiết kế thí nghiệm. Mục tiêu: một lần chạy ma trận ra
ĐỦ mọi bảng/hình cho paper, không phải chạy lại để lấy thêm số/hình.

---

## 1. Định vị & chiến lược (2 pha)

Bối cảnh trung thực: dữ liệu thật (notebook cũ) cho thấy QRD ≈ 73–74.5%, ladder
V1→V5 gần như phẳng, mạch lượng tử random-frozen ≈ RBF, variance cross-subject
lấn át mọi khác biệt. Đây là điểm xuất phát, không phải kỳ vọng "quantum thắng".

Do đó bài KHÔNG đặt cược vào "quantum tăng accuracy" (lý thuyết + dữ liệu đều
chống lại). Giá trị nằm ở: (a) một cơ chế distillation có cấu trúc mới, (b) định
vị lại giá trị sang GIẢM VARIANCE cross-subject, (c) khảo sát diagnostic trung
thực quantum-vs-classical.

- PHA 1 (trọng tâm, đường chắc): neighborhood-structure relational distillation
  + framing "variance regularizer". Chạy được trên hạ tầng đã dựng. Đảm bảo có bài.
- PHA 2 (optional, high-risk): Riemannian-covariance relational encoding. Chỉ làm
  nếu Pha 1 xong sớm và còn thời gian. Bỏ Pha 2 KHÔNG ảnh hưởng tính đứng của bài.

Mức tham vọng quantum: GIỮ MỞ. Thiết kế đối xứng quantum-encode vs classical-encode
của cùng một quan hệ; KẾT QUẢ quyết định nhãn cuối (quantum có vai trò thật / tương
đương). Không cam kết "quantum thắng" từ đầu.

---

## 2. Claims (mọi bảng/hình phải bám 1 claim)

- C1 (method): neighborhood-structure relational distillation là cơ chế truyền
  quan hệ khác pairwise thuần (QRKD) — chọn lọc theo teacher (uncertainty +
  local geometry), không phải toàn bộ N² cặp.
- C2 (giá trị, H3): cơ chế này GIẢM VARIANCE cross-subject trên MI-EEG, kể cả
  khi accuracy trung bình không tăng. ĐÂY LÀ CLAIM CHÍNH.
- C3 (diagnostic honest): quantum encoding ≈ classical kernel ở quy mô này;
  cấu trúc/selection quan trọng hơn không gian biểu diễn.
- C4 (định vị đúng): cải thiện (nếu có) nhỏ, nằm trong dao động — không overclaim.

---

## 3. Method — Pha 1

Ký hiệu: một batch N mẫu; teacher feats F^T ∈ R^{N×d}, student feats F^S ∈ R^{N×d},
d=144 (EEGNet, n_out_time=9 → 16×9). Kernel k(·,·) ∈ {quantum, cosine, rbf}.

### 3.1 Quan hệ pairwise chuẩn (nền, QRKD-style)
Ma trận quan hệ R_{ij} = k(f_i, f_j) cho MỌI cặp; loss = MSE(R^S, R^T). Đây là
`qrd_dense` — baseline nội bộ, KHÔNG phải đóng góp.

### 3.2 Neighborhood-structure relational distillation (ĐÓNG GÓP C1)
Thay vì truyền toàn bộ N² cặp (bị chi phối bởi các cặp xa vô nghĩa), ta truyền
CẤU TRÚC QUAN HỆ CỤC BỘ mà teacher cho là có ý nghĩa:
- Chọn tập mẫu S theo teacher-guided score: s_i = w_e·H_norm(teacher_i) +
  w_d·JS(teacher_i, student_i) (entropy chuẩn hoá + bất đồng teacher-student).
  → tập trung vào mẫu teacher "chắc" và mẫu student còn sai.
- Trong S, giữ quan hệ theo lân cận: anchor + kNN theo KHÔNG GIAN TEACHER
  (global_local), thay vì mọi cặp.
- Loss = MSE trên tập cặp được chọn: L_rel = MSE(R^S[M], R^T[M]), M = mask cặp.

Diễn giải: preserve local geometry teacher coi là quan trọng → đóng vai
regularizer cấu trúc cho student.

### 3.3 Framing variance-regularizer (ĐÓNG GÓP C2)
Giả thuyết: truyền cấu trúc quan hệ (thay vì chỉ logits/feature) ổn định hoá biểu
diễn student GIỮA các subject → giảm σ_sub (std accuracy cross-subject). Đo trực
tiếp bằng per-subject metrics (mục 8). Đây là nơi giá trị của bài nằm, KHÔNG phải
ở accuracy trung bình.

### 3.4 Tổng loss
L = α·CE + (1−α)·KD(logits) + β·L_rel   (feature_kd/rkd thêm số hạng tương ứng)

---

## 4. Dataset & Protocol (đã kiểm chứng)

- PhysionetMI (eegmmidb) qua MOABB. 103 subject (loại 88,90,92,100,104,106).
- Nhị phân: left_hand(0) vs right_hand(1).
- 64 kênh; bandpass 4–38 Hz; CAR; resample 100 Hz; window 3.0s = 300 mẫu.
- LOSO 5-fold: 62 train / 21 val / 20 test subject. Mỗi subject vào test ĐÚNG 1 lần
  → per-subject acc well-defined trên toàn 103 subject.
- Teacher = Ensemble-MI (n_subsets=7), train lại trên HPC (self-consistent).

---

## 5. Ma trận thí nghiệm (một lần chạy ra đủ)

Nhóm A — Ladder KD (dùng teacher), 5-fold, log per-subject:
  teacher, no_kd, kd_base, feature_kd, rkd_classical,
  qrd_dense, qrd_anchor, qrd_global_local, qrd_teacher_guided,
  ck_cosine_tg, ck_rbf_tg
Nhóm B — Sensitivity: method chính (qrd_teacher_guided) × β ∈ {0.01, 0.02, 0.05}
Nhóm C — Baseline đối chứng mới:
  C1) deep_ensemble_nokd : no_kd × 3 seed, ensemble logits (bảo vệ C2)
  C2) riemann_ts_lda     : pyriemann Covariances+TangentSpace+LDA (bảo vệ C1 + EEG ref)

---

## 6. Tham số & Justification (Cách 3: cố định theo chuẩn cộng đồng)

Nguyên tắc: tham số distillation cố định theo giá trị chuẩn văn liệu KD, KHÔNG
tune trên test. Lý do khoa học (viết vào Methods): (a) tránh test-set leakage;
(b) MỌI method dùng chung một bộ tham số → khác biệt đến từ CƠ CHẾ, không từ
tuning. Đây là cách cô lập biến, không phải bào chữa.

| Tham số | Giá trị | Justification |
|---|---|---|
| alpha (CE:KD) | 0.5 | Cân bằng hard/soft label chuẩn trong KD |
| temperature T | 4.0 | Giá trị chuẩn Hinton (2–4); T=4 phổ biến, dễ bảo vệ |
| beta (relation) | 0.02 + sensitivity {0.01,0.02,0.05} | Đặc thù method → chạy sensitivity 1 chiều chứng minh không phụ thuộc tinh chỉnh |
| gamma_feat, gamma_rkd | 1.0 / 1.0 | Trọng số phụ-loss = 1.0 cho mọi baseline liên quan, không thiên vị |
| n_qubits, n_q_layers | 4, 2 | 144→4 vừa angle-embedding; mạch NÔNG (2 layer) tránh barren plateau (chuẩn QML) |
| qrd_batch_size | 16 | Sub-batch để ma trận kernel N×N khả thi |
| num_anchors, knn_k | 8, 4 | Tỉ lệ hợp lý trên 16; structure-ablation (dense/anchor/global_local) đã bao phủ độ nhạy |

Teacher (Ensemble-MI [Zoumpourlis 2024]): n_subsets=7, n_modules_stage_1=4,
SGD lr=0.01, momentum=0.9, weight_decay=0.01, batch=64, feat-dim=144, 120 epoch
— giữ nguyên cấu hình gốc của kiến trúc teacher.
Student và mọi baseline KD: cùng backbone (EEGNet, feat-dim=144) + SGD momentum=0.9,
weight_decay=0.01, batch=64, lr=0.005, 30 epoch — một setup KD chung, KHÔNG tune
riêng từng biến thể. Justification: "teacher dùng cấu hình gốc của kiến trúc nguồn;
student và mọi baseline dùng chung một cấu hình huấn luyện để cô lập tác động của
cơ chế distillation — khác biệt giữa các method đến từ cơ chế, không từ tuning."

---

## 7. Baseline đối chứng — vì sao đúng 2 cái này

Mỗi baseline ánh xạ 1-1 với một câu hỏi reviewer nguy hiểm nhất; cả hai KHÔNG cần
teacher/quantum, tái dùng data + code có sẵn (nhẹ, đúng ràng buộc thời gian).

- deep_ensemble_nokd (bảo vệ C2): "giảm variance thì ensemble tầm thường cũng làm
  được — method hơn ở đâu?". So method vs ensembling no-KD (3 seed). Nếu method
  giảm variance hiệu quả/rẻ hơn → C2 vững; nếu không → biết trung thực.
- riemann_ts_lda (bảo vệ C1 + tính hợp lệ EEG): "so với phương pháp EEG kinh điển
  thì sao?". Neo số vào mốc cộng đồng; cầu nối tự nhiên tới Pha 2 (Riemannian).
  LƯU Ý: Riemannian-TS-LDA có thể NGANG/HƠN teacher deep trên PhysionetMI 2-class
  — nếu vậy là finding honest, KHÔNG xấu; định vị bài "không nhằm SOTA accuracy mà
  nhằm cơ chế distillation + variance". Đứng ở dòng riêng ("classical EEG ref"),
  ngoài ladder KD.

Rủi ro đã biết (ghi vào Limitations): không có baseline giảm-variance thứ 2
(augmentation...) → nếu bị hỏi thêm, trả lời bằng lập luận + để future work.

---

## 8. Thống kê — ĐƠN VỊ LÀ SUBJECT (không phải fold)

- Metric gốc: per-subject accuracy. Mỗi subject vào test đúng 1 lần (LOSO) → 103
  giá trị acc/method. Kappa/F1 cũng per-subject.
- Báo cáo: mean ± std TRÊN 103 SUBJECT (không phải trên 5 fold). std này CHÍNH LÀ
  σ_sub — đại lượng trung tâm của C2.
- Significance: so sánh cross-subject (n=103) bằng Wilcoxon signed-rank PAIRED
  theo subject (mỗi subject có acc dưới mỗi method). Đủ n để test hợp lệ — giải
  quyết dứt điểm lỗi Wilcoxon-5-fold của bản cũ.
- Variance reduction test: so σ_sub giữa method vs no_kd bằng Levene/Brown-Forsythe
  (test bằng nhau của phương sai). ĐÂY là test cho claim chính C2, không phải test accuracy.

---

## 9. Go / No-Go (định lượng, quyết trước khi nhìn kết quả)

- GO cho C2 (variance) nếu: σ_sub(method) < σ_sub(no_kd) với Levene p<0.05 VÀ
  giảm tương đối ≥ 15%. → bài đứng bằng "variance regularizer".
- PARTIAL nếu: σ_sub giảm nhưng không đạt p<0.05 → báo cáo effect size + CI, định
  vị "xu hướng giảm variance", nhẹ hơn nhưng vẫn honest.
- NO-GO cho C2 → rớt về kịch bản B (diagnostic thuần): bài vẫn đứng bằng C1
  (method mới) + C3 (quantum≈classical) + phân tích trung thực. KHÔNG chạy lại,
  chỉ đổi nhãn/khung viết.
- Quantum: GO cho "quantum có vai trò" nếu ck_quantum tách khỏi ck_cosine/rbf
  (accuracy HOẶC variance) với p<0.05. Nếu không → "quantum encoding tương đương
  classical ở quy mô này" (C3), vẫn hợp lệ.

Mọi nhánh trên đều CHO RA BÀI. Không có kịch bản phải chạy lại để cứu.

---

## 10. Bảng & Hình cần có (một lần chạy đủ)

BẢNG:
- T1 Main: mọi method × (acc, kappa, F1) mean±std trên 103 subject. [C1,C3,C4]
- T2 Variance: mỗi method × (σ_sub, min-subject acc, % subject cải thiện vs no_kd,
  Levene p vs no_kd). [C2 — bảng cốt lõi]
- T3 Selection ablation: dense→anchor→global_local→teacher_guided (cùng kernel). [C1]
- T4 Representation ablation: teacher_guided × {quantum,cosine,rbf}. [C3]
- T5 Cost: params, FLOPs, train-time/epoch, inference-time (student vs teacher). [C4]

HÌNH:
- F1 Sơ đồ method (pipeline + neighborhood-relation). [C1] (vẽ tay)
- F2 Per-subject box/violin acc từng method — thấy method thu hẹp spread. [C2]
- F3 Paired scatter no_kd vs method (mỗi điểm=1 subject) — subject yếu được kéo lên. [C2]
- F4 Kernel heatmap: K_quantum vs K_rbf cùng batch (≈ nhau). [C3]
- F5 (optional) Convergence val/test theo epoch. [phụ]

CON SỐ cho abstract/text: teacher acc; Δσ_sub method tốt nhất vs no_kd; Levene p;
n subject "kém" (<60%) được cải thiện.

---

## 11. Yêu cầu LOGGING (phải có TRƯỚC khi chạy — nếu thiếu phải chạy lại)

1. Per-subject metrics: evaluate_full trả acc/kappa/f1 THEO subject_id (không chỉ
   gộp). Bắt buộc — T2/F2/F3 và toàn bộ C2 phụ thuộc.
2. Đơn vị thống kê = subject (mục 8). Lưu bảng dài: (method, fold, subject_id,
   acc, kappa, f1) → mọi bảng/hình rút từ đây.
3. Kernel dump (F4): mỗi kernel_type, lưu K_student/K_teacher của 1 batch cố định.
4. Giữ per-epoch history (F5, kiểm hội tụ). Đã có.
5. Cost (T5): script riêng đo params/FLOPs/latency 1 lần.

---

## 12. Pha 2 (optional, high-risk) — Riemannian-covariance encoding

Chỉ làm nếu Pha 1 xong sớm. Ý tưởng: encode quan hệ giữa ma trận COVARIANCE (SPD
manifold) thay vì giữa vector đặc trưng. HIGH-RISK: phải định nghĩa chặt metric
manifold (AIRM/log-Euclidean) khi đưa vào mạch — vectorize ngây thơ sẽ mất cấu
trúc manifold, reviewer Riemannian bắt lỗi. Validate định nghĩa toán SỚM trước khi
code. Nếu kẹt → dừng, Pha 1 đã đủ ra bài.

---

## 13. Rủi ro & phòng ngừa (tóm tắt)

- Quantum không thắng accuracy: ĐÃ tính trước, giá trị ở variance + method. Không rủi ro bài.
- Riemannian baseline > teacher: finding honest, định vị lại, không xấu.
- Variance không giảm đủ: go/no-go mục 9 → rớt về diagnostic, vẫn có bài.
- Barren plateau (PQC): mạch nông 2 layer; quantum giữ mở, không phụ thuộc.
- Thời gian: Pha 2 optional, bỏ được. Pha 1 chạy trên hạ tầng đã dựng.

---

## 14. Ánh xạ sang cấu trúc paper

- Intro/Related: định vị vs QRKD (pairwise) + KD-EEG + QML-EEG; nêu C1–C4.
- Method: mục 3 (neighborhood-relation) + 6 (tham số justify).
- Experiments: mục 4 (data), 5 (ma trận), 7 (baseline), 8 (thống kê subject-level).
- Results: T1–T5, F1–F5; C2 (variance) là kết quả CHÍNH, không phải accuracy.
- Discussion: C3 (quantum≈classical honest), go/no-go outcomes, khi nào có ích.
- Limitations: baseline variance thứ 2, quy mô qubit, Pha 2 chưa làm.

---
## CẬP NHẬT / ĐÍNH CHÍNH SAU FULL RUN PHA 2 (2026-07-21)
*Các mục dưới đây SỬA/BỔ SUNG nội dung gốc ở trên; giữ bản gốc để truy vết.*

- **Mục 5 dòng 102 (số seed ensemble):** `deep_ensemble_nokd` chạy **5 seed**
  (SEEDS=[0..4] trong run_ensemble.py), KHÔNG phải 3 seed như ghi gốc. 5 seed ổn định hơn.

- **Mục 6 (epoch teacher):** teacher train **120 epoch** (5 fold), KHÔNG phải 30.
  Con số 30 là của STUDENT + mọi baseline KD/ensemble. Sửa để tránh nhầm.

- **Mục 7 dòng 145 (Riemann):** giả định "Riemannian-TS-LDA có thể NGANG/HƠN teacher
  trên PhysionetMI 2-class" **KHÔNG đúng** trên setup này. Thực tế: riemann_ts_lda = **58.7%**,
  bám no_kd, thua distill ~22pp. Vai trò "classical EEG ref" (C1) VẪN hợp lệ, nhưng là
  baseline **YẾU**, không phải baseline mạnh. Cầu nối Pha 2 Riemannian cần xét lại kỳ vọng.

- **Mục 5 dòng 140-142 (câu hỏi ensemble bảo vệ C2):** ĐÃ trả lời bằng số. Deep ensemble
  **KHÔNG** giảm variance đáng kể (chỉ 4.1% so single-seed). qrd ≈ ensemble về σ_sub.
  => C2 KHÔNG vững theo nghĩa "qrd giảm variance hiệu quả/rẻ hơn ensemble"; vững theo nghĩa
  **honest-diagnostic**: cả hai không giảm được variance nội tại của subject ở mức acc cao.

- **Mục 9 (Go/No-Go C2) — KẾT QUẢ THỰC:** C2 = **PARTIAL -> diagnostic**.
  σ_sub(method) KHÔNG < σ_sub(no_kd) (confound chance-floor); vs kd_base/ensemble không đạt
  p<0.05 và không đạt giảm ≥15%. Rớt về diagnostic theo đúng dòng 173-174, 234. VẪN CÓ BÀI:
  định vị lại đóng góp = **low-tail robustness** (min-subject, #subj<70%), KHÔNG phải giảm σ.

- **Mục 10 — số cho abstract:** KHÔNG dùng "Δσ_sub vs no_kd" (âm, confound). Dùng thay:
  teacher acc; distill gain ~+23pp; min-subject qrd vs ensemble/kd_base; C2 diagnostic honest.
