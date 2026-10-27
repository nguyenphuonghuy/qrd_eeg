"""Kiem anh xa 1:1 giua ban tieng Viet va cac ban tieng Anh cua bai bao.

So sanh: chuoi muc (section/subsection/subsubsection/paragraph), nhan \\label,
so bang/hinh/phuong trinh, so doan van trong tung muc, tap khoa \\cite.
Bo qua dong comment va muc \\section*{Acknowledgments} (ban IJRCS dat loi cam on
trong template). Thoat ma 1 neu co khac biet.

Dung: python3 -I scripts/check_vi_en_sync.py paper/body.tex paper/body_en.tex \\
          paper/ijrcs_submission/body_en.tex
"""
import re, sys


def load(path):
    lines = [l for l in open(path, encoding="utf-8").read().splitlines() if not l.lstrip().startswith("%")]
    text = "\n".join(lines)
    text = re.split(r"\\ifdefined\\IJRCSsubmission|\\section\*\{(?:Acknowledg|Lời cảm ơn)", text)[0]
    cites = {k.strip() for m in re.finditer(r"\\cite[a-zA-Z]*\{([^}]*)\}", text, re.S)
             for k in m.group(1).split(",") if k.strip()}
    labels = re.findall(r"\\label\{([^}]+)\}", text)
    envs = {e: len(re.findall(r"\\begin\{%s\}" % e, text)) for e in ("table", "figure", "equation")}
    secs, cur, para, inblk = [], "PRE", 0, False
    for line in text.splitlines():
        m = re.match(r"\\(section|subsection|subsubsection|paragraph)\*?\{", line.strip())
        if m:
            if inblk: para += 1
            secs.append((cur, para)); cur, para, inblk = m.group(1), 0, False
            continue
        if not line.strip():
            if inblk: para += 1
            inblk = False
        else:
            inblk = True
    if inblk: para += 1
    secs.append((cur, para))
    return dict(cites=cites, labels=labels, envs=envs, secs=secs)


def main(paths):
    docs = [load(p) for p in paths]
    ref, ok = docs[0], True
    for p, d in zip(paths[1:], docs[1:]):
        print(f"== {paths[0]}  vs  {p}")
        if d["labels"] != ref["labels"]:
            ok = False; print("  KHAC nhan:", sorted(set(ref["labels"]) ^ set(d["labels"])) or "(cung tap, khac thu tu)")
        if d["envs"] != ref["envs"]:
            ok = False; print("  KHAC so moi truong:", ref["envs"], "vs", d["envs"])
        if [s for s, _ in d["secs"]] != [s for s, _ in ref["secs"]]:
            ok = False; print("  KHAC chuoi muc:", len(ref["secs"]), "vs", len(d["secs"]))
        else:
            for i, ((s, a), (_, b)) in enumerate(zip(ref["secs"], d["secs"])):
                if a != b:
                    ok = False; print(f"  KHAC so doan o muc thu {i} ({s}, nhan gan nhat theo thu tu): {a} vs {b}")
        if d["cites"] != ref["cites"]:
            ok = False
            print("  Chi co o ban dau:", sorted(ref["cites"] - d["cites"]))
            print("  Chi co o ban sau:", sorted(d["cites"] - ref["cites"]))
    print("KET QUA:", "KHOP 1:1" if ok else "CO KHAC BIET")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
