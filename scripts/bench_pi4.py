################################################################
# scripts/bench_pi4.py  (qrd_eeg)
# Chay TREN Raspberry Pi 4 (hoac may bat ky co torch CPU). CHI can `torch`,
# khong can braindecode/mne. Do do tre suy luan cua student (EEGNetv4)
# hoac teacher (EnsembleEEG) da xuat bang export_student_pi4.py /
# export_teacher_pi4.py, cong voi RAM tien trinh chiem dung
# (resource.getrusage, don vi KB tren Linux).
#
# Dung cho student (input la tensor thuong):
#   python3 bench_pi4.py student_eegnetv4_traced.pt
# Dung cho teacher (input phai la dict {'x': tensor}, xem
# export_teacher_pi4.py ve ly do EnsembleEEG.forward doi hoi dict):
#   python3 bench_pi4.py teacher_ensembleeeg_traced.pt --dict-input
#
# LUU Y VE RAM DO DUOC: ru_maxrss la RSS DINH CUA CA TIEN TRINH PYTHON,
# gom ca interpreter + thu vien PyTorch da nap + trong so model + bo dem
# noi bo cua PyTorch allocator, KHONG chi rieng activation tensor cua
# model. Day la con so khac ve ban chat so voi uoc tinh "activation dinh
# ~600 KB" tinh giai tich trong bai (chi tinh rieng activation). In ca
# hai moc RSS (sau khi nap model, va dinh sau vong lap suy luan) de tach
# phan "footprint tinh" (nap model+framework) khoi phan "tang them do
# chay suy luan".
################################################################
import sys, time, statistics, resource
import torch

# KHONG goi torch.set_num_threads(): giu mac dinh cua PyTorch, dung y het
# giao thuc da dung cho Bang tab:tre (khong cau hinh so luong dac biet).

_args = [a for a in sys.argv[1:] if not a.startswith("--")]
DICT_INPUT = "--dict-input" in sys.argv[1:]
MODEL_PATH = _args[0] if _args else "student_eegnetv4_traced.pt"
N_ELECTRODES = 64
WINDOW_SIZE = 300
N_WARMUP = 20   # khop Bang tab:tre
N_REPS = 200    # khop Bang tab:tre

model = torch.jit.load(MODEL_PATH)
model.eval()

rss_after_load_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

x = torch.randn(1, N_ELECTRODES, WINDOW_SIZE)
model_input = {"x": x} if DICT_INPUT else x

with torch.no_grad():
    for _ in range(N_WARMUP):
        model(model_input)

lat_ms = []
with torch.no_grad():
    for _ in range(N_REPS):
        t0 = time.perf_counter()
        model(model_input)
        t1 = time.perf_counter()
        lat_ms.append((t1 - t0) * 1000.0)

rss_peak_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss

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
# ru_maxrss la high-water mark RSS CUA CA TIEN TRINH tu luc khoi dong toi
# thoi diem goi, khong phai RSS tuc thoi; don vi tren Linux la KiB (sua
# audit muc 9, nhan dung dinh nghia va don vi MiB thay vi MB).
print(f"rss_after_load_highwater = {rss_after_load_kb / 1024.0:.2f} MiB")
print(f"rss_peak_highwater       = {rss_peak_kb / 1024.0:.2f} MiB")
