#!/usr/bin/env python3
"""
Sinh file .drawio (mxGraph XML) cho Hinh 1 (khung teacher-student QRD),
noi dung khop body.tex, phong cach phang (khong gradient/do bong/icon),
de mo bang draw.io / diagrams.net va chinh tay truc quan.

Cong thuc duoc viet bang cu phap LaTeX that, boc trong $...$, va file da
tu bat san "Mathematical Typesetting" (math="1") nen draw.io se render
dung ngay khi mo, khong can bat tay qua menu Extras.

Chay: python3 gen_fig1_drawio.py > fig1_khung.drawio
(Khong can torch/mne/braindecode -- chay thang tren login node cung duoc.)
"""
import html
import re

CBLUE = "#1565C0"; CBLUEBG = "#E3F2FD"
CGREEN = "#2E7D32"; CGREENBG = "#E8F5E9"
CORANGE = "#E65100"; CORANGEBG = "#FFF3E0"
CPURPLE = "#6A1B9A"; CPURPLEBG = "#F3E5F5"
CGRAY = "#616161"; CGRAYBG = "#F5F5F5"
CDARK = "#424242"  # tieu de/vien trung tinh -- KHONG dung cho 4 co che chung cat

_id = [0]
def nid():
    _id[0] += 1
    return f"n{_id[0]}"

cells = []

def mathify(s):
    # draw.io/MathJax KHONG nhan dien $...$ -- phai la \(...\) (inline)
    # hoac $$...$$ (display). Chuyen tat ca cap $...$ trong label thanh
    # \(...\) tu dong, de code phia tren van viet $...$ cho de doc.
    return re.sub(r"\$([^$]+)\$", r"\\(\1\\)", s)

def esc(s):
    s = mathify(s)
    # KHONG dung html.escape() cho toan chuoi vi no doi ' thanh &#x27;
    # lam MathJax kho chiu voi mot so cu phap; chi thay & < > can thiet.
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace("\n", "&#10;")

def box(x, y, w, h, label, stroke, fill, font=11, bold=False, dashed=False,
        italic=False, align="center", valign="middle"):
    i = nid()
    style = (f"rounded=1;arcSize=10;whiteSpace=wrap;html=1;"
             f"strokeColor={stroke};fillColor={fill};fontSize={font};"
             f"align={align};verticalAlign={valign};spacing=4;")
    if bold: style += "fontStyle=1;"
    if italic: style += "fontStyle=2;"
    if dashed: style += "dashed=1;"
    cells.append(
        f'<mxCell id="{i}" value="{esc(label)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i

def outerbox(x, y, w, h, stroke, dashed=False):
    i = nid()
    style = (f"rounded=1;arcSize=6;whiteSpace=wrap;html=1;strokeColor={stroke};"
             f"fillColor=none;verticalAlign=top;")
    if dashed: style += "dashed=1;"
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="{h}" as="geometry"/></mxCell>')
    return i

def title(x, y, w, text, color, size=15):
    i = nid()
    style = (f"text;html=1;align=center;verticalAlign=middle;fontStyle=1;"
             f"fontSize={size};fontColor={color};")
    cells.append(
        f'<mxCell id="{i}" value="{esc(text)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x}" y="{y}" width="{w}" height="26" as="geometry"/></mxCell>')
    return i

def arrow(src, dst, dashed=False, color=CGRAY, label=None, exitxy=None, entryxy=None):
    i = nid()
    style = (f"edgeStyle=orthogonalEdgeStyle;rounded=0;html=1;"
             f"strokeColor={color};endArrow=block;endFill=1;strokeWidth=1.4;")
    if dashed: style += "dashed=1;"
    if exitxy: style += f"exitX={exitxy[0]};exitY={exitxy[1]};exitDx=0;exitDy=0;"
    if entryxy: style += f"entryX={entryxy[0]};entryY={entryxy[1]};entryDx=0;entryDy=0;"
    lbl = esc(label) if label else ""
    cells.append(
        f'<mxCell id="{i}" value="{lbl}" style="{style}" edge="1" parent="1" '
        f'source="{src}" target="{dst}"><mxGeometry relative="1" as="geometry"/></mxCell>')
    return i

# ---------------------------------------------------------------------
# Icon nho, thuan trang tri (khong mang y nghia mau -- luon xam trung tinh),
# dat trong dung khung toa do da danh rieng nen KHONG lam xe dich bat ky
# khoi nao khac trong hinh.
# ---------------------------------------------------------------------
def small_rect(x, y, w, h, stroke=CGRAY, fill="#EEEEEE"):
    i = nid()
    style = f"rounded=0;whiteSpace=wrap;html=1;strokeColor={stroke};fillColor={fill};"
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')
    return i

def floating_line(pts, stroke=CGRAY, w=1.2, curved=False):
    i = nid()
    style = (f"edgeStyle=none;html=1;strokeColor={stroke};strokeWidth={w};"
             f"endArrow=none;startArrow=none;")
    if curved: style += "curved=1;"
    mid = "".join(f'<mxPoint x="{px:.1f}" y="{py:.1f}"/>' for px, py in pts[1:-1])
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" edge="1" parent="1">'
        f'<mxGeometry relative="1" as="geometry">'
        f'<mxPoint x="{pts[0][0]:.1f}" y="{pts[0][1]:.1f}" as="sourcePoint"/>'
        f'<mxPoint x="{pts[-1][0]:.1f}" y="{pts[-1][1]:.1f}" as="targetPoint"/>'
        f'<Array as="points">{mid}</Array>'
        f'</mxGeometry></mxCell>')
    return i

