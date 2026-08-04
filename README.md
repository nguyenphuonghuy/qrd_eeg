# QRD-EEG — Quantum Relational Distillation cho giải mã tưởng tượng vận động (Motor Imagery)

Mã nguồn, log job, và số liệu thực nghiệm cho bài báo *"Quantum Relational
Knowledge Distillation for Motor Imagery Decoding: A Controlled Comparison
under Real-Time Control Constraints"* (đang revise, IJRCS).

Khung QRD chưng cất tri thức từ một teacher (mô hình tập hợp lớn) sang một
student (EEGNet gọn nhẹ), trong đó cấu trúc quan hệ giữa các mẫu được mô tả
bằng hàm nhân lượng tử ở **giai đoạn huấn luyện**. Mạch lượng tử không xuất
hiện trong mô hình triển khai. Repo này khảo sát năm chiến lược hình thành
quan hệ (V1–V5) và ba dạng hàm nhân (lượng tử, cosine, RBF) trong điều kiện
đồng nhất, trên bộ dữ liệu PhysionetMI (kiểm định chính) và Cho2017 (khám
phá, đối chiếu tính khái quát).

Bản thảo đầy đủ (LaTeX + số liệu + hình): [`paper/`](paper/). Bài báo dùng
tiếng Việt; các file mã nguồn dùng tiếng Việt không dấu trong comment/log
vì lý do lịch sử (chạy trên HPC, tránh lỗi encoding trong một số công cụ).

## 1. Cấu trúc repo

```
scripts/            Mã nguồn chính (train_all.py = logic huấn luyện + METHOD_TABLE;
                     run_all.py = chạy 1 seed cố định, nhiều method;
                     run_seeds.py = chạy nhiều seed qua biến môi trường;
                     extract_tsne_feats.py, plot_tsne.py = trích đặc trưng + vẽ Hình 3)
jobs/                Job PBS dùng trên cụm HPC nội bộ (mỗi job ứng với 1 thí nghiệm/ablation)
logs/                Log chạy thật của từng job trong jobs/ (tên file khớp theo #PBS -N)
results/             Số liệu per-subject (CSV) và tổng hợp (xlsx) sinh ra từ mỗi job
checkpoints/         Checkpoint teacher (Ensemble-MI) đã huấn luyện, 5 fold, PhysionetMI
checkpoints_cho2017/ Checkpoint teacher tương ứng cho Cho2017
paper/               Nguồn LaTeX của bài báo (body.tex, main.tex, references.bib, figs/)
docs/                Ghi chép quyết định thiết kế và lịch sử phiên làm việc (xem mục 6)
external/Ensemble-MI Repo bên thứ ba chứa kiến trúc teacher/student và pipeline dữ liệu
                     (KHÔNG nằm trong git, xem mục 2)
```

## 2. Cài đặt môi trường

Thí nghiệm chạy trên Python 3.11 với các thư viện chính (đã kiểm chứng ở
phiên bản dưới đây; các phiên bản mới hơn có thể vẫn tương thích nhưng chưa
được kiểm chứng lại):

| Thư viện | Phiên bản |
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

```bash
conda create -n qrd_env python=3.11
conda activate qrd_env
pip install torch pennylane mne braindecode moabb scikit-learn numpy pandas scipy openpyxl
```

Repo con `external/Ensemble-MI` (kiến trúc teacher gốc, tác giả
Zoumpourlis và cộng sự) không đi kèm trong git vì lý do kích thước và bản
quyền. Clone repo đó riêng và trỏ biến môi trường `ENSEMBLE_MI_DIR` tới nó:

```bash
git clone <URL Ensemble-MI> external/Ensemble-MI
export ENSEMBLE_MI_DIR=$(pwd)/external/Ensemble-MI
```

