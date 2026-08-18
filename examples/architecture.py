#!/usr/bin/env python3
"""A TPAMI/CVPR-style architecture figure, rendered entirely in matplotlib.

The subject here is a topology-aware, distribution-free segmentation
certificate: calibration images and a test image go through a frozen encoder,
a persistent-homology branch and a nonconformity-scoring branch feed a
split-conformal calibration step, and the result is a prediction set carrying
a finite-sample coverage guarantee.

Swap the placeholder thumbnails for real scans and the synthetic score
distribution for your own, and this becomes a submission-ready figure.

Run:  python examples/architecture.py
"""
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
from sciglyph import set_canvas, report, RC
from sciglyph.arch import (feature_stack, module_stack, trapezoid, dashed_group,
                           flow, op_circle, snowflake, image_thumb,
                           embedding_space, loss_tag, BLUE, GREEN)

plt.rcParams.update(RC)
fig = plt.figure(figsize=(12.0, 3.1), dpi=400)
ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
set_canvas(fig)

G_GREEN, G_ORANGE, G_BLUE, G_PURPLE = "#4a7a3a", "#b8860b", "#3a6a9a", "#7a5aa8"

# ---------------- inputs and frozen encoder ----------------
image_thumb(ax, .012, .565, .056, .345, seed=3, mask=True, label="Calibration Set")
image_thumb(ax, .012, .105, .056, .345, seed=8, mask=False, label="Test Image")
trapezoid(ax, .082, .175, .030, .690, shrink=.30, fc="#cfe0f2",
          label="Frozen Encoder", fs=6.6)
snowflake(ax, .097, .905, s=.030, c="#5aa7d8")
flow(ax, (.070, .737), (.080, .640), c="#4a4a4a", lw=.9)
flow(ax, (.070, .277), (.080, .390), c="#4a4a4a", lw=.9)

feature_stack(ax, .124, .615, n=4, w=.0075, h=.235, d=.014, gap=.0035, cols=BLUE)
ax.text(.147, .585, r"$F_{cal}$", fontsize=7.4, ha="center", va="top", zorder=25)
feature_stack(ax, .124, .175, n=4, w=.0075, h=.235, d=.014, gap=.0035, cols=BLUE)
ax.text(.147, .145, r"$F_{test}$", fontsize=7.4, ha="center", va="top", zorder=25)
flow(ax, (.114, .560), (.122, .700), c="#4a4a4a", lw=.9)
flow(ax, (.114, .480), (.122, .320), c="#4a4a4a", lw=.9)

# ---------------- (a) persistent-homology branch ----------------
dashed_group(ax, .186, .565, .300, .360, "(a) Persistent-Homology Feature Branch",
             c=G_GREEN, fs=7.4)
feature_stack(ax, .196, .640, n=3, w=.0070, h=.190, d=.012, gap=.0032, cols=GREEN)
ax.text(.212, .612, r"$\Psi(F_{cal})$", fontsize=6.4, ha="center", va="top", zorder=25)
module_stack(ax, .246, .640, .086, .190, ["Sublevel", "Filtration", "PH", "Barcode"], fs=4.9)
for i, (w_, c) in enumerate([(.052, "#c0392b"), (.034, "#2f7fc1"),
                             (.044, "#27ae60"), (.022, "#8e44ad")]):
    ax.add_patch(Rectangle((.346, .802 - i*.030), w_, .014, fc=c, ec="none", zorder=6))
ax.text(.372, .672, r"$\beta_0,\beta_1$ barcode", fontsize=6.0, ha="center", va="top", zorder=25)
flow(ax, (.336, .735), (.344, .735), c="#4a4a4a", lw=.9)
feature_stack(ax, .422, .640, n=3, w=.0070, h=.190, d=.012, gap=.0032, cols=GREEN)
ax.text(.440, .612, r"$T_{cal}$", fontsize=6.4, ha="center", va="top", zorder=25)
flow(ax, (.406, .735), (.420, .735), c="#4a4a4a", lw=.9)
loss_tag(ax, .212, .952, r"$L_{topo}$", c=G_GREEN, fs=8.4)
flow(ax, (.212, .938), (.212, .908), c=G_GREEN, lw=.9, ls=(0, (3, 2)), style="-|>")

# ---------------- (b) nonconformity scoring ----------------
dashed_group(ax, .186, .095, .300, .335, "(b) Nonconformity Scoring",
             c=G_ORANGE, fs=7.4, lab_pos="bottom")
for x0, lab in [(.200, "Softmax\nMargin"), (.268, "Topo\nMismatch"), (.336, "Boundary\nDistance")]:
    ax.add_patch(FancyBboxPatch((x0, .215), .058, .130,
                                boxstyle="round,pad=0,rounding_size=.010",
                                fc="#fdf0d8", ec="#c8a45a", lw=.7, zorder=5))
    ax.text(x0+.029, .280, lab, fontsize=5.6, ha="center", va="center", zorder=6)
flow(ax, (.258, .280), (.266, .280), c="#4a4a4a", lw=.8)
flow(ax, (.326, .280), (.334, .280), c="#4a4a4a", lw=.8)
op_circle(ax, .410, .280, sym=r"$\oplus$", r=.016, fs=6.4)
flow(ax, (.394, .280), (.400, .280), c="#4a4a4a", lw=.8)
ax.text(.410, .188, r"$s_i$", fontsize=7.0, ha="center", va="top", zorder=25)
flow(ax, (.420, .280), (.452, .280), c="#4a4a4a", lw=.9)
ax.add_patch(Rectangle((.452, .225), .026, .110, fc="#f2e2c0", ec="#c8a45a", lw=.7, zorder=5))
ax.text(.465, .280, "sort", fontsize=5.4, ha="center", va="center", rotation=90, zorder=6)