def icon_bars(x, y, w, h, heights=(0.5, 1.0, 0.7, 0.4)):
    n = len(heights)
    bw = w / n - 3
    cx = x
    for hf in heights:
        bh = h * hf
        small_rect(cx, y + h - bh, bw, bh)
        cx += bw + 3

def icon_grid(x, y, w, h, rows=2, cols=3):
    cw = w / cols - 3
    ch = h / rows - 3
    for r in range(rows):
        for c in range(cols):
            small_rect(x + c * (cw + 3), y + r * (ch + 3), cw, ch)

def icon_stack(x, y, w, h, n=3):
    bw = w / n
    for k in range(n):
        rw = bw * 0.75
        rh = h * (1 - k * 0.18)
        small_rect(x + k * bw, y + (h - rh) / 2, rw, rh)

def icon_wave(x, y, w, h):
    import math
    n = 24
    pts = []
    for k in range(n + 1):
        px = x + w * k / n
        py = y + h / 2 + (h / 2 - 1) * math.sin(k * 1.15) * (0.55 if k % 3 == 0 else 1.0)
        pts.append((px, py))
    floating_line(pts, w=1.1, curved=True)

def icon_circuit(x, y, w, h, nlines=3):
    for r in range(nlines):
        ly = y + h * (r + 0.5) / nlines
        floating_line([(x, ly), (x + w, ly)], w=1.0)
    gs = min(w / 5, h / nlines) * 0.6
    gate_pos = [(0.22, 0), (0.55, 1), (0.82, 0), (0.4, 2), (0.7, 1)]
    for gx, gr in gate_pos:
        px = x + w * gx - gs / 2
        py = y + h * (gr + 0.5) / nlines - gs / 2
        small_rect(px, py, gs, gs)

def icon_dots_arrow(x, y, w, h):
    r = min(w, h) * 0.16
    small_rect(x, y + h * 0.25 - r, r * 2, r * 2, fill="#90CAF9")
    small_rect(x, y + h * 0.65 - r, r * 2, r * 2, fill="#90CAF9")
    floating_line([(x + r * 2 + 3, y + h * 0.25), (x + w * 0.55, y + h * 0.45)])
    floating_line([(x + r * 2 + 3, y + h * 0.65), (x + w * 0.55, y + h * 0.45)])
    small_rect(x + w * 0.6, y + h * 0.45 - r, r * 2, r * 2, fill="#A5D6A7")
    small_rect(x + w * 0.8, y + h * 0.3 - r, r * 2, r * 2, fill="#A5D6A7")

# =====================================================================
# (A) Input / Teacher / Student / Ground-truth / Update
# =====================================================================
input_b = box(20, 275, 190, 140,
    "Input\nEEG--MI mini-batch\n$X=\\{x_i\\}_{i=1}^{N}$\n($C$ channels $\\times$ $T$ time)\nBatch size: $N$",
    CGRAY, CGRAYBG, bold=False)

