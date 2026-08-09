################################################################
# scripts/export_student_pi4.py  (qrd_eeg)
# Xuat kien truc student (EEGNetv4) thanh TorchScript doc lap, dung
# de do do tre suy luan that tren Raspberry Pi 4 (khong can braindecode/
# mne o phia Pi4, chi can torch).
# Trong so NGAU NHIEN (co seed de tai lap): do tre suy luan chi phu thuoc
# kien truc/kich thuoc tensor, khong phu thuoc GIA TRI trong so.
################################################################
import os, sys, torch

sys.dont_write_bytecode = True
_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path: sys.path.insert(0, _REPO)

from braindecode.models import EEGNetv4

torch.manual_seed(20200220)

N_ELECTRODES = 64
WINDOW_SIZE = 300
N_CLASSES = 2

net = EEGNetv4(
    n_chans=N_ELECTRODES,
    n_outputs=N_CLASSES,
    n_times=WINDOW_SIZE,
    chs_info=[{"ch_name": f"E{i}"} for i in range(N_ELECTRODES)],
    sfreq=100,
    final_conv_length="auto",
    pool_mode="max",
    F1=8, D=2, F2=16, kernel_length=64,
    drop_prob=0.4,  # khong anh huong latency (dropout la no-op o eval())
)
net.eval()

example = torch.randn(1, N_ELECTRODES, WINDOW_SIZE)
with torch.no_grad():
    out = net(example)
print("output shape:", tuple(out.shape))

traced = torch.jit.trace(net, example)
out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "pi4_latency")
os.makedirs(out_dir, exist_ok=True)
out_path = os.path.join(out_dir, "student_eegnetv4_traced.pt")
traced.save(out_path)
print("Saved:", out_path, "size(KB)=", os.path.getsize(out_path) / 1024)

# sanity: reload va so sanh output voi ban goc
reloaded = torch.jit.load(out_path)
with torch.no_grad():
    out2 = reloaded(example)
diff = (out - out2).abs().max().item()
print("max abs diff (goc vs traced-reload):", diff)
assert diff < 1e-5, "Traced model KHONG khop model goc"
print("OK: traced model khop model goc.")
