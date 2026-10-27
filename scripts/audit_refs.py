"""Audit references.bib against Crossref: DOI validity + metadata match + editor rules.
Usage: python3 -I audit_refs.py <references.bib> <body.tex> <out_prefix>
"""
import sys, re, json, time, csv, difflib, urllib.request, urllib.error, urllib.parse

bib_path, tex_path, out = sys.argv[1], sys.argv[2], sys.argv[3]
UA = {"User-Agent": "qrd-eeg-ref-audit/1.0 (python-urllib)"}
ALLOWED = ["elsevier", "institute of electrical and electronics engineers", "ieee", "springer",
           "wiley", "nature", "frontiers", "informa", "taylor", "mdpi"]
SELF = [("nguyen", "phuong huy"), ("nguyen", "huy phuong"), ("duong", "thi mai thuong")]


def parse_bib(text):
    entries, i = [], 0
    while True:
        m = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,").search(text, i)
        if not m: break
        depth, j = 1, text.index("{", m.start()) + 1
        while depth and j < len(text):
            depth += {"{": 1, "}": -1}.get(text[j], 0); j += 1
        body = text[m.end():j - 1]
        fields, k = {}, 0
        for fm in re.finditer(r"(\w+)\s*=\s*", body):
            if fm.start() < k: continue
            name, p = fm.group(1).lower(), fm.end()
            if p < len(body) and body[p] == "{":
                d, q = 1, p + 1
                while d and q < len(body):
                    d += {"{": 1, "}": -1}.get(body[q], 0); q += 1
                val = body[p + 1:q - 1]
            else:
                q = body.find(",", p); q = len(body) if q < 0 else q
                val = body[p:q]
            fields[name] = val.strip().strip('"'); k = q
        entries.append(dict(type=m.group(1).lower(), key=m.group(2), **fields))
        i = j
    return entries


def norm(s):
    s = re.sub(r"\\[a-zA-Z]+\s*", " ", s or "")
    s = re.sub(r"[{}$\\]", "", s).lower()
    return re.sub(r"[^a-z0-9]+", " ", s).strip()


def sim(a, b):
    return difflib.SequenceMatcher(None, norm(a), norm(b)).ratio()


def first_family(author_field):
    a = (author_field or "").split(" and ")[0].strip()
    a = re.sub(r"[{}]", "", a)
    return (a.split(",")[0] if "," in a else a.split()[-1] if a.split() else "").strip()


def crossref(doi):
    url = "https://api.crossref.org/works/" + urllib.parse.quote(doi, safe="/()<>;:")
    for attempt in range(3):
        try:
            with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30) as r:
                return 200, json.load(r)["message"]
        except urllib.error.HTTPError as e:
            if e.code == 404: return 404, None
            time.sleep(2 + 3 * attempt)
        except Exception:
            time.sleep(2 + 3 * attempt)
    return -1, None


def doi_resolves(doi):
    req = urllib.request.Request("https://doi.org/" + doi, headers=UA, method="HEAD")
    try:
        class NoRedirect(urllib.request.HTTPRedirectHandler):
            def redirect_request(self, *a, **k): return None
        opener = urllib.request.build_opener(NoRedirect)
        opener.open(req, timeout=20)
        return True
    except urllib.error.HTTPError as e:
        return e.code in (301, 302, 303, 307, 308)
    except Exception:
        return False


def cr_year(m):
    for k in ("published-print", "published-online", "issued", "published"):
        dp = (m.get(k) or {}).get("date-parts")
        if dp and dp[0] and dp[0][0]: return dp[0][0]
    return None


entries = parse_bib(open(bib_path, encoding="utf-8").read())
tex = open(tex_path, encoding="utf-8").read()
tex = "\n".join(l for l in tex.splitlines() if not l.lstrip().startswith("%"))
cited = []
for cm in re.finditer(r"\\cite[a-zA-Z]*\*?(?:\[[^\]]*\])?\{([^}]*)\}", tex):
    for k in cm.group(1).split(","):
        k = k.strip()
        if k and k not in cited: cited.append(k)

