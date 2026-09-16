# Hướng dẫn: Claude Code tự SSH vào Raspberry Pi 4 từ login node HPC

Mục đích: cho phép một phiên Claude Code chạy trên login node HPC
(`adminsm.tnut.local`, thư mục dự án này) tự kết nối tới Raspberry Pi 4
dùng để đo benchmark phần cứng nhúng (xem `docs/PI4_BENCHMARK_GUIDE.md`),
**không cần người dùng thao tác tay qua máy Windows trung gian**.

Đã kiểm chứng hoạt động ngày 2026-08-16 với tài khoản HPC `gv_nphuy`.

## 1. Vì sao không `ssh`/`ping` trực tiếp được (đọc trước khi chẩn đoán lại từ đầu)

- Pi4 (Tailscale IP `100.125.255.91`, hostname OS `huy`) và login node HPC
  này nằm trong cùng mạng Tailscale (tài khoản Google
  `nguyenphuonghuy1979@gmail.com`), nhưng **khác mạng vật lý**. Không có
  đường đi trực tiếp qua IP nội bộ/campus.
- Login node HPC **không** có `tailscale` trong `PATH` hệ thống và
  **không** có interface kernel `tailscale0` (không có quyền tạo TUN
  device trên máy dùng chung). Không cài `tailscale` qua gói hệ thống,
  không cần `sudo`.
- Mỗi user HPC (ít nhất `gv_nphuy`, `gv_dnanh`, `gv_bvnam` — có thể còn
  người khác) đã tự cài **`tailscaled` chế độ userspace-networking**
  riêng tại `~/tailscale/` (binary `tailscale` + `tailscaled`, chạy nền,
  socket `~/tailscale/tailscaled.sock`). Đây là cách hợp lệ để một user
  không có quyền root vẫn tham gia được mạng Tailscale.
- Chế độ userspace-networking **không** tự mở cổng SOCKS5/HTTP proxy
  (không có gì lắng nghe ở `127.0.0.1:1055`), nên không dùng
  `ssh -o ProxyCommand="nc -X 5 -x 127.0.0.1:1055 %h %p"` được như cách
  làm quen thuộc với Tailscale chế độ TUN thường.
- Cách dùng được, **không cần khởi động lại `tailscaled`** (tránh làm
  gián đoạn các phiên SSH khác đang dùng chung daemon đó): lệnh
  **`tailscale nc <host> <port>`** — tự mở một kết nối TCP đơn lẻ tới
  `<host>:<port>` qua chính tailnet, pipe qua stdin/stdout. Dùng thẳng
  làm `ProxyCommand` cho `ssh`/`scp`.
- Xác thực: Pi4 dùng `PasswordAuthentication` (chưa thêm public key nào
  của HPC vào `~/.ssh/authorized_keys` trên Pi). Dùng `sshpass -p
  "$PASS"` để không cần nhập tay.

## 2. Kiểm tra điều kiện tiên quyết

```bash
# tailscaled cua chinh user dang dung da chay chua
ps aux | grep "[t]ailscaled --tun=userspace"

# neu chua chay, khoi dong (khong lam gian doan phien khac vi moi user
# co daemon rieng):
~/tailscale/start-tailscaled.sh

# xac nhan Pi4 thay duoc trong tailnet
~/tailscale/tailscale --socket=$HOME/tailscale/tailscaled.sock status | grep pi4

# sshpass co san khong (thuong co san tren HPC nay)
which sshpass
```

## 3. Kết nối nhanh (đã có sẵn helper trong repo)

```bash
cd /gpfs0/users/gv_nphuy/projects/qrd_eeg
source scripts/pi4_connect.sh      # nap ham pi_ssh() va pi_scp()

pi_ssh 'hostname && uname -a && nproc'
pi_scp local_file.py "$PI4_USER@$PI4_IP:~/"
```

`scripts/pi4_connect.sh` tự đọc thông tin đăng nhập từ
`scripts/.pi4_credentials.local` (đã **gitignore**, không commit). Nếu
file này bị mất (repo clone mới), tạo lại đúng định dạng:

```
PI4_USER=khoinguyen
PI4_PASS=12345678
PI4_IP=100.125.255.91
TS_BIN=/home/gv_nphuy/tailscale/tailscale
TS_SOCK=/home/gv_nphuy/tailscale/tailscaled.sock
```

(`TS_BIN`/`TS_SOCK` phải trỏ đúng `~/tailscale/` của tài khoản HPC đang
dùng — mỗi tài khoản có `tailscaled` riêng, xem §1.)

