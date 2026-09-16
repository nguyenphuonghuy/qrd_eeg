#!/usr/bin/env python3
"""
Sinh file .drawio (mxGraph XML) cho Hinh 2 (5 bien the xay dung ma tran
quan he QRD). Ket hop 2 dieu da chot:
  (a) cau truc "hai truc khao sat giao nhau" (V1 vs V2; V2->V3->V4->V5)
      da noi ro trong Muc 3.4 body.tex -- anh AI ban dau KHONG the hien.
  (b) so do cham-noi toi gian, NHAT QUAN 1 kieu bo tri 5 diem ngu giac
      cho ca 5 o (small-multiples) -- chi khac o CANH nao duoc ve, dung
      chinh xac theo dinh nghia tap chi so I_Vk trong body.tex (khong
      phai suy dien):
        V1/V2: day du (moi cap deu noi) -- I_V1 = I_V2 = {(i,j)|1<=i,j<=q}
        V3   : CHI 2 diem neo noi voi nhau, 3 diem con lai KHONG noi gi
               (mau ngoai A khong dong gop vao L_QRD) -- I_V3={(a,a')|a,a' in A}
        V4   : nhu V3 + cac canh kNN cuc bo ket noi diem thuong voi
               lang gieng gan nhat -- I_V4 = I_V3 hop {(i,j)|j in N_k(i)}
        V5   : CHI 3 diem duoc chon (S) noi day du voi nhau, 2 diem con
               lai khong noi gi -- I_V5={(i,j)|i,j in S}

Chay: python3 gen_fig2_drawio.py > fig2_khung.drawio
"""
import re
import math

CBLUE = "#1565C0"; CBLUEBG = "#E3F2FD"
CGREEN = "#2E7D32"; CGREENBG = "#E8F5E9"
CRED = "#B71C1C"; CREDBG = "#FFEBEE"
CORANGE = "#E65100"
CGRAY = "#616161"; CGRAYBG = "#F5F5F5"
CDARK = "#424242"

_id = [0]
def nid():
    _id[0] += 1
    return f"h{_id[0]}"

cells = []

def mathify(s):
    return re.sub(r"\$([^$]+)\$", r"\\(\1\\)", s)

def esc(s):
    s = mathify(s)
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    return s.replace("\n", "&#10;")

def box(x, y, w, h, label, stroke, fill, font=10, align="left", valign="top", bold=False):
    i = nid()
    style = (f"rounded=1;arcSize=8;whiteSpace=wrap;html=1;"
             f"strokeColor={stroke};fillColor={fill};fontSize={font};"
             f"align={align};verticalAlign={valign};spacing=6;")
    if bold: style += "fontStyle=1;"
    cells.append(
        f'<mxCell id="{i}" value="{esc(label)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')
    return i

def outerbox(x, y, w, h, stroke):
    i = nid()
    style = f"rounded=1;arcSize=8;whiteSpace=wrap;html=1;strokeColor={stroke};fillColor=none;"
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')
    return i

def small_text(x, y, w, h, text, size, color, bold=True, align="center"):
    i = nid()
    style = (f"text;html=1;align={align};verticalAlign=middle;fontSize={size};"
             f"fontColor={color};")
    if bold: style += "fontStyle=1;"
    cells.append(
        f'<mxCell id="{i}" value="{esc(text)}" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" as="geometry"/></mxCell>')
    return i

def dot(cx, cy, r, stroke, fill):
    i = nid()
    style = f"ellipse;whiteSpace=wrap;html=1;strokeColor={stroke};fillColor={fill};"
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" vertex="1" parent="1">'
        f'<mxGeometry x="{cx-r:.1f}" y="{cy-r:.1f}" width="{2*r:.1f}" height="{2*r:.1f}" as="geometry"/></mxCell>')
    return i

def line(p1, p2, stroke, w=1.2):
    i = nid()
    style = f"edgeStyle=none;html=1;strokeColor={stroke};strokeWidth={w};endArrow=none;startArrow=none;"
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" edge="1" parent="1">'
        f'<mxGeometry relative="1" as="geometry">'
        f'<mxPoint x="{p1[0]:.1f}" y="{p1[1]:.1f}" as="sourcePoint"/>'
        f'<mxPoint x="{p2[0]:.1f}" y="{p2[1]:.1f}" as="targetPoint"/>'
        f'</mxGeometry></mxCell>')
    return i

def bracket(x1, x2, y, label, color, tick_down):
    style = f"edgeStyle=none;html=1;strokeColor={color};strokeWidth=1.6;endArrow=none;startArrow=none;"
    i = nid()
    cells.append(
        f'<mxCell id="{i}" value="" style="{style}" edge="1" parent="1">'
        f'<mxGeometry relative="1" as="geometry">'
        f'<mxPoint x="{x1:.1f}" y="{y:.1f}" as="sourcePoint"/>'
        f'<mxPoint x="{x2:.1f}" y="{y:.1f}" as="targetPoint"/>'
        f'</mxGeometry></mxCell>')
    tlen = 10 if tick_down else -10
    for tx in (x1, x2):
        j = nid()
        cells.append(
            f'<mxCell id="{j}" value="" style="{style}" edge="1" parent="1">'
            f'<mxGeometry relative="1" as="geometry">'
            f'<mxPoint x="{tx:.1f}" y="{y:.1f}" as="sourcePoint"/>'
            f'<mxPoint x="{tx:.1f}" y="{y+tlen:.1f}" as="targetPoint"/>'
            f'</mxGeometry></mxCell>')
    ly = y - 24 if tick_down else y + 6
    small_text(x1, ly, x2 - x1, 20, label, size=11, color=color, bold=False)