# Teacher (trung tinh -- mau chi danh cho 4 co che chung cat, khong danh
# cho truc teacher/student; teacher/student da phan biet ro qua vi tri + nhan chu)
# Moi khoi tach icon (trai) + chu (phai) nhung GIU NGUYEN tong khung
# toa do cu (x,y,w,h) nen khong lam xe dich bat ky khoi nao khac.
icon_stack(304, 124, 44, 62)
t_back = box(352, 120, 78, 70, "Backbone\n(e.g., Ensemble-MI)", CGRAY, CGRAYBG, font=9)
t_pool = box(470, 130, 100, 50, "Global Pooling", CGRAY, CGRAYBG)
icon_bars(614, 86, 40, 48)
t_logit = box(658, 80, 132, 60, "Logits (softmax)\n$Z_T \\in \\mathbb{R}^{C\\times N}$", CGRAY, CGRAYBG, font=10)
icon_grid(614, 198, 40, 44)
t_feat = box(658, 190, 132, 60, "Features\n$F_T \\in \\mathbb{R}^{d\\times N}$", CGRAY, CGRAYBG, font=10)
arrow(t_back, t_pool); arrow(t_pool, t_logit); arrow(t_pool, t_feat)
teacher_outer = outerbox(260, 40, 560, 260, CGRAY)
teacher_title = title(260, 12, 560, "Teacher Network (fixed)", CDARK)

# Student
icon_stack(304, 464, 44, 62)
s_back = box(352, 460, 78, 70, "Backbone\n(e.g., EEGNet)", CGRAY, CGRAYBG, font=9)
s_pool = box(470, 470, 100, 50, "Global Pooling", CGRAY, CGRAYBG)
icon_bars(614, 426, 40, 48)
s_logit = box(658, 420, 132, 60, "Logits (softmax)\n$Z_S \\in \\mathbb{R}^{C\\times N}$", CGRAY, CGRAYBG, font=10)
icon_grid(614, 538, 40, 44)
s_feat = box(658, 530, 132, 60, "Features\n$F_S \\in \\mathbb{R}^{d\\times N}$", CGRAY, CGRAYBG, font=10)
arrow(s_back, s_pool); arrow(s_pool, s_logit); arrow(s_pool, s_feat)
student_outer = outerbox(260, 380, 560, 260, CGRAY)
student_title = title(260, 352, 560, "Student Network (trainable)", CDARK)

arrow(input_b, teacher_outer, entryxy=("0", "0.3"))
arrow(input_b, student_outer, entryxy=("0", "0.3"))

gt_b = box(20, 630, 190, 90, "Ground-truth labels\n$y=\\{y_i\\}_{i=1}^N \\in \\{1,\\ldots,C\\}^N$",
           CGRAY, CGRAYBG)
upd_b = box(330, 660, 220, 60, "Update student parameters $\\theta_S$\n(teacher parameters fixed)",
            CGRAY, CGRAYBG)
arrow(student_outer, upd_b, dashed=True, color=CDARK, exitxy=("0.3", "1"), entryxy=("0.3", "0"))
arrow(gt_b, upd_b, dashed=True, color=CDARK)

# =====================================================================
# (B) Distillation Modules
# =====================================================================
DB_X = 900

# (i) KD Base
kd_ZT = box(DB_X+40, 60, 140, 50, "$Z_T$\n(teacher logits)", CBLUE, CBLUEBG)
kd_ZS = box(DB_X+40, 130, 140, 50, "$Z_S$\n(student logits)", CBLUE, CBLUEBG)
kd_temp = box(DB_X+230, 80, 220, 60, "Temperature $T$, Softmax", CGRAY, CGRAYBG)
kd_LKD = box(DB_X+500, 80, 160, 60, "$\\mathcal{L}_{KD}$\n(KL Divergence)", CBLUE, CBLUEBG)
arrow(kd_ZT, kd_temp); arrow(kd_ZS, kd_temp); arrow(kd_temp, kd_LKD)
kdbase_outer = outerbox(DB_X, 30, 700, 200, CBLUE)
title(DB_X, 4, 700, "(i) KD Base (logits-level)", CBLUE, size=13)

# (ii) Feature-level KD
fk_FT = box(DB_X+40, 290, 140, 50, "$F_T$\n(teacher features)", CGREEN, CGREENBG)
fk_FS = box(DB_X+40, 360, 140, 50, "$F_S$\n(student features)", CGREEN, CGREENBG)
fk_align = box(DB_X+230, 310, 165, 60, "Alignment in feature space $\\mathbb{R}^d$", CGRAY, CGRAYBG, font=10)
icon_dots_arrow(DB_X+398, 322, 48, 36)
fk_Lfeat = box(DB_X+500, 310, 160, 60, "$\\mathcal{L}_{feat}$\n(MSE)", CGREEN, CGREENBG)
arrow(fk_FT, fk_align); arrow(fk_FS, fk_align); arrow(fk_align, fk_Lfeat)
fk_outer = outerbox(DB_X, 260, 700, 200, CGREEN)
title(DB_X, 234, 700, "(ii) Feature-level KD", CGREEN, size=13)