Đây là **cùng một Raspberry Pi 4 vật lý** dùng chung giữa nhiều dự án
trên máy HPC này (ví dụ dự án `ssvep_ensemble` của tài khoản `gv_dnanh`
cũng dùng chính thiết bị này, IP Tailscale giống hệt) — cùng một bộ thông
tin đăng nhập hệ điều hành Pi hoạt động từ mọi tài khoản HPC join được
tailnet đó, vì đều là cùng một máy Linux thật.

## 4. Môi trường Python đã cài sẵn trên Pi4 (không cần cài lại)

- venv: `~/pi4bench` (torch CPU-only — cài qua
  `pip install torch --index-url https://download.pytorch.org/whl/cpu`,
  **bắt buộc** chỉ định đúng index CPU vì Raspberry Pi OS chặn
  `pip install` thẳng vào Python hệ thống — lỗi PEP 668
  `externally-managed-environment` — và cài `torch` không chỉ định index
  sẽ kéo theo gói CUDA ~540 MB làm đầy thẻ SD).
- Model đã export: `~/student_eegnetv4_traced.pt` (sinh bởi
  `scripts/export_student_pi4.py` chạy trên HPC rồi `scp` sang, xem
  `docs/PI4_BENCHMARK_GUIDE.md` Bước 1-2 nếu cần export lại từ đầu).
- Script benchmark: `~/bench_pi4.py`, `~/run5_pi4.sh` — đồng bộ lại mỗi
  khi sửa bản trong `scripts/` của repo này, xem §5.

## 5. Quy trình chạy benchmark đầy đủ (tự động, không cần người dùng)

```bash
cd /gpfs0/users/gv_nphuy/projects/qrd_eeg
source scripts/pi4_connect.sh

# 1) dong bo script moi nhat len Pi (de neu vua sua bench_pi4.py/run5_pi4.sh)
pi_scp scripts/bench_pi4.py scripts/run5_pi4.sh "$PI4_USER@$PI4_IP:~/"

# 2) kiem tra trang thai phan cung TRUOC khi do (quan trong — do lech giua
#    cac phien do rat lon neu CPU dang throttle/co tai nen, xem §6)
pi_ssh '
  echo "--- governor ---"; cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
  echo "--- cur freq (kHz) ---"; cat /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
  echo "--- temp ---"; vcgencmd measure_temp
  echo "--- throttled ---"; vcgencmd get_throttled
  echo "--- load avg ---"; cat /proc/loadavg
'

# 3) chay benchmark (5 lan chay doc lap, ~1-2 phut)
pi_ssh 'source ~/pi4bench/bin/activate && cd ~ && bash run5_pi4.sh' \
  > /path/toi/output.log 2>&1

# 4) doc lai output.log, doi chieu voi so lieu da co trong bai truoc khi sua
```

## 6. Cảnh báo quan trọng: độ trễ Pi4 rất nhạy điều kiện đo

Raspberry Pi 4 không có tản nhiệt chủ động và dùng CPU governor tự điều
chỉnh tần số (`ondemand` theo mặc định). Đã quan sát thực tế chênh lệch
tới ~3,3 lần giữa hai phiên đo trên cùng thiết bị, cùng script, khác thời
điểm (một phiên 2026-08-08/09 cho median ~26,7 ms, phiên 2026-08-16 cho
median ~8,0 ms — xem `docs/PI4_BENCHMARK_GUIDE.md` mục "Kết quả tham
chiếu" để biết số liệu đầy đủ và cách bài xử lý chênh lệch này).

**Luôn chạy bước 2 ở §5 (kiểm tra governor/tần số/nhiệt độ/tải) ngay
trước khi benchmark**, và đính kèm kết quả đó khi báo cáo số liệu benchmark
lại cho người dùng — không chỉ gửi mỗi con số median/p95. Nếu số liệu lần
đo mới lệch nhiều so với lần trước, đây là dấu hiệu đầu tiên cần kiểm
tra, không phải giả định script hay model có vấn đề.

## 7. Kéo kết quả về và dọn dẹp

Không cần thao tác thêm nếu chỉ dùng `pi_ssh '... > log 2>&1'` như ở §5
bước 3 (output đã chảy thẳng về HPC qua stdout của lệnh SSH). Chỉ cần
`pi_scp` khi có file kết quả sinh ra trên chính Pi4 (ví dụ file `.json`
tự ghi bởi script), dạng:

```bash
pi_scp "$PI4_USER@$PI4_IP:~/ket_qua.json" ./results/pi4_latency/
```
