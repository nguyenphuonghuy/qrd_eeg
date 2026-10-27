################################################################
# scripts/export_student_pi4.py  (qrd_eeg)
# Xuat kien truc student THAT da dung de huan luyen (EEGNetv4_class trong
# external/Ensemble-MI/models/eegnet.py) thanh TorchScript doc lap, dung
# de do do tre suy luan that tren Raspberry Pi 4 (khong can braindecode/
# mne o phia Pi4, chi can torch).
#
# SUA 2026-10-03 (audit docs/AUDIT_PAPER_CODE_2026_10_03.md muc 2): ban
# truoc day import tu braindecode.models.EEGNetv4 (kien truc THU VIEN),
# khac that voi EEGNetv4_class ma initializers.py/train_all.py dung de
# huan luyen (khac so layer BatchNorm, activation block 2, cau truc lop
# phan loai cuoi). Script nay sua lai dung dung class goc.
#
# Trong so NGAU NHIEN (co seed de tai lap): do tre suy luan chi phu thuoc
# kien truc/kich thuoc tensor, khong phu thuoc GIA TRI trong so.
################################################################
import os, sys, torch
import torch.nn as nn

sys.dont_write_bytecode = True
_REPO = os.environ.get("ENSEMBLE_MI_DIR")
if not _REPO or not os.path.isdir(_REPO):
    sys.exit("ERROR: dat bien ENSEMBLE_MI_DIR tro toi external/Ensemble-MI")
if _REPO not in sys.path: sys.path.insert(0, _REPO)

from models import EEGNetv4_class

torch.manual_seed(20200220)

N_ELECTRODES = 64
WINDOW_SIZE = 300
N_CLASSES = 2

# Tham so khop chinh xac voi initializers.py::init_net khi net_cls=="eegnet"
# va args.backbone_k_width=1, args.dropout_input=0.4, args.dropout_1=0.1
# (cau hinh dung trong moi job huan luyen cua bai, xem jobs/*.pbs).
net = EEGNetv4_class(
    in_chans=N_ELECTRODES,
    n_classes=N_CLASSES,
    input_window_samples=WINDOW_SIZE,
    final_conv_length="auto",
    pool_mode="max",
    F1=1 * 8,
    D=2,
    F2=1 * 16,
    kernel_length=64,
    dropout_input_prob=0.4,
    dropout_1_prob=0.1,
)
net.eval()


class ScoresOnly(nn.Module):
    """EEGNetv4_class.forward tra ve dict {'feats','scores'}; TorchScript
    tracing va benchmark chi can tensor logits cuoi cung (quyet dinh phan
    loai mot lenh), giong nhu luc trien khai thuc te chi can 'scores'."""
    def __init__(self, inner):
        super().__init__()
        self.inner = inner

    def forward(self, x):
        return self.inner(x)["scores"]


wrapped = ScoresOnly(net)
wrapped.eval()

example = torch.randn(1, N_ELECTRODES, WINDOW_SIZE)
with torch.no_grad():
    out = wrapped(example)
print("output shape:", tuple(out.shape))

traced = torch.jit.trace(wrapped, example)
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

n_params = sum(p.numel() for p in net.parameters())
print("So tham so (phai khop 2402 trong bai):", n_params)
