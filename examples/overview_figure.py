"""A Nature/Science-style overview figure, rendered entirely in matplotlib.

This is the kind of figure that opens a paper and summarises the whole study:
a cohort banner, a stacked single-cell atlas, an xQTL mapping chain, a gene
regulatory network and a model schematic -- normally drawn in BioRender or
Illustrator, here produced as code so it is reproducible and diffable.

The content is synthetic. Replace the placeholder numbers and distributions
with your own and the layout carries over unchanged.

Run:  python examples/overview_figure.py
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (Rectangle, Ellipse, Circle, Polygon,
                                PathPatch, FancyBboxPatch)
from matplotlib.path import Path
from matplotlib.transforms import Affine2D
import matplotlib.colors as mcolors

from sciglyph import set_canvas, report, RC
from sciglyph.bio import (person, dna, cell, lipid, metabolite, umap_layer,
                          seq_logo, rbox, arr)

plt.rcParams.update(RC)

INK, GRAY = "#1a1a1a", "#8a8a8a"
GREEN_BG, BLUE_BG = "#e8f4e2", "#e6f0f8"
CIMA_COLS = ["#e94f37", "#f6a01a", "#3aa76d", "#2f7fc1"]


def title(ax, x, y, s, fs=8.5):
    ax.text(x, y, s, fontsize=fs, weight="bold", ha="center", color=INK, zorder=20)

# ---------------- canvas: a three-row grid ----------------
fig = plt.figure(figsize=(7.2, 8.2), dpi=400)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
set_canvas(fig)


# ---- cohort banner ----
rbox(ax, .02, .800, .70, .185, GREEN_BG)
rbox(ax, .735, .800, .245, .185, BLUE_BG)

ax.text(.035, .958, "428 Chinese Natural Cohort", fontsize=8, weight="bold", color=INK, zorder=20)
cmap_age = mcolors.LinearSegmentedColormap.from_list("age", ["#f6b8a0", "#c0392b"])
gap = .0235
for i, a in enumerate(np.linspace(0, 1, 9)):
    person(ax, .048+i*gap, .900, s=.058, fc=cmap_age(a), z=4)
ax.annotate("", xy=(.245, .845), xytext=(.038, .845),
            arrowprops=dict(arrowstyle="-|>", color=INK, lw=.9), zorder=20)
ax.text(.034, .824, "20", fontsize=6.5, color=INK, zorder=20)
ax.text(.232, .824, "77", fontsize=6.5, color=INK, zorder=20)
ax.text(.135, .824, "Age", fontsize=6.5, style="italic", color=INK, ha="center", zorder=20)

# omics icons, each paired with its label
dna(ax, .300, .938, w=.026, h=.050, n=2.3, lw=1.2)
ax.text(.325, .952, "scRNA-seq", fontsize=7.2, weight="bold", color=INK, zorder=20)
ax.text(.325, .933, "(6,484,974 cells)", fontsize=5.9, color="#555", zorder=20)

for i, (dx, dy, sd) in enumerate([(0, 0, 1), (.019, -.004, 2), (.009, -.014, 3)]):
    cell(ax, .490+dx, .944+dy, r=.0105, seed=sd, z=4)
ax.text(.530, .952, "scATAC-seq", fontsize=7.2, weight="bold", color=INK, zorder=20)
ax.text(.530, .933, "(3,762,242 cells)", fontsize=5.9, color="#555", zorder=20)

metabolite(ax, .300, .878, s=.048)
ax.text(.322, .884, "Metabolomics", fontsize=7.2, weight="bold", color=INK, zorder=20)
ax.text(.322, .866, "(321 species)", fontsize=5.9, color="#555", zorder=20)

lipid(ax, .462, .878, s=.050)
ax.text(.487, .884, "Lipidomics", fontsize=7.2, weight="bold", color=INK, zorder=20)
ax.text(.487, .866, "(1228 species)", fontsize=5.9, color="#555", zorder=20)

dna(ax, .625, .876, w=.020, h=.038, n=1.9, lw=1.0, cols=("#8e44ad", "#16a085"))
ax.text(.648, .872, "WGS", fontsize=7.2, weight="bold", color=INK, zorder=20)

for i, ch in enumerate("CIMA"):
    ax.text(.790+i*.037, .932, ch, fontsize=18, weight="bold", color=CIMA_COLS[i],
            ha="center", zorder=20)
ax.text(.857, .906, "Chinese Immune Multi-Omics Atlas", fontsize=5.4, ha="center",
        color="#333", zorder=20)
ax.text(.857, .884, "Natural Cohort", fontsize=6.4, ha="center", style="italic",
        color="#3aa76d", weight="bold", zorder=20)
arr(ax, (.36, .797), (.36, .770), c=INK, lw=1.1, ms=9)

# ---- row 1 left: single-cell atlas ----
title(ax, .245, .752, "Circulating Immune Cell Atlas")
cmaps = ["Reds", "Purples", "Blues", "Greens", "Oranges", "YlGnBu", "PuRd"]
labs = ["scRNA", "Integration", "scATAC", "ILC", "B", "Myeloid & HSPC", "CD8 & Other T"]
for i in range(7):
    umap_layer(ax, .050+i*.0425, .565, .100, .150, seed=10+i, cmap=cmaps[i], z=3+i)
    ax.text(.056+i*.0425, .722+(i % 2)*.013, labs[i], fontsize=4.4, color="#444", zorder=15)
rbox(ax, .075, .524, .100, .024, "#d9efd4", r=.006, z=4)
ax.text(.125, .532, "73 Cell Types", fontsize=6.0, weight="bold", ha="center", zorder=20)
rbox(ax, .205, .524, .132, .024, "#d9efd4", r=.006, z=4)
ax.text(.271, .532, "10,247,216 Cells", fontsize=6.0, weight="bold", ha="center", zorder=20)

# ---- row 1 right: xQTL mapping ----
title(ax, .750, .752, "xQTL mapping")
title(ax, .750, .733, "and GWAS-QTL integration")
dna(ax, .565, .612, w=.030, h=.065, n=2.1, lw=1.2)
ax.add_patch(Ellipse((.565, .618), .019, .032, fc="none", ec="#e94f37", lw=1.0, zorder=8))
ax.text(.565, .563, "Variant", fontsize=6.2, ha="center", color=INK, zorder=20)
for i in range(4):
    ax.add_patch(Ellipse((.652+i*.020, .626), .018, .012, fc="#f3b6c6", ec="#d9829b",
                         lw=.6, zorder=4, angle=-12))
ax.plot([.593, .733], [.626, .626], color="#d9829b", lw=.7, zorder=3)
ax.text(.638, .598, "52,361 caPeaks", fontsize=6.2, ha="center", color=INK, zorder=20)
for i, sd in enumerate([21, 22, 23]): cell(ax, .800+i*.025, .650, r=.0095, seed=sd, z=5)
ax.text(.825, .718, "Cell Types", fontsize=6.2, ha="center", color=INK, zorder=20)
ax.add_patch(Rectangle((.888, .618), .072, .015, fc="#f4f4f4", ec="#999", lw=.5, zorder=4))
for i in range(6):
    ax.add_patch(Rectangle((.893+i*.0105, .620), .0065, .011,
                           fc="#e94f37" if i % 2 else "#2f7fc1", ec="none", zorder=5))
ax.text(.924, .598, "9600 eGenes", fontsize=6.2, ha="center", color=INK, zorder=20)
arr(ax, (.585, .644), (.642, .652), c="#c0392b", lw=1.0, rad=-.25)
arr(ax, (.743, .642), (.790, .652), c="#2f7fc1", lw=1.0, rad=.2)
arr(ax, (.862, .644), (.888, .634), c="#c0392b", lw=1.0, rad=-.2)
for xx in (.610, .650): ax.plot(xx, .664, marker="*", ms=6, color="#f39c12", zorder=9)

# ---- row 2 right: mechanistic chain ----
ax.text(.572, .458, "rs34415530", fontsize=6.0, color="#c0392b", weight="bold", zorder=20)
ax.text(.590, .437, "C>T", fontsize=5.8, color="#c0392b", zorder=20)
cell(ax, .700, .450, r=.020, fc="#dbeaf7", ec="#2f7fc1", seed=31, z=5)
ax.text(.700, .478, "IKZF4", fontsize=5.6, ha="center", color="#2f7fc1", weight="bold", zorder=20)
ax.text(.700, .413, "CD4 Treg\n-FOXP3", fontsize=5.2, ha="center", va="top",
        color="#3aa76d", zorder=20)
cell(ax, .820, .450, r=.021, fc="#e6dcf2", ec="#8e44ad", seed=32, z=5)
ax.text(.820, .420, "DC", fontsize=5.8, ha="center", color=INK, zorder=20)
ax.text(.935, .446, "Asthma", fontsize=6.2, ha="center", color="#c0392b", weight="bold", zorder=20)
arr(ax, (.636, .452), (.674, .452), c="#c0392b", lw=.9)
arr(ax, (.724, .456), (.795, .456), c=INK, lw=.9, style="|-|", ms=3)
arr(ax, (.844, .454), (.906, .450), c="#c0392b", lw=.9, rad=.15)
arr(ax, (.628, .424), (.900, .428), c="#3aa76d", lw=.9, rad=-.10)
ax.text(.612, .402, "SMR", fontsize=5.4, color="#3aa76d", zorder=20)
arr(ax, (.628, .386), (.925, .388), c="#c0392b", lw=.9, rad=-.08)
ax.text(.760, .366, "GWAS", fontsize=5.4, color="#c0392b", zorder=20)

# ---- panel separators ----
ax.plot([.02, .50], [.470, .470], color="#ccc", lw=.7, ls=(0, (4, 3)))
ax.plot([.50, .50], [.470, .015], color="#ccc", lw=.7, ls=(0, (4, 3)))
ax.plot([.50, .50], [.800, .262], color="#ccc", lw=.7, ls=(0, (4, 3)))
ax.plot([.02, .98], [.250, .250], color="#ccc", lw=.7, ls=(0, (4, 3)))

# ---- row 2 left: multi-omics variation ----
title(ax, .245, .448, "Multi-Omics Variations within Population", fs=8.0)
rng = np.random.default_rng(7)
for i, c in enumerate(["#8e6cb0", "#5b8dd6", "#e08a4a", "#7fbf7f"]):
    tr = (Affine2D().skew(0, np.arctan(.42)).scale(.115, .040)
          .translate(.052, .300+i*.022) + ax.transData)
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=c, lw=.9, alpha=.8,
                           transform=tr, zorder=3+i))
    ax.scatter(rng.uniform(.08, .92, 40), rng.uniform(.1, .9, 40), s=1.3, c=c,
               alpha=.8, linewidths=0, transform=tr, zorder=4+i)
ax.text(.043, .318, "Omics", fontsize=5.8, rotation=90, color=INK, va="bottom", zorder=20)
ax.text(.088, .282, "PC2", fontsize=5.6, color="#555", zorder=20)
ax.text(.152, .282, "PC1", fontsize=5.6, color="#555", zorder=20)
grad = np.linspace(0, 1, 120).reshape(1, -1)
ax.imshow(grad, cmap="RdYlBu_r", aspect="auto", extent=[.250, .395, .400, .414], zorder=4)
ax.text(.3225, .420, "Age", fontsize=6.0, ha="center", color=INK, zorder=20)
hm = np.sort(rng.normal(0, 1, (9, 26)), axis=1)*np.where(np.arange(9)[:, None] < 5, 1, -1)
ax.imshow(hm, cmap="RdYlBu_r", aspect="auto", extent=[.250, .395, .306, .394], zorder=4)
ax.text(.243, .350, "Features", fontsize=6.0, rotation=90, ha="center", va="center",
        color=INK, zorder=20)
ax.text(.3225, .288, "Expression", fontsize=6.0, ha="center", color=INK, zorder=20)
for i, ww in enumerate([.048, .035, .024, .015, -.028, -.020, -.012, -.007]):
    ax.add_patch(Rectangle((.408, .388-i*.0092), abs(ww), .0070,
                           fc="#c0392b" if ww > 0 else "#2f7fc1", ec="none", zorder=5))
ax.text(.440, .404, "Factor Weights", fontsize=6.0, ha="center", color=INK, zorder=20)

# ---- row 3 left: gene regulatory network ----
title(ax, .245, .228, "Gene Regulatory Networks")
ax.add_patch(Circle((.070, .130), .019, fc="#5dade2", ec="#2f7fc1", lw=.8, zorder=5))
ax.text(.070, .130, "Cell\nType", fontsize=4.4, ha="center", va="center", zorder=6)
tf_cols = ["#9b59b6", "#f1c40f", "#e8a0b8", "#e67e22", "#27ae60"]
tfy = [.190, .166, .142, .118, .086]
for i, (c, yy) in enumerate(zip(tf_cols, tfy)):
    tr = Affine2D().scale(.018, .014).translate(.160, yy)
    ax.add_patch(PathPatch(Path.unit_regular_polygon(6).transformed(tr), fc=c,
                           ec="white", lw=.7, zorder=5))
    ax.text(.160, yy, f"TF-{i+1}", fontsize=4.2, ha="center", va="center",
            color="white", weight="bold", zorder=6)
    ax.plot([.088, .143], [.130, yy], color="#c0392b", lw=.6, ls=(0, (2, 1.6)), zorder=3)
    for j in range(2):
        py = yy + (j-.5)*.013
        ax.add_patch(Rectangle((.232, py-.004), .0075, .0075, fc="#2f7fc1",
                               ec="none", zorder=5, angle=45))
        ax.plot([.178, .232], [yy, py], color=c, lw=.6, zorder=3)
        ax.add_patch(Circle((.300, py), .0052, fc="#e74c3c", ec="none", zorder=5))
        ax.plot([.240, .295], [py, py], color=c, lw=.6, zorder=3)
rbox(ax, .340, .160, .150, .026, "#dbeaf7", r=.006, z=4)
ax.text(.415, .173, "Immune Cell Type-\nSpecific GRN", fontsize=5.4, ha="center",
        va="center", zorder=20)
rbox(ax, .340, .112, .150, .020, "#fadbd8", r=.006, z=4)
ax.text(.415, .122, "Age Associated GRN", fontsize=5.4, ha="center", va="center", zorder=20)
for x, s in [(.070, "Cell Types"), (.160, "TFs"), (.236, "Peaks"), (.300, "Genes")]:
    ax.text(x, .052, s, fontsize=5.2, ha="center", color="#555", zorder=20)

# ---- row 3 right: model schematic ----
title(ax, .750, .228, "Cell Language Model")
seqx = np.linspace(.535, .612, 55)
ax.plot(seqx, .190+.005*np.sin(np.linspace(0, 12, 55)), color="#7f8c8d", lw=.8)
ax.plot(seqx, .181+.005*np.cos(np.linspace(0, 12, 55)), color="#7f8c8d", lw=.8)
ax.text(.573, .206, "Open Chromatin\nSequence", fontsize=5.6, ha="center", color=INK, zorder=20)
for i, sd in enumerate([41, 42, 43]): cell(ax, .660+i*.013, .178+(i % 2)*.009, r=.011, seed=sd, z=6)
ax.add_patch(FancyBboxPatch((.640, .162), .054, .036, boxstyle="round,pad=0,rounding_size=.012",
                            fc="none", ec="#8a8a8a", lw=.9, zorder=5))
ax.text(.667, .150, "CIMA-CLM", fontsize=5.8, ha="center", weight="bold", color=INK, zorder=20)
dna(ax, .568, .130, w=.018, h=.028, n=1.7, lw=.9)
ax.text(.572, .104, "scRNA-seq\nData", fontsize=5.6, ha="center", color=INK, zorder=20)
arr(ax, (.616, .186), (.638, .184), c="#7f8c8d", lw=.9)
arr(ax, (.592, .118), (.638, .158), c="#e84393", lw=.9, rad=.2)
arr(ax, (.698, .190), (.752, .200), c="#3498db", lw=.9, rad=-.15)
arr(ax, (.698, .168), (.752, .128), c="#e84393", lw=.9, rad=.15)
ax.text(.742, .203, "Cell Type-\nSpecific", fontsize=5.0, color="#e84393", zorder=20)
ax.text(.878, .208, "Peak Value Prediction", fontsize=6.2, ha="center", weight="bold",
        color=INK, zorder=20)
xs = np.linspace(0, 1, 120)
for c, mu, sg, h in [("#e74c3c", .18, .05, 1.), ("#f39c12", .34, .045, .72),
                     ("#27ae60", .50, .05, .88), ("#3498db", .66, .042, .60),
                     ("#9b59b6", .82, .05, .78)]:
    ax.fill_between(.782+xs*.195, .162, .162+h*np.exp(-(xs-mu)**2/(2*sg**2))*.030,
                    color=c, alpha=.8, lw=0, zorder=4)
ax.plot([.782, .977], [.162, .162], color="#666", lw=.6, zorder=5)
ax.text(.878, .128, "Single-Nucleotide\nPermutation Analysis", fontsize=6.2, ha="center",
        weight="bold", color=INK, zorder=20)
# overlapping fills blend into one muddy colour; keep them light and stroke each
xa = np.linspace(0, 1, 200)
base = .60*np.exp(-(xa-.42)**2/.006)+.95*np.exp(-(xa-.55)**2/.004)+.45*np.exp(-(xa-.66)**2/.005)
# keep overlapping curves distinguishable: offset the peaks, vary the
# amplitude and stroke each one -- tuning alpha alone blends them into mud
for c, sh, dx in [("#3498db", .00, .000), ("#e74c3c", .22, .018),
                  ("#f39c12", -.18, -.015), ("#27ae60", .10, .032)]:
    bs = (.60*np.exp(-(xa-.42-dx)**2/.006) + .95*np.exp(-(xa-.55-dx)**2/.004)
          + .45*np.exp(-(xa-.66-dx)**2/.005))
    yv = .052+bs*(1+sh)*.028
    ax.fill_between(.782+xa*.195, .052, yv, color=c, alpha=.10, lw=0, zorder=4)
    ax.plot(.782+xa*.195, yv, color=c, lw=.85, zorder=5, solid_capstyle="round")
ax.text(.770, .072, "Accessibility", fontsize=5.2, rotation=90, va="center", color=INK, zorder=20)
seq_logo(ax, .800, .018, [("A", .5), ("T", .35), ("C", .9), ("G", .55), ("T", .45), ("G", .8),
                          ("C", .4), ("C", .6), ("T", .3), ("A", .7), ("A", .4)],
         w=.0150, hmax=.024)

report(fig, ax)
fig.savefig("gallery/overview_figure.png", dpi=400, bbox_inches="tight", facecolor="white")
fig.savefig("gallery/overview_figure.pdf", bbox_inches="tight", facecolor="white")
print("saved gallery/overview_figure.png / .pdf")