# =====================================================================
# So do 5 diem ngu giac -- CUNG MOT bo tri cho ca 5 o (small multiples),
# chi khac canh nao duoc ve. Toa do la CUC BO (goc 0,0 = tam vung ve),
# duoc dich sang tung o bang offset (ox,oy).
# =====================================================================
DIAG_W, DIAG_H = 150, 96
_cx, _cy, _r = DIAG_W/2, DIAG_H/2 + 4, 34
PENT = []
for k in range(5):
    ang = math.radians(90 - k*72)
    PENT.append((_cx + _r*math.cos(ang), _cy - _r*math.sin(ang)))

def pent_pts(ox, oy):
    return [(ox+px, oy+py) for px, py in PENT]

BLUE_FILL, GREEN_FILL, RED_FILL, GRAY_FILL = "#90CAF9", "#A5D6A7", "#EF9A9A", "#E0E0E0"

def draw_v1v2(ox, oy):
    pts = pent_pts(ox, oy)
    for i in range(5):
        for j in range(i+1, 5):
            line(pts[i], pts[j], CBLUE, w=0.7)
    for p in pts:
        dot(p[0], p[1], 7, CBLUE, BLUE_FILL)

def draw_v3(ox, oy):
    pts = pent_pts(ox, oy)
    anchors = [0, 2]  # 2 trong 5 diem la neo
    line(pts[anchors[0]], pts[anchors[1]], CGREEN, w=1.4)
    for k, p in enumerate(pts):
        if k in anchors:
            dot(p[0], p[1], 7, CGREEN, GREEN_FILL)
        else:
            dot(p[0], p[1], 6, "#9E9E9E", GRAY_FILL)

def draw_v4(ox, oy):
    pts = pent_pts(ox, oy)
    anchors = [0, 2]
    line(pts[anchors[0]], pts[anchors[1]], CGREEN, w=1.4)
    # canh kNN cuc bo: moi diem thuong noi voi lang gieng gan nhat (canh ngu giac ke)
    others = [1, 3, 4]
    knn_edges = [(1, 0), (3, 4), (4, 3)]  # (i, nearest neighbor index) -- ve 1 lan/cap
    drawn = set()
    for a, b in [(1, 0), (3, 4)]:
        key = tuple(sorted((a, b)))
        if key not in drawn:
            line(pts[a], pts[b], CORANGE, w=1.0)
            drawn.add(key)
    for k, p in enumerate(pts):
        if k in anchors:
            dot(p[0], p[1], 7, CGREEN, GREEN_FILL)
        else:
            dot(p[0], p[1], 6, CBLUE, BLUE_FILL)

def draw_v5(ox, oy):
    pts = pent_pts(ox, oy)
    sel = [0, 1, 3]  # 3 trong 5 diem duoc chon (S)
    for i in range(len(sel)):
        for j in range(i+1, len(sel)):
            line(pts[sel[i]], pts[sel[j]], CRED, w=1.4)
    for k, p in enumerate(pts):
        if k in sel:
            dot(p[0], p[1], 7, CRED, RED_FILL)
        else:
            dot(p[0], p[1], 6, "#9E9E9E", GRAY_FILL)

DRAW_FN = [draw_v1v2, draw_v1v2, draw_v3, draw_v4, draw_v5]

# =====================================================================
# 5 o bien the: khung ngoai + tieu de + so do cham-noi + van ban
# =====================================================================
COLW, GAP = 380, 25
def colx(k): return k * (COLW + GAP)

FAMILY = {0: (CBLUE, CBLUEBG), 1: (CBLUE, CBLUEBG),
          2: (CGREEN, CGREENBG), 3: (CGREEN, CGREENBG),
          4: (CRED, CREDBG)}