# (iii) Classical Relational KD
cr_FT = box(DB_X+40, 520, 140, 50, "$F_T$\n(teacher features)", CORANGE, CORANGEBG)
cr_FS = box(DB_X+40, 590, 140, 50, "$F_S$\n(student features)", CORANGE, CORANGEBG)
cr_Rmat = box(DB_X+220, 545, 160, 70, "Relation matrix\n(classical)", CGRAY, CGRAYBG)
cr_RTC = box(DB_X+420, 510, 170, 50, "$R_T^{(C)} \\in \\mathbb{R}^{N\\times N}$", CORANGE, CORANGEBG)
cr_RSC = box(DB_X+420, 590, 170, 50, "$R_S^{(C)} \\in \\mathbb{R}^{N\\times N}$", CORANGE, CORANGEBG)
cr_Lrel = box(DB_X+630, 545, 160, 60, "$\\mathcal{L}_{rel}$\n(Frobenius Norm)", CORANGE, CORANGEBG)
arrow(cr_FT, cr_Rmat); arrow(cr_FS, cr_Rmat)
arrow(cr_Rmat, cr_RTC); arrow(cr_Rmat, cr_RSC)
arrow(cr_RTC, cr_Lrel); arrow(cr_RSC, cr_Lrel)
cr_outer = outerbox(DB_X, 490, 830, 200, CORANGE)
title(DB_X, 464, 830, "(iii) Classical Relational KD  (Euclidean / Cosine)", CORANGE, size=13)

# (iv) Quantum Relational Distillation
qd_FT = box(DB_X+40, 750, 140, 50, "$F_T$\n(teacher features)", CPURPLE, CPURPLEBG)
qd_FS = box(DB_X+40, 820, 140, 50, "$F_S$\n(student features)", CPURPLE, CPURPLEBG)
qd_projT = box(DB_X+210, 750, 150, 50, "Projection / Encoding $\\phi(\\cdot)$", CPURPLE, CPURPLEBG)
qd_projS = box(DB_X+210, 820, 150, 50, "Projection / Encoding $\\phi(\\cdot)$", CPURPLE, CPURPLEBG)
qd_pqc = box(DB_X+400, 760, 190, 100, "Quantum Mapping\n(PQC)", CGRAY, CGRAYBG, valign="top")
icon_circuit(DB_X+412, 810, 166, 42, nlines=3)
qd_RTQ = box(DB_X+630, 745, 190, 55, "Quantum relation matrix\n$R_T^{(Q)} \\in \\mathbb{R}^{N\\times N}$", CPURPLE, CPURPLEBG)
qd_RSQ = box(DB_X+630, 815, 190, 55, "Quantum relation matrix\n$R_S^{(Q)} \\in \\mathbb{R}^{N\\times N}$", CPURPLE, CPURPLEBG)
qd_LQRD = box(DB_X+860, 780, 160, 60, "$\\mathcal{L}_{QRD}$\n(Frobenius Norm)", CPURPLE, CPURPLEBG)
arrow(qd_FT, qd_projT); arrow(qd_FS, qd_projS)
arrow(qd_projT, qd_pqc); arrow(qd_projS, qd_pqc)
arrow(qd_pqc, qd_RTQ); arrow(qd_pqc, qd_RSQ)
arrow(qd_RTQ, qd_LQRD); arrow(qd_RSQ, qd_LQRD)