# ---------------- (c) split-conformal certification ----------------
dashed_group(ax, .506, .095, .330, .830, "(c) Split-Conformal Certification",
             c=G_BLUE, fs=7.4)
# calibration score distribution and the conformal quantile
xs = np.linspace(0, 1, 60); dens = np.exp(-(xs-.42)**2/.045)
for i, xv in enumerate(xs[::2]):
    ax.add_patch(Rectangle((.522+xv*.150, .640), .0042, dens[i*2]*.135,
                           fc="#9fc3e0" if xv < .78 else "#e08a72", ec="none", zorder=5))
ax.plot([.522+.78*.150]*2, [.638, .800], color="#c0392b", lw=1.0, ls=(0, (3, 2)), zorder=8)
ax.text(.640, .812, r"$\hat{q}_{1-\alpha}$", fontsize=7.0, ha="center", color="#c0392b", zorder=25)
ax.text(.597, .612, "calibration scores", fontsize=5.8, ha="center", va="top", zorder=25)
flow(ax, (.486, .735), (.518, .706), c="#4a4a4a", lw=.9, rad=-.12)
flow(ax, (.482, .280), (.518, .620), c="#4a4a4a", lw=.9, rad=.16)

# the coverage guarantee
ax.add_patch(FancyBboxPatch((.518, .448), .156, .092,
                            boxstyle="round,pad=0,rounding_size=.010",
                            fc="#eaf3ea", ec=G_GREEN, lw=.8, zorder=5))
ax.text(.596, .508, r"$\mathbb{P}\left(Y\in\mathcal{C}(X)\right)\geq 1-\alpha$",
        fontsize=7.2, ha="center", va="center", color="#2d5a22", zorder=6)
ax.text(.596, .470, "distribution-free, finite-sample", fontsize=5.2,
        ha="center", va="center", color=G_GREEN, zorder=6)

# empirical vs nominal coverage
bx, by, bw, bh = .540, .150, .120, .168
ax.add_patch(Rectangle((bx, by), bw, bh, fc="white", ec="#9a9a9a", lw=.6, zorder=5))
al = np.linspace(.02, .98, 80)
ax.plot(bx+al*bw, by+(1-al)*bh, color="#999", lw=.7, ls=(0, (2, 2)), zorder=6)
ax.plot(bx+al*bw, by+np.clip((1-al)+.055*np.sin(al*15), 0, 1)*bh,
        color="#2f7fc1", lw=1.1, zorder=7)
ax.text(bx+bw/2, by-.016, r"$\alpha$", fontsize=5.6, ha="center", va="top", zorder=25)
ax.text(bx+bw/2, by+bh+.014, "empirical vs nominal coverage", fontsize=5.4,
        ha="center", va="bottom", zorder=25)

# inclusion rule and the resulting prediction set
ax.add_patch(FancyBboxPatch((.700, .640), .058, .140,
                            boxstyle="round,pad=0,rounding_size=.010",
                            fc="#dce9f5", ec="#7aa5c8", lw=.8, zorder=5))
ax.text(.729, .710, "Include\nif $s\\leq\\hat{q}$", fontsize=5.6, ha="center",
        va="center", zorder=6)
flow(ax, (.676, .710), (.696, .710), c="#4a4a4a", lw=.9)
for i, (dx, a) in enumerate([(0, .95), (.010, .70), (.020, .45)]):
    ax.add_patch(Rectangle((.700+dx, .190+i*.014), .050, .155, fc="#b9d6ea",
                           ec="#5f93bd", lw=.6, alpha=a, zorder=5+i))
ax.text(.734, .160, "Prediction Set", fontsize=6.0, ha="center", va="top", zorder=25)
flow(ax, (.729, .632), (.729, .360), c="#4a4a4a", lw=.9)

# ---------------- certified embedding space ----------------
embedding_space(ax, .912, .545, rx=.042, ry=.310, seed=5, n_cls=3, per=13,
                bg_pts=11, dot=.105, jitter=.56)
ax.text(.912, .196, "Certified Embedding", fontsize=6.2, ha="center", va="top", zorder=25)
# route the contrastive arrow from the prediction set into the blob
flow(ax, (.776, .300), (.884, .430), c=G_PURPLE, lw=1.2, rad=-.24, ms=9)
loss_tag(ax, .912, .945, r"$L_{NCE}$", c=G_PURPLE, fs=8.4)
flow(ax, (.912, .930), (.912, .872), c=G_PURPLE, lw=.9, ls=(0, (3, 2)))

# ---------------- legend ----------------
ax.text(.012, .012, r"$\Psi(\cdot)$  topological feature map", fontsize=5.6, va="bottom", zorder=25)
ax.text(.300, .012, r"$\oplus$  score fusion", fontsize=5.6, va="bottom", zorder=25)
snowflake(ax, .470, .020, s=.014, c="#5aa7d8", lw=.6)
ax.text(.480, .012, "frozen backbone", fontsize=5.6, va="bottom", zorder=25)
ax.plot([.640, .664], [.022, .022], color="#999", lw=.7, ls=(0, (2, 2)), zorder=25)
ax.text(.670, .012, "nominal level", fontsize=5.6, va="bottom", zorder=25)

report(fig, ax)
fig.savefig("gallery/architecture.png", dpi=400, bbox_inches="tight", facecolor="white")
fig.savefig("gallery/architecture.pdf", bbox_inches="tight", facecolor="white")
print("saved gallery/architecture.png / .pdf")
