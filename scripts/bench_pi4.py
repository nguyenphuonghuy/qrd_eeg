################################################################
# scripts/bench_pi4.py  (qrd_eeg)
# Chay TREN Raspberry Pi 4 (hoac may bat ky co torch CPU). CHI can `torch`,
# khong can braindecode/mne. Do do tre suy luan cua student (EEGNetv4)
# da xuat bang export_student_pi4.py.
#
# Dung: python3 bench_pi4.py student_eegnetv4_traced.pt
################################################################
import sys, time, statistics
import torch

# KHONG goi torch.set_num_threads(): giu mac dinh cua PyTorch, dung y het
# giao thuc da dung cho Bang tab:tre (khong cau hinh so luong dac biet).

MODEL_PATH = sys.argv[1] if len(sys.argv) > 1 else "student_eegnetv4_traced.pt"
N_ELECTRODES = 64
WINDOW_SIZE = 300
N_WARMUP = 20   # khop Bang tab:tre
N_REPS = 200    # khop Bang tab:tre

model = torch.jit.load(MODEL_PATH)
model.eval()

x = torch.randn(1, N_ELECTRODES, WINDOW_SIZE)

with torch.no_grad():
    for _ in range(N_WARMUP):
        model(x)

lat_ms = []
with torch.no_grad():
    for _ in range(N_REPS):
        t0 = time.perf_counter()
        model(x)
        t1 = time.perf_counter()
        lat_ms.append((t1 - t0) * 1000.0)

lat_ms.sort()
median = statistics.median(lat_ms)
mean = statistics.mean(lat_ms)
p25 = lat_ms[int(0.25 * N_REPS)]
p75 = lat_ms[int(0.75 * N_REPS)]
p95 = lat_ms[int(0.95 * N_REPS)]

print(f"N_REPS={N_REPS} (sau {N_WARMUP} warm-up)")
print(f"median = {median:.3f} ms")
print(f"mean   = {mean:.3f} ms")
print(f"p25    = {p25:.3f} ms")
print(f"p75    = {p75:.3f} ms")
print(f"p95    = {p95:.3f} ms")
print(f"min/max = {lat_ms[0]:.3f} / {lat_ms[-1]:.3f} ms")