rows = []
for n, e in enumerate(entries, 1):
    doi = re.sub(r"^https?://(dx\.)?doi\.org/", "", e.get("doi", "").strip(), flags=re.I)
    r = dict(key=e["key"], type=e["type"], year=e.get("year", ""), doi=doi,
             venue=e.get("journal") or e.get("booktitle") or e.get("publisher") or e.get("howpublished", ""),
             title=norm(e.get("title", ""))[:90], cited=e["key"] in cited,
             cite_order=(cited.index(e["key"]) + 1) if e["key"] in cited else "",
             cr_status="", cr_type="", cr_publisher="", cr_year="", title_sim="", author_ok="",
             venue_sim="", flags=[])
    fam = norm(first_family(e.get("author", "")))
    authors_norm = norm(e.get("author", ""))
    if any(f in authors_norm and g in authors_norm for f, g in SELF): r["flags"].append("SELF_CITATION")
    if not doi:
        r["flags"].append("NO_DOI")
    else:
        st, m = crossref(doi)
        r["cr_status"] = st
        if st == 200:
            ct = (m.get("title") or [""])[0]
            r["cr_type"] = m.get("type", ""); r["cr_publisher"] = m.get("publisher", "")
            r["cr_year"] = cr_year(m) or ""
            r["title_sim"] = round(sim(e.get("title", ""), ct), 2)
            fams = [norm(a.get("family") or a.get("name") or "") for a in m.get("author", [])]
            r["author_ok"] = (not fams) or any(fam and (fam == f or fam in f or f in fam) for f in fams[:3])
            cont = (m.get("container-title") or [""])[0]
            if r["venue"] and cont: r["venue_sim"] = round(sim(r["venue"], cont), 2)
            if r["title_sim"] < 0.85: r["flags"].append("TITLE_MISMATCH(cr: %s)" % ct[:80])
            if not r["author_ok"]: r["flags"].append("AUTHOR_MISMATCH(cr first: %s)" % (fams[0] if fams else "?"))
            try:
                if r["cr_year"] and abs(int(r["year"]) - int(r["cr_year"])) > 1:
                    r["flags"].append("YEAR_MISMATCH(cr %s)" % r["cr_year"])
                elif r["cr_year"] and int(r["year"]) != int(r["cr_year"]):
                    r["flags"].append("YEAR_DIFF_1(cr %s)" % r["cr_year"])
            except ValueError:
                r["flags"].append("YEAR_UNPARSABLE")
            if r["venue_sim"] != "" and r["venue_sim"] < 0.6 and e["type"] == "article":
                r["flags"].append("VENUE_DIFF(cr: %s)" % cont[:60])
            if r["cr_type"] != "journal-article": r["flags"].append("NOT_JOURNAL(%s)" % r["cr_type"])
            if not any(a in r["cr_publisher"].lower() for a in ALLOWED): r["flags"].append("PUBLISHER_CHECK")
            for upd in m.get("update-to", []) or []:
                if "retract" in (upd.get("type") or "").lower(): r["flags"].append("RETRACTION_NOTICE")
            if any("retract" in (t or "").lower() for t in (m.get("title") or [])): r["flags"].append("RETRACTED?")
        elif st == 404:
            r["flags"].append("DOI_NOT_IN_CROSSREF" + ("(resolves via doi.org)" if doi_resolves(doi) else "(DOES NOT RESOLVE)"))
        else:
            r["flags"].append("CROSSREF_ERROR")
        time.sleep(0.25)
    if e["type"] != "article": r["flags"].append("BIBTYPE_" + e["type"].upper())
    try:
        if int(r["year"]) < 2021: r["flags"].append("OLDER_THAN_5Y")
    except ValueError:
        pass
    if not r["cited"]: r["flags"].append("NOT_CITED")
    rows.append(r)
    print(f"[{n:3d}/{len(entries)}] {e['key']:<32} {r['cr_status']!s:>4} {';'.join(r['flags'])}", flush=True)

# duplicates
for i in range(len(rows)):
    for j in range(i + 1, len(rows)):
        a, b = rows[i], rows[j]
        if (a["doi"] and a["doi"].lower() == b["doi"].lower()) or (a["title"] and sim(a["title"], b["title"]) > 0.95):
            a["flags"].append("DUPLICATE_OF " + b["key"]); b["flags"].append("DUPLICATE_OF " + a["key"])
missing = [k for k in cited if k not in {r["key"] for r in rows}]

with open(out + ".tsv", "w", newline="", encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter="\t")
    w.writeheader()
    for r in rows: w.writerow({**r, "flags": "; ".join(r["flags"])})
json.dump(dict(rows=rows, cited_order=cited, missing_in_bib=missing), open(out + ".json", "w"), indent=1, default=str)
print("cited keys:", len(cited), "| missing in bib:", missing)
