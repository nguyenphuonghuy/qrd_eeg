# CLAUDE.md — qrd_eeg (Quantum Relational Distillation cho MI-EEG)

## Đọc trước khi làm bất cứ việc gì, theo đúng thứ tự
1. `../../CLAUDE.md` (quy tắc chung HPC)
2. `hpc_ai/`: README → HPC_CONTEXT → AI_WORKFLOW → PROJECT_STANDARD →
   ENVIRONMENT_STANDARD → PBS_STANDARD → TROUBLESHOOTING → CHECKLIST
3. `docs/DESIGN.md` — thiết kế ĐÃ ĐÓNG BĂNG. Không tự đổi hyperparameter,
   claim, hay ma trận thí nghiệm mà không hỏi.
4. `AI_CONTEXT.md` — lịch sử quyết định, bug đã gặp.
5. `docs/TODO_NEXT.md` — việc đang làm / đã quyết định KHÔNG làm.
6. `docs/PREREG_*.md` nếu có — cam kết thống kê CHỐT TRƯỚC KHI CHẠY, không
   đổi sau khi đã nhìn kết quả.

## Bối cảnh một câu
Bài báo (IJRCS, đang revise) khảo sát chưng cất quan hệ có cấu trúc
neighborhood cho MI-EEG, dùng kernel lượng tử làm "ca kiểm chứng khắt khe
nhất" — KHÔNG phải đề xuất "lượng tử thắng accuracy". Đóng góp chính (C2)
là khảo sát variance cross-subject, không phải accuracy trung bình.

## Lệnh nền tảng
PROJ=/gpfs0/users/gv_nphuy/projects/qrd_eeg
ENSEMBLE_MI_DIR=$PROJ/external/Ensemble-MI
PY=/gpfs0/users/gv_nphuy/envs/qrd_env/bin/python

## Bẫy đã gặp thật, đừng lặp lại
- `cd` PHẢI là `$ENSEMBLE_MI_DIR` trước khi gọi script import từ
  `train_all.py`. `initializers.py` dùng `os.getcwd()` để tìm
  `preprocessed_data/`, không dùng đường dẫn tuyệt đối.
- `run_all.py` khác `run_seeds.py`:
  - `run_all.py`: `--methods --folds --epochs --skip_teacher --out`, seed
    CỐ ĐỊNH 20200220 (không đổi qua CLI), tự sinh thêm `qrd_tg_b0.01`/
    `qrd_tg_b0.05` nếu thấy `qrd_teacher_guided` trong `--methods`.
  - `run_seeds.py`: tham số qua biến môi trường (`QRD_SEEDS`,
    `QRD_N_FOLDS`, `QRD_MAX_EPOCHS`, `QRD_RUNS`, `QRD_SEEDS_OUT`,
    `QRD_DATASET`, `QRD_OUT_DIR`). `QRD_RUNS="tag:method:beta,..."` có thể
    liệt kê nhiều method một lần, ghi chung 1 CSV. Tự thoát nếu
    `QRD_SEEDS_OUT` đã tồn tại trừ khi `QRD_OVERWRITE=1`.
  - `train_method(..., verbose=False)` khi gọi từ `run_seeds.py` → KHÔNG in
    `QRD varKs` mỗi epoch. Muốn xem chẩn đoán collapse, dùng `run_all.py`
    (verbose=True mặc định) cho 1 lượt smoke test trước.
- Đổi dataset qua `QRD_DATASET=Cho2017` (mặc định `PhysionetMI`). Checkpoint
  và output tách theo dataset (`checkpoints_cho2017/`, tiền tố `cho_*`).
- File `.pkl` tiền xử lý rất nặng (có file tới ~467MB/subject) — KHÔNG đưa
  vào git.

## Nguyên tắc trung thực khoa học
- Đơn vị thống kê là SUBJECT, không phải fold. Cột `±` trong log
  `train_all.py` là std trên 5 FOLD, không phải σ_sub.
- Không p-hacking, không quét hyperparameter tìm cấu hình đẹp để báo cáo.
- Không khẳng định điều gì "đã hoạt động" chỉ vì nghe hợp lý — luôn đối
  chiếu log/code thật trước. Không chắc cú pháp thì đọc code trước khi chạy.
- Phát hiện số liệu trong bài mâu thuẫn log/code thật thì dừng lại và báo,
  không tự làm tròn hay bỏ qua.
- Kết quả âm là kết quả hợp lệ, không phải lý do chạy lại tìm cấu hình khác.

## Văn phong khi sửa body.tex
- Tránh em-dash. Tránh lặp "vì vậy", "thứ nhất/hai/ba", "cho phép".
- Số thập phân dùng dấu phẩy (0,05 không phải 0.05).
- Dùng \eqref{} trỏ nhãn có sẵn, không ghi số phương trình cứng.
- Sau khi sửa .tex, biên dịch thử bằng xelatex (2 lần liên tiếp) trước khi
  báo đã xong, kiểm tra không phát sinh "Reference undefined" mới.

## Quy tắc tự động hoá job PBS
- **Smoke test (ước tính ≤ ~30 phút thực tế)**: được tự `qsub` không cần hỏi
  trước. Sau khi submit, tự lặp lại "chờ vài phút → `qstat` + `tail log` →
  chưa xong thì chờ tiếp" trong cùng phiên cho tới khi có kết quả, rồi tự
  đọc log và tự quyết định bước tiếp theo (đạt/không đạt tiêu chí, có nên
  tiến hành job lớn hay không).
- **Job thật (ước tính hơn ~1 giờ)**: PHẢI trình bày kế hoạch (walltime,
  method/seed/fold, output path dự kiến) và chờ xác nhận trước khi `qsub`,
  trừ khi được yêu cầu rõ "cứ submit luôn". Sau khi submit, KHÔNG tự ý ngồi
  chờ nhiều giờ — Bash tool có trần cứng 10 phút/lệnh, không có cách nào
  chờ xuyên suốt một job nhiều giờ trong một phiên. Ghi lại rõ Job ID,
  đường dẫn log, tiêu chí cần kiểm tra khi xong, rồi DỪNG và báo đang chờ
  người dùng xác nhận job hoàn tất trước khi tiếp tục.
