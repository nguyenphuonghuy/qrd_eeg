#!/bin/bash
# Chay bench_pi4.py 5 LAN DOC LAP (moi lan mot tien trinh python rieng),
# roi tinh trung binh +/- do lech chuan qua 5 lan, thay vi tin vao 1 lan.
N=5
MEDIANS=""
P95S=""

for i in $(seq 1 $N); do
  echo "=== Lan chay $i/$N ==="
  OUT=$(python3 bench_pi4.py student_eegnetv4_traced.pt)
  echo "$OUT"
  MED=$(echo "$OUT" | awk '/^median/{print $3}')
  P95=$(echo "$OUT" | awk '/^p95/{print $3}')
  MEDIANS="$MEDIANS $MED"
  P95S="$P95S $P95"
  echo ""
done

MEDIANS_CSV=$(echo $MEDIANS | xargs | tr ' ' ',')
P95S_CSV=$(echo $P95S | xargs | tr ' ' ',')

echo "=== TONG HOP $N LAN CHAY DOC LAP ==="
python3 -c "
import statistics
medians = [$MEDIANS_CSV]
p95s = [$P95S_CSV]
print(f'median qua {len(medians)} lan: mean={statistics.mean(medians):.3f} sd={statistics.stdev(medians):.3f} ms | gia tri: {medians}')
print(f'p95    qua {len(p95s)} lan: mean={statistics.mean(p95s):.3f} sd={statistics.stdev(p95s):.3f} ms | gia tri: {p95s}')
"
