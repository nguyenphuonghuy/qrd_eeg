#!/bin/bash
# setup_env.sh — cai tron env qrd_env sau khi conda tao xong Python 3.11.
# Chay: bash scripts/setup_env.sh
# Bai hoc da nhung san:
#   - CONDA_PKGS_DIRS tro sang cho ghi duoc (tranh /opt/anaconda3/pkgs read-only)
#   - torch cu118 cai TRUOC, cung lenh voi torchvision (tranh keo nguoc CUDA sai)
#   - braindecode 1.4.0 (can Python >=3.11) + moabb 1.5.0 (da fix windowing/naming)
set -e

ENV=/gpfs0/users/gv_nphuy/envs/qrd_env
PY=$ENV/bin/python
export CONDA_PKGS_DIRS=/gpfs0/users/gv_nphuy/conda_pkgs

echo "===== 0. KIEM ENV TON TAI ====="
if [ ! -x "$PY" ]; then
  echo "LOI: $PY chua co. Cho conda create xong da roi chay lai." ; exit 1
fi
$PY --version

echo "===== 1. TORCH cu118 (TRUOC TIEN, cung lenh voi torchvision) ====="
$PY -m pip install --no-cache-dir \
    torch==2.7.1+cu118 torchvision==0.22.1+cu118 \
    --index-url https://download.pytorch.org/whl/cu118

echo "===== 2. VERIFY torch dung build TRUOC khi cai tiep ====="
$PY -m pip show torch | grep -i version
$PY -m pip show torchvision | grep -i version

echo "===== 3. PHAN CON LAI (braindecode 1.4.0 + moabb 1.5.0 + ...) ====="
# Sua audit docs/AUDIT_PAPER_CODE_2026_10_03.md muc 10: truoc day cac goi
# nay khong pin phien ban, nen cau "version-pinned software environment"
# cuoi bai khong co co so trong repo. Pin dung phien ban da dung de tao
# ket qua trong bai (xem requirements-lock_2026-10-03.txt, sinh bang
# "pip freeze" tren chinh qrd_env dang dung).
$PY -m pip install --no-cache-dir \
    "braindecode==1.4.0" "moabb==1.5.0" "mne==1.12.1" \
    "pennylane==0.45.1" "scikit-learn==1.9.0" "pyriemann==0.12" \
    "openpyxl==3.1.5" "pandas==3.0.3" "numpy==2.4.4" "scipy==1.17.1"

echo "===== 4. VERIFY torch KHONG bi doi sau khi cai them (TROUBLESHOOTING muc 5) ====="
$PY -m pip show torch | grep -i version
echo "--- pip check ---"
$PY -m pip check || echo "(pip check co canh bao — doc ky o tren)"

echo "===== 5. TOM TAT PHIEN BAN ====="
$PY -m pip list 2>/dev/null | grep -iE "^torch |^torchvision |braindecode|moabb|^mne |pennylane|scikit-learn|pyriemann|openpyxl|pandas"

echo ""
echo "===== SETUP ENV XONG. Buoc sau: verify import qua PBS (KHONG import nang tren login node). ====="
