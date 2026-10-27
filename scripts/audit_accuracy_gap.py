"""Read-only accuracy/learning-curve audit; standard library only.

Run from any directory: python scripts/audit_accuracy_gap.py
No training, tensor imports, network calls, or writes to existing results.
"""
import csv
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def csv_summary(relative_path, tags=None):
    groups = defaultdict(list)
    seen = set()
    with (ROOT / relative_path).open() as stream:
        for row in csv.DictReader(stream):
            tag = row.get("tag", row["method"])
            if tags is not None and tag not in tags:
                continue
            seed = row.get("seed", "single")
            key = (tag, seed, row["subject"])
            if key in seen:
                raise ValueError(f"Duplicate subject result in {relative_path}: {key}")
            seen.add(key)
            groups[(tag, seed)].append(float(row["acc"]))
    per_tag = defaultdict(dict)
    for (tag, seed), values in groups.items():
        per_tag[tag][seed] = statistics.mean(values)
    return {
        tag: {
            "mean": statistics.mean(values.values()),
            "sample_sd": statistics.stdev(values.values()) if len(values) > 1 else None,
            "per_seed": values,
        }
        for tag, values in per_tag.items()
    }


def teacher_curve_summary():
    source = ROOT / "logs/train_teacher_full_11421.adminsm.tnut.local.log"
    clean = re.sub(r"\x1b\[[0-9;]*m", "", source.read_text())
    folds, current = [], []
    for line in clean.splitlines():
        fields = line.split()
        if len(fields) != 8 or not fields[0].isdigit():
            continue
        try:
            values = list(map(float, fields))
        except ValueError:
            continue
        if values[0] == 1 and current:
            folds.append(current)
            current = []
        current.append(values)
    if current:
        folds.append(current)
    if len(folds) != 5 or any(len(fold) != 120 for fold in folds):
        raise ValueError("Expected exactly five complete 120-epoch teacher curves")
    output = []
    for index, fold in enumerate(folds):
        # max retains the first occurrence on validation ties, matching trainer.
        short = max(fold[:30], key=lambda row: row[5])
        full = max(fold, key=lambda row: row[5])
        output.append({
            "fold": index,
            "first_30": {"epoch": int(short[0]), "val": short[5], "test": short[1]},
            "full_120": {"epoch": int(full[0]), "val": full[5], "test": full[1]},
        })
    return {
        "folds": output,
        "mean_test_first_30": statistics.mean(row["first_30"]["test"] for row in output),
        "mean_test_full_120": statistics.mean(row["full_120"]["test"] for row in output),
        "note": "Retrospective selection within the same teacher run, not a separate 30-epoch curriculum run.",
    }


def relation_gradient_summary():
    groups = defaultdict(list)
    tag = None
    source = ROOT / "logs/beta_fairness_diag.log"
    for line in source.read_text().splitlines():
        match = re.search(r"method=(\w+)", line)
        if match:
            tag = match[1]
        match = re.search(r"rawL=([0-9.e+-]+).*gradNormS=([0-9.e+-]+)", line)
        if match and tag:
            groups[tag].append(tuple(map(float, match.groups())))
    return {
        tag: {"n_epochs": len(values),
              "mean_raw_loss": statistics.mean(row[0] for row in values),
              "mean_weighted_relation_grad_norm": statistics.mean(row[1] for row in values)}
        for tag, values in groups.items()
    }


def main():
    sources = {
        "no_kd_alpha_0_5": ("results/seeds2_per_subject.csv", {"no_kd"}),
        "no_kd_alpha_1": ("results/no_kd_alpha1_2026_08_03/no_kd_alpha1_per_subject.csv", None),
        "kd_base": ("results/seeds_per_subject.csv", {"kd_base"}),
        "feature_kd": ("results/seeds2_per_subject.csv", {"feature_kd"}),
        "quantum": ("results/qrd_seeds_rerun_2026_07_30/seeds_quantum_rerun_per_subject.csv", None),
    }
    output = {name: csv_summary(path, tags) for name, (path, tags) in sources.items()}
    output["teacher_curves"] = teacher_curve_summary()
    output["relation_diagnostic"] = relation_gradient_summary()
    print(json.dumps(output, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