# V5-only subbox
v5_in = box(DB_X+40, 940, 130, 60, "Inputs:\n$Z_T, Z_S$", CPURPLE, CPURPLEBG, dashed=True)
v5_ui = box(DB_X+195, 940, 150, 60, "Uncertainty $u_i$\n(teacher entropy)", CPURPLE, CPURPLEBG)
v5_di = box(DB_X+370, 940, 170, 60, "Disagreement $d_i$\n(Jensen--Shannon divergence)", CPURPLE, CPURPLEBG)
v5_si = box(DB_X+565, 940, 190, 60, "Score $s_i = w_e u_i + w_d d_i$\n$w_e = w_d = 0{,}5$", CPURPLE, CPURPLEBG)
v5_topk = box(DB_X+780, 940, 170, 60, "Top-$K$ selection $S$\n(informative samples)", CPURPLE, CPURPLEBG)
# Ghi ro ngay trong o cuoi chuoi V5 rang S quyet dinh mau nao duoc dua vao
# buoc Projection/Encoding cho CA HAI nhanh teacher/student (dung Thuat
# toan 1, buoc 7) -- KHONG dung mui ten dai xuyen khung QRD (de vo khi
# dinh tuyen orthogonal qua khoang cach lon, da thay o ban truoc).
v5_comp = box(DB_X+975, 940, 170, 60,
    "Compute QRD on selected\nsamples $S$ -- feeds $F_T[S], F_S[S]$\ninto Projection/Encoding above",
    CPURPLE, CPURPLEBG, font=9)
arrow(v5_in, v5_ui); arrow(v5_ui, v5_di); arrow(v5_di, v5_si)
arrow(v5_si, v5_topk); arrow(v5_topk, v5_comp)
v5_outer = outerbox(DB_X+20, 910, 1150, 130, CPURPLE, dashed=True)
title(DB_X+20, 884, 1150, "Variant V5 only (informative sample selection)", CPURPLE, size=12)

qrd_outer = outerbox(DB_X, 720, 1200, 350, CPURPLE)
title(DB_X, 694, 1200, "(iv) Quantum Relational Distillation (QRD)", CPURPLE, size=13)

dmod_outer = outerbox(DB_X-40, 0, 1280, 1100, CGRAY)
title(DB_X-40, -30, 1280, "Distillation Modules (training-time only)", CDARK, size=16)

# =====================================================================
# (C) 5 hop loss thanh phan + Total Training Objective + 2 legend
# =====================================================================
LY = 1150
LCE = box(20, LY, 190, 60, "$\\mathcal{L}_{CE}$ (Cross-Entropy)\nInput: $Z_S, y$", CGRAY, CGRAYBG)
LKD2 = box(230, LY, 170, 60, "$\\mathcal{L}_{KD}$\n(from KD Base)", CBLUE, CBLUEBG)
Lfeat2 = box(420, LY, 180, 60, "$\\mathcal{L}_{feat}$\n(from Feature KD)\n(optional)", CGREEN, CGREENBG)
Lrel2 = box(620, LY, 180, 60, "$\\mathcal{L}_{rel}$\n(from Relational KD)\n(optional)", CORANGE, CORANGEBG)
LQRD2 = box(820, LY, 190, 60, "$\\mathcal{L}_{QRD}$\n(from QRD variants)\n(optional)", CPURPLE, CPURPLEBG)

total_b = box(20, LY+100, 990, 90,
    "Total Training Objective (configured by experiment)\n"
    "$\\mathcal{L}_{total}=\\alpha\\mathcal{L}_{CE}+(1-\\alpha)\\mathcal{L}_{KD}"
    "+\\gamma_f\\mathcal{L}_{feat}+\\gamma_r\\mathcal{L}_{rel}+\\beta\\mathcal{L}_{QRD}$\n"
    "(Set $\\gamma_f$, $\\gamma_r$, or $\\beta$ = 0 when the corresponding component is not used)",
    CGRAY, CGRAYBG, font=11, bold=False)
for src in (LCE, LKD2, Lfeat2, Lrel2, LQRD2):
    arrow(src, total_b)

arrow(total_b, upd_b, dashed=True, color=CDARK,
      exitxy=("0", "0.5"), entryxy=("0", "0.7"))
arrow(total_b, upd_b, dashed=True, color=CDARK, label="Backpropagation",
      exitxy=("0.05", "1"), entryxy=("0.05", "0.9"))

