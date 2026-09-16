# Hướng dẫn đo độ trễ suy luận thật trên Raspberry Pi 4

Mục đích: đo `T_infer` của student (EEGNetv4) trên phần cứng nhúng thật,
bổ sung cho số đo trên CPU máy chủ HPC (Bảng `tab:tre` trong bài). Tài
liệu này ghi lại toàn bộ quy trình đã chạy thành công ngày 2026-08-08/09,
để một phiên Claude Code khác (cửa sổ khác, không có ngữ cảnh hội thoại
này) có thể lặp lại mà không phải dò lại từ đầu các lỗi đã gặp.

## Điều kiện tiên quyết

- Pi4 và máy chủ HPC (`adminsm`, node `ai01`) cùng nằm trong một mạng
  Tailscale. Kiểm tra địa chỉ Tailscale của cả hai tại
  https://login.tailscale.com/admin/machines (hoặc hỏi người dùng địa chỉ
  100.x.x.x hiện tại của `adminsm` và của Pi4, vì địa chỉ có thể đổi).
- Không cần biết địa chỉ IP nội bộ/campus của HPC (ví dụ 192.168.x.x) —
  địa chỉ đó KHÔNG dùng được từ Pi4 vì khác mạng vật lý. Luôn dùng địa
  chỉ Tailscale (100.x.x.x) cho chiều Pi4 -> HPC.
- Script `scripts/export_student_pi4.py`, `scripts/bench_pi4.py`,
  `scripts/run5_pi4.sh` đã có sẵn trong repo (nhánh `main`).

## Bước 1 — Xuất mô hình TorchScript trên HPC

Chạy trên login node HPC (đây là smoke test nhẹ, KHÔNG cần hỏi trước,
theo quy tắc dự án — nhưng vẫn phải qua `qsub`, không chạy `torch`/
`braindecode` trực tiếp trên login node):

```bash
qstat -u gv_nphuy   # xac nhan khong co job ket E truoc khi qsub
qsub jobs/export_student_pi4.pbs
```

Job này build kiến trúc EEGNetv4 (`n_chans=64, n_outputs=2, n_times=300`,
trọng số **ngẫu nhiên**, không cần checkpoint thật vì độ trễ suy luận chỉ
phụ thuộc kiến trúc/kích thước tensor, không phụ thuộc giá trị trọng số),
trace bằng `torch.jit.trace`, lưu ra
`results/pi4_latency/student_eegnetv4_traced.pt`.

**Bẫy đã gặp, script hiện tại đã xử lý sẵn, không cần sửa lại**:
- API `EEGNetv4` của bản `braindecode` đang cài đã đổi tên tham số:
  `in_chans`→`n_chans`, `n_classes`→`n_outputs`,
  `input_window_samples`→`n_times`.
- `torch.jit.trace` gọi `hasattr()` nội bộ để dò các thuộc tính của
  `EEGModuleMixin`. Nếu không truyền `chs_info` và `sfreq`, các property
  `chs_info`/`n_times`/`input_window_seconds`/`sfreq` sẽ ném `ValueError`
  (không phải `AttributeError`) khiến `hasattr()` không bắt được và
  trace thất bại. Script đã truyền đủ `chs_info=[...]` và `sfreq=100`.

Theo dõi job xong (`qstat -u gv_nphuy` tới khi hết dòng job), rồi kiểm
tra `logs/export_student_pi4.log` có `rc=0` và dòng
`OK: traced model khop model goc.`.

## Bước 2 — Chuyển file từ HPC sang Pi4

Trên Pi4 (SSH vào Pi4 từ máy Windows trước, ví dụ `ssh pi4`), gọi thẳng
`scp` với địa chỉ Tailscale của `adminsm` (KHÔNG dùng địa chỉ nội bộ
192.168.x.x, không có đường mạng từ Pi4 tới đó):

```bash
scp gv_nphuy@<tailscale-ip-cua-adminsm>:/gpfs0/users/gv_nphuy/projects/qrd_eeg/results/pi4_latency/student_eegnetv4_traced.pt .
scp gv_nphuy@<tailscale-ip-cua-adminsm>:/gpfs0/users/gv_nphuy/projects/qrd_eeg/scripts/bench_pi4.py .
scp gv_nphuy@<tailscale-ip-cua-adminsm>:/gpfs0/users/gv_nphuy/projects/qrd_eeg/scripts/run5_pi4.sh .
```

Nếu `adminsm` bật Tailscale SSH, lệnh trên sẽ tự mở link xác thực trình
duyệt (`https://login.tailscale.com/a/...`) ở lần đầu, sau đó chạy bình
thường.

## Bước 3 — Cài môi trường Python trên Pi4

Raspberry Pi OS bản mới (Debian Bookworm+) chặn `pip install` thẳng vào
Python hệ thống (PEP 668, lỗi `externally-managed-environment`). Luôn
tạo venv:

```bash
python3 -m venv ~/pi4bench
source ~/pi4bench/bin/activate
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

**Bẫy đã gặp**: `pip install torch` KHÔNG có `--index-url ... /cpu` sẽ
kéo theo các gói CUDA (`nvidia_cublas`, ~540MB) dù Pi4 không có GPU
NVIDIA, làm hết dung lượng thẻ SD (`No space left on device`). Luôn chỉ
định đúng index CPU-only ở trên.

## Bước 4 — Chạy benchmark

Chạy một lần để kiểm tra:
```bash
python3 bench_pi4.py student_eegnetv4_traced.pt
```

Chạy 5 lần độc lập (khớp quy ước "n=5 hạt giống" của cả bài, tránh dựa
vào một lần chạy đơn không đáng tin cậy) và tự tính trung bình ± độ lệch
chuẩn:
```bash
bash run5_pi4.sh
```

Script `run5_pi4.sh` tự gọi `bench_pi4.py` 5 lần (mỗi lần là một tiến
trình Python độc lập, không phải lặp lại trong cùng process, để phản ánh
đúng dao động thật giữa các lần chạy do tần số CPU tự điều chỉnh), rồi in
`mean`/`sd` cho cả `median` và `p95`.

Gửi lại toàn bộ output (không chỉ 2 dòng cuối) để đối chiếu số liệu.

## Kết quả tham chiếu

**Đo lại 2026-08-16 (số liệu dùng trong bài, `tab:pi4`)**: SSH trực tiếp
từ login node HPC (`adminsm`, tài khoản `gv_nphuy`) vào Pi4 qua
`tailscale nc` làm `ProxyCommand` (không cần máy Windows trung gian) —
xem `docs/PI4_SSH_GUIDE.md` để tự lặp lại toàn bộ, không cần dò lại từ
đầu. `bench_pi4.py`
đã bổ sung đo RAM tiến trình (`resource.getrusage().ru_maxrss`) cạnh độ
trễ.

- Chạy 2 lượt độc lập, mỗi lượt 5 lần chạy (10 lần tổng), kết quả nhất
  quán trong sai số giữa hai lượt.
- Lượt dùng để báo cáo: median trung bình $7{,}99 \pm 0{,}08$ ms; p95
  trung bình $8{,}14 \pm 0{,}11$ ms; RAM sau khi nạp model $216{,}08 \pm
  0{,}03$ MB; RAM đỉnh khi suy luận $238{,}07 \pm 0{,}02$ MB.
- So với CPU máy chủ HPC (median 3,17 ms): cao hơn ~2,5 lần, chỉ chiếm
  ~0,27% ngân sách cửa sổ tín hiệu 3000 ms.
- Kiểm tra phần cứng ngay lúc đo: CPU giữ 1800 MHz (tối đa), 39,4°C,
  không throttle (`vcgencmd get_throttled` = `0x0`), tải hệ thống gần
  rảnh.

**Teacher (Ensemble-MI) trên Pi4, cùng ngày 2026-08-16**: export bằng
`scripts/export_teacher_pi4.py` (input dạng dict `{'x': tensor}`, xem
comment trong file — `subset`/`dataset_idx` không được đọc trong
forward() lúc eval nên không cần truyền), benchmark bằng
`bash run5_pi4.sh teacher_ensembleeeg_traced.pt --dict-input`.

- median trung bình $85{,}30 \pm 1{,}42$ ms; p95 trung bình $87{,}26 \pm
  1{,}48$ ms; RAM sau khi nạp model $219{,}11 \pm 0{,}05$ MB; RAM đỉnh
  $251{,}63 \pm 0{,}11$ MB.
- Chậm hơn student trên Pi4 khoảng 10,7 lần, so với ~7,1 lần trên CPU
  HPC — khoảng cách nới rộng thêm trên phần cứng yếu hơn.
- RAM đỉnh chỉ cao hơn student ~5,7% dù gấp 6,3 lần số tham số — phần
  lớn RAM đo được là overhead cố định của Python/PyTorch runtime, không
  phải trọng số/activation thật của model.
- Điều kiện phần cứng lúc đo: 1800 MHz, 40,9°C, không throttle.

**Kết quả phiên đo trước (2026-08-08/09, không còn dùng trong bài)**:
median trung bình 26,68 ± 3,24 ms, p95 trung bình 50,38 ± 2,59 ms — chậm
hơn ~3,3 lần và dao động rộng hơn nhiều so với lần đo lại. Không có bản
ghi trạng thái nhiệt/tải nền tại thời điểm đo đó nên không xác nhận được
nguyên nhân chắc chắn, nhưng phù hợp với giả thuyết CPU bị throttle hoặc
có tải nền tại thời điểm đo. Nếu đo lại lần nữa và thấy số liệu lệch xa
so với 2026-08-16, luôn kiểm tra `vcgencmd measure_temp` / `get_throttled`
/ `cat /proc/loadavg` trước khi kết luận.

## Nếu muốn dò thêm thông tin phần cứng/phần mềm của node HPC

Dùng `scripts/probe_hw_env.py` qua `jobs/probe_hw_env.pbs` (cũng là smoke
test nhẹ, tự `qsub` được) để lấy CPU model, số luồng, BLAS backend, OS,
phiên bản PyTorch của chính node đã chạy benchmark CPU gốc — phục vụ yêu
cầu ghi rõ cấu hình phần cứng/phần mềm trong Bảng `tab:tre`.
