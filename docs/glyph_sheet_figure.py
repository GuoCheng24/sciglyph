"""Every public glyph, drawn once and labelled with its call.

A figure library is judged by looking at its catalogue, not by reading an API
table. This sheet is that catalogue: 23 cells, one glyph each, name underneath.
It is also a regression net - if a glyph breaks, its cell breaks visibly.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sciglyph import bio, arch, set_canvas, report, RC

plt.rcParams.update(RC)

COLS, CW, CH = 5, 2.35, 2.05
CELLS = [
    # ---- bio ----
    ("bio.person",        lambda ax: bio.person(ax, .5, .30, s=.52)),
    ("bio.cell",          lambda ax: bio.cell(ax, .5, .52, r=.20, seed=1)),
    ("bio.dna",           lambda ax: bio.dna(ax, .5, .56, w=.24, h=.58, n=3)),   # y is the CENTRE
    ("bio.lipid",         lambda ax: bio.lipid(ax, .5, .50, s=.30)),
    ("bio.metabolite",    lambda ax: bio.metabolite(ax, .5, .50, s=.30)),
    ("bio.nucleosome_chain", lambda ax: bio.nucleosome_chain(ax, .16, .50, n=4, gap=.17, w=.11, h=.075)),
    ("bio.seq_logo",      lambda ax: bio.seq_logo(ax, .16, .28, [("A", .6), ("C", .95), ("G", .4), ("T", .75)], w=.16, hmax=.44)),
    ("bio.umap_layer",    lambda ax: bio.umap_layer(ax, .18, .22, .60, .48, seed=3, cmap="viridis", npts=500)),
    ("bio.stacked_planes", lambda ax: bio.stacked_planes(ax, .16, .30, .58, .34, ["#cfe3f5", "#f3c14a", "#7fc4a8"], dy=.085)),
    ("bio.rbox",          lambda ax: bio.rbox(ax, .18, .30, .64, .40, "#eef2f6", ec="#5f9fd4", lw=1.0, r=.05)),
    ("bio.arr",           lambda ax: bio.arr(ax, (.15, .50), (.85, .50), lw=1.6, ms=11)),
    # ---- arch ----
    ("arch.cuboid",       lambda ax: arch.cuboid(ax, .28, .28, .40, .40, d=.10)),
    ("arch.feature_stack", lambda ax: arch.feature_stack(ax, .28, .24, n=4, w=.055, h=.50, d=.045, gap=.028)),
    ("arch.trapezoid",    lambda ax: arch.trapezoid(ax, .32, .22, .34, .56, label="Enc", fs=9)),
    ("arch.module_stack", lambda ax: arch.module_stack(ax, .26, .20, .48, .60, ["Conv", "BN", "ReLU"], fs=8)),
    ("arch.dashed_group", lambda ax: arch.dashed_group(ax, .14, .18, .70, .55, "(a) branch", fs=8)),
    ("arch.embedding_space", lambda ax: arch.embedding_space(ax, .50, .48, rx=.16, ry=.30, seed=5, per=8, dot=.5)),
    ("arch.image_thumb",  lambda ax: arch.image_thumb(ax, .26, .22, .46, .55, seed=3, mask=True)),
    ("arch.flow",         lambda ax: arch.flow(ax, (.15, .40), (.85, .60), rad=-.25, lw=1.6, ms=11)),
    ("arch.op_circle",    lambda ax: arch.op_circle(ax, .5, .5, sym=r"$\oplus$", r=.13, fs=13)),
    ("arch.snowflake",    lambda ax: arch.snowflake(ax, .5, .52, s=.14, lw=1.6)),
    ("arch.loss_tag",     lambda ax: arch.loss_tag(ax, .5, .52, r"$L_{topo}$", fs=13)),
    ("arch.bracket",      lambda ax: arch.bracket(ax, .15, .85, .55, lw=1.4, tick=.09)),
]

rows = (len(CELLS) + COLS - 1) // COLS
fig = plt.figure(figsize=(COLS * CW, rows * CH + .45), dpi=200)
fig.text(.5, 1 - .18 / (rows * CH + .45), "sciglyph — every glyph, one call each",
         ha="center", fontsize=13, weight="bold", color="#1a1a1a")

for i, (name, draw) in enumerate(CELLS):
    r, c = divmod(i, COLS)
    ax = fig.add_axes([c / COLS + .010, 1 - (r + 1) * CH / (rows * CH + .45) - .012,
                       1 / COLS - .020, CH / (rows * CH + .45) - .030])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    ax.add_patch(plt.Rectangle((0, .13), 1, .87, fc="#fbfaf8", ec="#ddd8d0",
                               lw=.8, zorder=0, clip_on=False))
    try:
        draw(ax)
    except Exception as e:                     # a broken glyph must be visible, not skipped
        ax.text(.5, .55, "BROKEN\n%s" % type(e).__name__, ha="center", color="#c0392b")
    ax.text(.5, .015, name, ha="center", fontsize=8.6, family="monospace", color="#4a4a4a")

out = Path(__file__).parent / "glyph-sheet.png"
fig.savefig(out, dpi=200, facecolor="white")
print("saved", out)