VARIANTS = [
    ("V1 Dense (deterministic)",
     "Dense relations, deterministic dimensionality reduction.",
     "$\\mathcal{I}_{V1}=\\{(i,j)\\mid 1\\le i,j\\le q\\}$",
     "$W_T$: not used   $W_S$: not used   $\\theta$: trainable",
     "Additional parameters: 24"),
    ("V2 Dense (learned projection)",
     "Dense relations, learned linear projection.",
     "$\\mathcal{I}_{V2}=\\mathcal{I}_{V1}$",
     "$W_T$: fixed   $W_S$: trainable   $\\theta$: trainable",
     "Additional parameters: 604"),
    ("V3 Anchor",
     "Sparse relations: computed only among anchor samples; other samples do not contribute.",
     "$\\mathcal{I}_{V3}=\\{(a,a')\\mid a,a'\\in\\mathcal{A}\\}$, $|\\mathcal{A}|=8$",
     "$W_T$: fixed   $W_S$: trainable   $\\theta$: trainable",
     "Additional parameters: 604"),
    ("V4 Anchor + kNN",
     "Adds local kNN relations for every sample, alongside anchor-to-anchor relations.",
     "$\\mathcal{I}_{V4}=\\mathcal{I}_{V3}\\cup\\{(i,j)\\mid j\\in\\mathcal{N}_k(i)\\}$, $k=4$",
     "$W_T$: fixed   $W_S$: trainable   $\\theta$: trainable",
     "Additional parameters: 604"),
    ("V5 Guided",
     "Dense relations, but restricted to the subset of samples selected by the teacher.",
     "$\\mathcal{I}_{V5}=\\{(i,j)\\mid i,j\\in\\mathcal{S}\\}$, top-$q$ by teacher score",
     "$W_T$: fixed   $W_S$: trainable   $\\theta$: trainable",
     "Additional parameters: 604"),
]

ROW_Y = 100
TITLE_H = 24
DIAG_Y = ROW_Y + TITLE_H + 6
TEXT_Y = DIAG_Y + DIAG_H + 10
TEXT_H = 150
ROW_H = (TEXT_Y + TEXT_H) - ROW_Y

for k, (name, desc, iset, status, nparam) in enumerate(VARIANTS):
    x0 = colx(k)
    stroke, fill = FAMILY[k]
    outerbox(x0, ROW_Y, COLW, ROW_H, stroke)
    small_text(x0, ROW_Y + 4, COLW, TITLE_H, name, size=12, color=stroke, bold=True)
    DRAW_FN[k](x0 + (COLW - DIAG_W) / 2, DIAG_Y)
    body_txt = f"{desc}\n\n{iset}\n\n{status}\n\n{nparam}"
    box(x0 + 14, TEXT_Y, COLW - 28, TEXT_H, body_txt, stroke, fill, font=9)

TOTAL_W = colx(4) + COLW  # = 2000

bracket(colx(0), colx(1) + COLW, ROW_Y - 30,
        "Axis 1: adaptivity of the dimensionality reduction (V1 vs. V2)",
        CBLUE, tick_down=True)
bracket(colx(1), colx(4) + COLW, ROW_Y + ROW_H + 18,
        "Axis 2: relation density and selection strategy, from no intervention to content-based sample selection (V2 → V3 → V4 → V5)",
        CGREEN, tick_down=False)

# =====================================================================
# Chu giai mau cham (thay legend icon rườm rà bang 1 dong text ngan)
# =====================================================================
LEGY = ROW_Y + ROW_H + 65
leg_items = [("Regular sample", BLUE_FILL, CBLUE), ("Anchor sample", GREEN_FILL, CGREEN),
             ("kNN neighbor", "#FFFFFF", CORANGE), ("Teacher-selected sample", RED_FILL, CRED),
             ("Not used in $\\mathcal{L}_{QRD}$", GRAY_FILL, "#9E9E9E")]
lx = 20
for name, fill, stroke in leg_items:
    dot(lx, LEGY + 8, 6, stroke, fill)
    small_text(lx + 14, LEGY, 300, 16, name, size=9, color=CDARK, bold=False, align="left")
    lx += 380

# =====================================================================
# 2 o cong thuc dung chung
# =====================================================================
SHY = LEGY + 40
note = box(0, SHY, TOTAL_W, 40,
    "All five variants share the same loss function $\\mathcal{L}_{QRD}$ and hyperparameters, "
    "differing only in the relation index set $\\mathcal{I}$ (given in each box above).",
    CGRAY, "#FAFAFA", font=10, align="center", valign="middle")

kernel_b = box(0, SHY+55, 975, 150,
    "Quantum kernel (shared by all variants)\n\n"
    "$K(a_i,a_j) = |\\langle \\psi(x_i) | \\psi(x_j)\\rangle|^2 \\in [0,1]$\n\n"
    "(quantum feature encoding, followed by a parameterized quantum circuit -- PQC)",
    CGRAY, CGRAYBG, font=10)

loss_b = box(1005, SHY+55, 995, 150,
    "Quantum relational loss (shared by all variants)\n\n"
    "$\\mathcal{L}_{QRD} = \\dfrac{1}{|\\mathcal{I}|}\\displaystyle\\sum_{(i,j)\\in\\mathcal{I}} "
    "\\left(R_T^{(Q)}(i,j) - R_S^{(Q)}(i,j)\\right)^2$\n\n"
    "where $\\mathcal{I}$ is the relation index set defined individually by each variant above.",
    CGRAY, CGRAYBG, font=10)

# =====================================================================
xml = f"""<mxfile host="app.diagrams.net">
  <diagram name="Hinh2_BienThe" id="fig2">
    <mxGraphModel dx="1400" dy="900" grid="1" gridSize="10" guides="1" tooltips="1"
        connect="1" arrows="1" fold="1" page="1" pageScale="1"
        pageWidth="2100" pageHeight="1050" math="1" shadow="0">
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
