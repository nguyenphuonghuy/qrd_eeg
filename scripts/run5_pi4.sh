#!/bin/bash
# Chay bench_pi4.py 5 LAN DOC LAP (moi lan mot tien trinh python rieng),
# roi tinh trung binh +/- do lech chuan qua 5 lan, thay vi tin vao 1 lan.
#
# Dung: bash run5_pi4.sh [model.pt] [--dict-input]
#   Mac dinh: student_eegnetv4_traced.pt (input tensor thuong)
#   Vi du cho teacher: bash run5_pi4.sh teacher_ensembleeeg_traced.pt --dict-input
MODEL="${1:-student_eegnetv4_traced.pt}"
EXTRA_FLAG="${2:-}"
N=5
MEDIANS=""
P95S=""
RSS_LOADS=""
RSS_PEAKS=""

for i in $(seq 1 $N); do
  echo "=== Lan chay $i/$N ($MODEL $EXTRA_FLAG) ==="
  OUT=$(python3 bench_pi4.py "$MODEL" $EXTRA_FLAG)
  echo "$OUT"
  MED=$(echo "$OUT" | awk '/^median/{print $3}')
  P95=$(echo "$OUT" | awk '/^p95/{print $3}')
  RSS_LOAD=$(echo "$OUT" | awk '/^rss_after_load_highwater/{print $3}')
  RSS_PEAK=$(echo "$OUT" | awk '/^rss_peak_highwater/{print $3}')
  MEDIANS="$MEDIANS $MED"
  P95S="$P95S $P95"
  RSS_LOADS="$RSS_LOADS $RSS_LOAD"
  RSS_PEAKS="$RSS_PEAKS $RSS_PEAK"
  echo ""
done

MEDIANS_CSV=$(echo $MEDIANS | xargs | tr ' ' ',')
P95S_CSV=$(echo $P95S | xargs | tr ' ' ',')
RSS_LOADS_CSV=$(echo $RSS_LOADS | xargs | tr ' ' ',')
RSS_PEAKS_CSV=$(echo $RSS_PEAKS | xargs | tr ' ' ',')

echo "=== TONG HOP $N LAN CHAY DOC LAP ==="
python3 -c "
import statistics
medians = [$MEDIANS_CSV]
p95s = [$P95S_CSV]
rss_loads = [$RSS_LOADS_CSV]
rss_peaks = [$RSS_PEAKS_CSV]
print(f'median qua {len(medians)} lan: mean={statistics.mean(medians):.3f} sd={statistics.stdev(medians):.3f} ms | gia tri: {medians}')
print(f'p95    qua {len(p95s)} lan: mean={statistics.mean(p95s):.3f} sd={statistics.stdev(p95s):.3f} ms | gia tri: {p95s}')
print(f'rss_after_load_highwater qua {len(rss_loads)} lan: mean={statistics.mean(rss_loads):.2f} sd={statistics.stdev(rss_loads):.2f} MiB | gia tri: {rss_loads}')
print(f'rss_peak_highwater       qua {len(rss_peaks)} lan: mean={statistics.mean(rss_peaks):.2f} sd={statistics.stdev(rss_peaks):.2f} MiB | gia tri: {rss_peaks}')
"