**Bẫy quan trọng:** mọi script trong `scripts/` phải chạy với thư mục làm
việc (`cwd`) là `$ENSEMBLE_MI_DIR`, vì `initializers.py` bên trong dùng
`os.getcwd()` để tìm `preprocessed_data/` (không dùng đường dẫn tuyệt đối).
Luôn `cd "$ENSEMBLE_MI_DIR"` trước khi gọi `python .../scripts/run_*.py`.

Dữ liệu EEG (PhysionetMI, Cho2017) tải tự động qua MOABB ở lần chạy đầu và
được cache dưới dạng `.pkl` trong `preprocessed_data/` (có file tới
~467MB/đối tượng) — các file này **không** nằm trong git (xem
`.gitignore`), sẽ tự sinh lại khi chạy.

## 3. Tái lập thí nghiệm

### 3.1. Chạy nhanh, một seed cố định (`run_all.py`)

Dùng để chạy toàn bộ ma trận method trên 5 fold với seed cố định
`20200220`, phù hợp để kiểm tra nhanh hoặc tái lập cột "một hạt giống"
trong Bảng đảo hạng của bài báo.

```bash
cd "$ENSEMBLE_MI_DIR"
python /path/to/qrd_eeg/scripts/run_all.py \
    --methods no_kd,kd_base,feature_kd,rkd_classical,qrd_dense,qrd_anchor,qrd_global_local,qrd_teacher_guided,ck_cosine_tg,ck_rbf_tg \
    --folds 0,1,2,3,4 --epochs 30 --out results/results_all.xlsx
```

Nếu `--methods` chứa `qrd_teacher_guided`, script tự sinh thêm hai biến thể
`qrd_tg_b0.01` và `qrd_tg_b0.05` (khảo sát độ nhạy hệ số β). Cờ
`--skip_teacher` bỏ qua bước huấn luyện lại teacher (dùng checkpoint có
sẵn trong `checkpoints/`).

### 3.2. Nhiều hạt giống (`run_seeds.py`)

Dùng cho mọi bảng số chính trong bài báo (đơn vị suy luận thống kê là hạt
giống, `n=5`). Tham số truyền qua **biến môi trường**, không qua CLI:

| Biến | Ý nghĩa | Mặc định |
|---|---|---|
| `QRD_SEEDS` | Danh sách hạt giống, phân tách bằng dấu phẩy | `1,2,3,4,5` |
| `QRD_N_FOLDS` | Số fold | `5` |
| `QRD_MAX_EPOCHS` | Số epoch huấn luyện student | `30` |
| `QRD_RUNS` | `"tag:method:beta,tag:method,..."` (beta rỗng bỏ qua) | 3 method QRD mặc định |
| `QRD_DATASET` | `PhysionetMI` hoặc `Cho2017` | `PhysionetMI` |
| `QRD_OUT_DIR` | Thư mục ghi CSV | `results/` |
| `QRD_SEEDS_OUT` | Tên file CSV | `seeds_per_subject.csv` |
| `QRD_TEACHER_DIR` | Thư mục checkpoint teacher | `checkpoints/` |
| `QRD_ALPHA` | Hệ số α (CE:KD), override mặc định 0,5 | `0.5` |
| `QRD_OVERWRITE` | Đặt `1` để cho phép ghi đè `QRD_SEEDS_OUT` đã tồn tại | (rỗng, mặc định từ chối ghi đè) |
| `QRD_GRAD_DIAG` | Đặt `1` để in chẩn đoán `rawL=`/`gradNormS=` mỗi epoch | (rỗng) |

Ví dụ chạy lại toàn bộ 5 chiến lược quan hệ lượng tử (V1–V5) trên 5 hạt
giống, PhysionetMI:

```bash
cd "$ENSEMBLE_MI_DIR"
export ENSEMBLE_MI_DIR QRD_TEACHER_DIR=/path/to/qrd_eeg/checkpoints
export QRD_DATASET=PhysionetMI QRD_SEEDS="1,2,3,4,5"
export QRD_OUT_DIR=/path/to/qrd_eeg/results/repro_v1_v5
export QRD_SEEDS_OUT="v1_v5_per_subject.csv"
export QRD_RUNS="qrd_dense_noproj:qrd_dense_noproj,qrd_dense:qrd_dense,qrd_anchor:qrd_anchor,qrd_global_local:qrd_global_local,qrd_teacher_guided:qrd_teacher_guided"
python /path/to/qrd_eeg/scripts/run_seeds.py
```

Toàn bộ 20 method khả dụng được định nghĩa trong `METHOD_TABLE` ở
[`scripts/train_all.py`](scripts/train_all.py#L297) (5 cấu hình cổ điển,
5 biến thể QRD chính V1–V5, 2 kernel cổ điển đối chứng ± bản chiếu công
bằng chiều, 2 đối chứng `theta_mode`, 5 đối chứng độ nhạy $W_T$, 1 đối
chứng `random_pool64`).

### 3.3. Job PBS (cụm HPC nội bộ)

Mỗi file trong [`jobs/`](jobs/) là một job PBS đã dùng thật để sinh số liệu
trong `results/`, đọc trực tiếp để biết chính xác biến môi trường/tham số
đã dùng cho từng thí nghiệm. Các job này gắn với `-q sharedgpu` và tài
nguyên của cụm nội bộ, cần chỉnh `#PBS` header cho phù hợp hệ thống khác;
phần logic bên trong (gọi `run_all.py`/`run_seeds.py`) chạy độc lập với
PBS, có thể copy phần thân script để chạy trực tiếp bằng `bash` hoặc
`nohup` trên máy có GPU.

**Không chạy các script import `torch`/`mne`/`moabb`/`braindecode` trực
tiếp trên node đăng nhập của cụm chia sẻ** — luôn qua `qsub`/`sbatch` hoặc
tương đương, để tránh tải nặng ảnh hưởng người dùng khác.

## 4. Xem kết quả

Mỗi thư mục con của `results/` ứng với một job trong `jobs/` (tên thư mục
thường có ngày). File `*_per_subject.csv` là đơn vị dữ liệu gốc cho mọi
bảng trong bài báo, có cột:

```
method   — tag kèm hạt giống, ví dụ "qrd_dense_s3"
tag      — tên method không kèm hạt giống, ví dụ "qrd_dense"
seed     — hạt giống ngẫu nhiên
fold     — chỉ số fold (0-4)
subject  — mã số đối tượng
acc      — accuracy (%) của đối tượng đó trong fold/seed này
n        — số trial của đối tượng trong fold test
```

Vì mỗi đối tượng vào tập test đúng một lần trong 5-fold LOSO, để lấy
accuracy trung bình theo hạt giống cho một method: nhóm theo `subject`,
lấy trung bình `acc` (mỗi subject chỉ có 1 dòng ứng với fold nó thuộc tập
test), rồi trung bình các subject đó — chính là cách bài báo tính mọi số
"accuracy" trong Bảng 4–6, 10. Không dùng trực tiếp trung bình toàn bộ
515 dòng (không phải đơn vị thống kê đúng, xem Mục 4.1 của bài báo).

Bảng ánh xạ job → kết quả → mục trong bài báo (các job chính, xem thêm
`docs/TODO_NEXT.md` cho lịch sử đầy đủ):