# Legend 1: Ablation settings -- moi o to theo dung mau co che tuong ung,
# giu nhat quan 1 truc mau duy nhat xuyen suot ca hinh.
abl_items = [
    ("KDBase", "$\\mathcal{L}_{extra}=0$", CGRAY, CGRAYBG),
    ("FeatureKD", "$\\mathcal{L}_{extra}=\\mathcal{L}_{feat}$", CGREEN, CGREENBG),
    ("RelationalKD", "$\\mathcal{L}_{extra}=\\mathcal{L}_{rel}$", CORANGE, CORANGEBG),
    ("QRD (V1--V4)", "$\\mathcal{L}_{extra}=\\mathcal{L}_{QRD}$\n($\\mathcal{I}$: relation on fixed $q$ samples)", CPURPLE, CPURPLEBG),
    ("QRD (V5 Guided)", "$\\mathcal{L}_{extra}=\\mathcal{L}_{QRD}$\n($\\mathcal{I}$: relation on teacher-selected $S$)", CPURPLE, CPURPLEBG),
]
LEGY = LY+230
x = 40
abl_ids = []
for name, sub, c, cbg in abl_items:
    w = 190
    bid = box(x, LEGY+30, w, 80, f"{name}\n{sub}", c, cbg, font=10)
    abl_ids.append(bid); x += w + 15
outerbox(20, LEGY, 990, 130, CGRAY, dashed=True)
title(20, LEGY-26, 990, "Ablation settings (loss-level)", CDARK, size=13)

var_items = [
    ("V1 Dense", "(deterministic dimensionality reduction)"),
    ("V2 Dense", "(learned projection)"),
    ("V3 Anchor", "(anchor-based sparse relation)"),
    ("V4 Anchor+kNN", "(anchor + kNN hybrid relation)"),
    ("V5 Guided", "(teacher-guided informative relation)"),
]
x = 1060
for name, sub in var_items:
    w = 190
    # Ca 5 bien the deu thuoc co che QRD (tim) -- day la legend rieng
    # cho Hinh 2, chi khac nhau ve cach chon quan he, khong phai 1 truc
    # mau moi.
    box(x, LEGY+30, w, 80, f"{name}\n{sub}", CPURPLE, CPURPLEBG, font=10)
    x += w + 15
outerbox(1040, LEGY, 990, 130, CGRAY, dashed=True)
title(1040, LEGY-26, 990, "QRD relation construction variants (see Fig. 2)", CDARK, size=13)

# =====================================================================
# (D) Training Procedure + Deployment
# =====================================================================
DX = 2350
s1 = box(DX+30, 40, 420, 45, "1. Forward pass through teacher and student", CGRAY, CGRAYBG)
s2 = box(DX+30, 100, 420, 45, "2. Compute the losses activated by the selected variant", CGRAY, CGRAYBG)
s3 = box(DX+30, 160, 420, 45, "3. Form the total training objective", CGRAY, CGRAYBG)
s4 = box(DX+30, 220, 420, 45, "4. Backpropagate and update the student only", CGRAY, CGRAYBG)
arrow(s1, s2); arrow(s2, s3); arrow(s3, s4)
# Rieng ghi chu ve QRD duoc giu mau tim vi no noi truc tiep ve co che QRD;
# khung ngoai + tieu de Training Procedure la trung tinh (khong phai 1 co che).
qnote = box(DX+30, 280, 420, 45, "Quantum module (QRD) is used only during training.",
            CPURPLE, CPURPLEBG, italic=True)
outerbox(DX, 10, 480, 340, CGRAY)
title(DX, -18, 480, "Training Procedure", CDARK, size=15)

d1 = box(DX+30, 420, 300, 55, "EEG--MI input (single trial or stream)", CGRAY, CGRAYBG, font=10)
icon_wave(DX+345, 435, 90, 26)
d2 = box(DX+30, 490, 300, 45, "Trained Student (used alone)", CGRAY, CGRAYBG, font=10)
icon_stack(DX+345, 495, 65, 35)
d3 = box(DX+30, 550, 300, 45, "Predicted class (Softmax output)", CGRAY, CGRAYBG, font=10)
icon_bars(DX+345, 555, 65, 32)
arrow(d1, d2); arrow(d2, d3)
outerbox(DX, 390, 480, 230, CGRAY)
title(DX, 362, 480, "Deployment (Inference)", CDARK, size=15)

# =====================================================================
# math="1" -> file tu bat san "Mathematical Typesetting" (MathJax) khi mo
# trong draw.io, khong can nguoi dung bat tay qua menu Extras.
xml = f"""<mxfile host="app.diagrams.net">
  <diagram name="Hinh1_Khung" id="fig1">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1"
        connect="1" arrows="1" fold="1" page="1" pageScale="1"
        pageWidth="3960" pageHeight="1600" math="1" shadow="0">
      <root>
        <mxCell id="0"/>
        <mxCell id="1" parent="0"/>
        {"".join(cells)}
      </root>
    </mxGraphModel>
  </diagram>
</mxfile>
"""
print(xml)
