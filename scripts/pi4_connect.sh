################################################################
# scripts/pi4_connect.sh  (qrd_eeg)
# Nap bien PI4_USER/PI4_PASS/PI4_IP/TS_BIN/TS_SOCK tu
# scripts/.pi4_credentials.local, roi dinh nghia pi_ssh()/pi_scp() de
# goi lenh tren Raspberry Pi 4 thang tu login node HPC nay, khong can
# may Windows trung gian. Xem docs/PI4_SSH_GUIDE.md de biet boi canh day
# du va cach xu ly khi gap loi.
#
# Dung: source scripts/pi4_connect.sh
#       pi_ssh 'hostname && uname -a'
#       pi_scp local_file "$PI4_USER@$PI4_IP:~/dich/"
################################################################
_CRED="$(dirname "${BASH_SOURCE[0]}")/.pi4_credentials.local"
if [ ! -f "$_CRED" ]; then
  echo "LOI: khong thay $_CRED. Tao file nay voi PI4_USER/PI4_PASS/PI4_IP/TS_BIN/TS_SOCK (hoi nguoi dung neu khong biet)." >&2
  return 1 2>/dev/null || exit 1
fi
set -a
source "$_CRED"
set +a

if [ ! -S "$TS_SOCK" ]; then
  echo "LOI: khong thay socket tailscaled tai $TS_SOCK. Kiem tra: ps aux | grep tailscaled" >&2
  echo "Neu chua chay, khoi dong bang: \$HOME/tailscale/start-tailscaled.sh" >&2
  return 1 2>/dev/null || exit 1
fi

pi_ssh() {
  sshpass -p "$PI4_PASS" ssh -o StrictHostKeyChecking=accept-new -o ConnectTimeout=15 \
    -o ProxyCommand="$TS_BIN --socket=$TS_SOCK nc %h %p" \
    "$PI4_USER@$PI4_IP" "$@"
}

pi_scp() {
  sshpass -p "$PI4_PASS" scp -o StrictHostKeyChecking=accept-new \
    -o ProxyCommand="$TS_BIN --socket=$TS_SOCK nc %h %p" \
    "$@"
}