| Job (`jobs/*.pbs`) | Kết quả (`results/`) | Dùng cho |
|---|---|---|
| `full_seeds*` (lịch sử, xem TODO_NEXT) | `seeds_per_subject.csv`, `seeds2_per_subject.csv` | Bảng 4, 5 (12 cấu hình × 5 seed) |
| `qrd_v1_seeds_rerun.pbs` | `qrd_v1_rerun_2026_08_03/` | V1 Dense trong Bảng 5, 6 |
| `no_kd_alpha1_seeds.pbs` | `no_kd_alpha1_2026_08_03/` | Baseline "không chưng cất" đã sửa lỗi α, Mục 4.4.1 |
| `no_kd_alpha_sweep.pbs` | `no_kd_alpha_sweep_2026_08_04/` | Bảng độ nhạy α cho no\_kd |
| `kernel_fair_seeds.pbs` | `kernel_fair_2026_08_03/` | Đối chứng cosine/RBF chiếu công bằng chiều, Mục 4.4.2 |
| `theta_mode_ablation.pbs` | `theta_mode_ablation_2026_08_04/` | Đối chứng θ dùng chung/cố định/tách riêng, Mục 3.4 |
| `beta_fairness_diag.pbs` | `beta_fairness_diag_2026_08_04/` | Chẩn đoán gradNormS/rawL theo hàm nhân, Bảng 1 |
| `pool64_control.pbs` | `pool64_control_2026_08_04/` | Đối chứng `random_pool64` cho V5, Mục 4.4.2 |
| `tsne_feats.pbs` + `plot_tsne_cpu.pbs` | `tsne_feats_2026_08_03/` | Hình 3 (t-SNE 4 panel) |
| `cho/*.pbs`, `cho_no_kd_alpha1_seeds.pbs` | `cho_*`, `cho_no_kd_alpha1_2026_08_04/` | Mục 4.4.6, kiểm chứng khám phá Cho2017 |

### Kết quả chính (PhysionetMI, 5 hạt giống, xem bài báo để đầy đủ)

- Chưng cất tri thức: 74,93% (không chưng cất) → 81,49% (KDBase), +6,56pp
  (CI95% [4,08; 9,04], p=0,0018).
- Ba dạng hàm nhân (cùng chiến lược V5): cosine 81,63%, RBF 81,61%, lượng
  tử 81,12% — không phát hiện khác biệt có ý nghĩa; khoảng tin cậy phép so
  sánh chính (lượng tử vs cosine) vượt ra ngoài biên tương đương ±0,5pp đã
  tiền đăng ký, nên **chưa đủ dữ liệu để kết luận theo bất kỳ chiều nào**.
  Chi phí huấn luyện nhánh lượng tử cao hơn khoảng 13 lần.
- Độ lệch chuẩn giữa 12 cơ chế chưng cất (0,459pp) nhỏ hơn độ lệch chuẩn
  do đổi hạt giống (0,750pp) — khác biệt giữa các cơ chế nằm dưới mức
  nhiễu tự nhiên của quy trình huấn luyện.

Số liệu đầy đủ, kiểm định thống kê, và giới hạn của từng kết luận: xem
[`paper/body.tex`](paper/body.tex) (Mục 4, Kết luận) hoặc biên dịch PDF
theo mục 5.

## 5. Biên dịch bài báo

```bash
cd paper/
tectonic -X compile main.tex   # hoặc: xelatex main.tex && bibtex main && xelatex main.tex && xelatex main.tex
```

Yêu cầu font TeX Gyre Termes (qua `fontspec`) và biên dịch bằng XeLaTeX
(khai trong `main.tex`), vì tài liệu dùng `polyglossia` cho tiếng Việt có
dấu.

## 6. Ghi chép quá trình (dành cho người tiếp tục dự án)

`docs/DESIGN.md` là thiết kế thí nghiệm đã đóng băng trước khi chạy.
`docs/AI_CONTEXT.md` và `docs/TODO_NEXT.md` ghi lại lịch sử quyết định,
lỗi đã phát hiện/sửa, và việc còn tồn đọng theo thứ tự thời gian — đọc
trước khi thay đổi thiết kế thí nghiệm hoặc chạy lại số liệu.

## Trích dẫn

Bài báo đang trong quá trình revise tại IJRCS; chi tiết trích dẫn sẽ được
bổ sung sau khi có thông tin xuất bản chính thức.
