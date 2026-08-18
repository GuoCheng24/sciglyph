"""Neural-network architecture glyphs (TPAMI / CVPR / NeurIPS style).

A different visual language from `sciglyph.bio`: 3-D feature blocks, module
stacks, data-flow arrows, dashed sub-figure groups, loss annotations and
contrastive embedding spaces.

Architecture figures are wide and short (10:2 is typical), which makes the
aspect-ratio correction essential -- **call `set_canvas(fig)` first**, or every
circular element will be stretched into a rugby ball.

    import matplotlib.pyplot as plt
    from sciglyph import arch, set_canvas, RC
    plt.rcParams.update(RC)
    fig = plt.figure(figsize=(12, 3.1), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    set_canvas(fig)
"""

import numpy as np
from matplotlib.patches import (Rectangle, Polygon, FancyBboxPatch,
                                FancyArrowPatch, Ellipse, PathPatch)
from matplotlib.path import Path

from ._canvas import set_canvas, aspect
from ._canvas import circle as _circ

__all__ = ["RC", "set_canvas", "cuboid", "feature_stack", "module_stack",
           "trapezoid", "dashed_group", "flow", "op_circle", "snowflake",
           "image_thumb", "embedding_space", "loss_tag", "bracket",
           "BLUE", "GRAY", "GREEN", "PURPLE", "ORANGE"]

RC = {"font.family": "Liberation Sans", "font.size": 7, "axes.linewidth": .6,
      "pdf.fonttype": 42, "ps.fonttype": 42}

# Three-face palettes: (front, top, side) with decreasing lightness.
BLUE = ["#c5d9ee", "#a9c6e4", "#8fb3d9"]
GRAY = ["#dcdcdc", "#c9c9c9", "#b4b4b4"]
GREEN = ["#cfe3cf", "#b9d6b9", "#a2c8a2"]
PURPLE = ["#d9d0e8", "#c6b9dd", "#b3a3d1"]
ORANGE = ["#f6ddc0", "#eecfa8", "#e5c08f"]


def cuboid(ax, x, y, w, h, d=.010, cols=BLUE, z=3, lw=.5, ec="#6f6f6f", alpha=1.):
    """A single 3-D feature block -- the stack of blue slabs in every architecture paper.

    ``d`` is the depth. Note it is a *vertical* quantity: the horizontal
    component is divided by the aspect ratio, otherwise the perspective shears
    absurdly on a wide canvas. Returns the right edge, useful for chaining.
    """
    dx = d / aspect()
    ax.add_patch(Rectangle((x, y), w, h, fc=cols[0], ec=ec, lw=lw, zorder=z,
                           alpha=alpha))
    ax.add_patch(Polygon([(x, y + h), (x + dx, y + h + d), (x + w + dx, y + h + d),
                          (x + w, y + h)], closed=True, fc=cols[1], ec=ec,
                         lw=lw, zorder=z, alpha=alpha))
    ax.add_patch(Polygon([(x + w, y), (x + w + dx, y + d), (x + w + dx, y + h + d),
                          (x + w, y + h)], closed=True, fc=cols[2], ec=ec,
                         lw=lw, zorder=z, alpha=alpha))
    return x + w + dx


def feature_stack(ax, x, y, n=4, w=.010, h=.16, d=.008, gap=.004, cols=BLUE,
                  z=3, taper=0., label=None, fs=6, lab_dy=.022):
    """A row of feature blocks, e.g. the multi-scale output of an encoder.

    ``taper > 0`` shrinks each successive block to suggest falling resolution.

    **Anchor your arrows to the return value** (the right edge) rather than
    hard-coded coordinates -- otherwise changing ``n`` silently breaks every
    connector in the figure.
    """
    right = x
    for i in range(n):
        hh = h * (1 - taper * i / max(n - 1, 1))
        right = cuboid(ax, x + i * (w + gap), y + (h - hh) / 2, w, hh, d, cols, z + i)
    if label:
        ax.text(x + (n * (w + gap)) / 2, y - lab_dy, label, fontsize=fs,
                ha="center", va="top", zorder=z + 20)
    return right


def module_stack(ax, x, y, w, h, labels, cols=None, z=4, fs=5.4, rot=90,
                 ec="#6f6f6f"):
    """A pipeline bar with rotated labels, e.g. ``Conv | BN | ReLU | Conv``."""
    cols = cols or ["#eef4ea", "#dfeada"]
    k = len(labels)
    ww = w / k
    for i, s in enumerate(labels):
        ax.add_patch(Rectangle((x + i * ww, y), ww, h, fc=cols[i % len(cols)],
                               ec=ec, lw=.5, zorder=z))
        ax.text(x + i * ww + ww / 2, y + h / 2, s, fontsize=fs, ha="center",
                va="center", rotation=rot, zorder=z + 1)
    return x + w


def trapezoid(ax, x, y, w, h, shrink=.34, fc="#cfe0f2", ec="#6f6f6f", z=4,
              label=None, fs=7, rot=90):
    """Encoder/decoder trapezoid. ``shrink`` is the relative narrowing at the right."""
    dy = h * shrink / 2
    ax.add_patch(Polygon([(x, y), (x + w, y + dy), (x + w, y + h - dy), (x, y + h)],
                         closed=True, fc=fc, ec=ec, lw=.6, zorder=z))
    if label:
        ax.text(x + w / 2, y + h / 2, label, fontsize=fs, ha="center",
                va="center", rotation=rot, zorder=z + 1)
    return x + w


def dashed_group(ax, x, y, w, h, label=None, c="#4a7a3a", z=1, fs=7.2, lw=.9,
                 dash=(0, (4, 2.5)), lab_pos="top", fc="none", alpha=1.):
    """Dashed sub-figure group with an italic caption -- the ``(a) / (b) / (c)`` language.

    The caption is anchored with an explicit vertical alignment. With the
    default baseline alignment it grows *into* the box and ends up sitting on
    the dashed border, which is especially visible for ``lab_pos='bottom'``.
    """
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle="round,pad=0,rounding_size=.006",
                                fc=fc, ec=c, lw=lw, ls=dash, zorder=z, alpha=alpha))
    if label:
        if lab_pos == "top":
            yy, va = y + h + .014, "bottom"
        else:
            yy, va = y - .012, "top"
        ax.text(x + w / 2, yy, label, fontsize=fs, ha="center", va=va, color=c,
                style="italic", zorder=z + 30)


def flow(ax, p, q, c="#4a4a4a", lw=1.0, rad=0., style="-|>", ms=8, z=10, ls="-"):
    """Data-flow arrow. ``ls='--'`` for auxiliary/gradient paths."""
    ax.add_patch(FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}",
                                 arrowstyle=style, mutation_scale=ms, lw=lw,
                                 color=c, zorder=z, shrinkA=1.5, shrinkB=1.5,
                                 linestyle=ls))


def op_circle(ax, x, y, sym="U", r=.011, fc="white", ec="#4a4a4a", z=12, fs=5.6):
    """Circled operator: upsample, add, concat. Pass mathtext, e.g. ``r'$\\oplus$'``."""
    _circ(ax, (x, y), r, fc=fc, ec=ec, lw=.7, zorder=z)
    ax.text(x, y, sym, fontsize=fs, ha="center", va="center", zorder=z + 1)


def snowflake(ax, x, y, s=.012, c="#5aa7d8", z=12, lw=.8):
    """Frozen-backbone marker, drawn as strokes.

    Deliberately drawn rather than typed: the Unicode snowflake (U+2744) is
    missing from many sans fonts and renders as a tofu box. As a rule, do not
    put symbol codepoints in figure text -- draw them.
    """
    ar = aspect()
    for a in np.arange(0, np.pi, np.pi / 3):
        dx, dy = s * np.cos(a) / ar, s * np.sin(a)
        ax.plot([x - dx, x + dx], [y - dy, y + dy], color=c, lw=lw, zorder=z,
                solid_capstyle="round")
        for sgn in (-1, 1):
            bx, by = x + sgn * dx * .62, y + sgn * dy * .62
            for da in (-.7, .7):
                ax.plot([bx, bx + s * .30 * np.cos(a + da) / ar],
                        [by, by + s * .30 * np.sin(a + da)], color=c,
                        lw=lw * .8, zorder=z)


def image_thumb(ax, x, y, w, h, seed=0, mask=False, z=5, ec="#4a4a4a",
                label=None, fs=6, mask_c="#e05a4a"):
    """Placeholder input thumbnail (smoothed noise in an elliptical field).

    Use it to block out and align the figure before real images are ready;
    swap in ``ax.imshow`` of the actual scan for the final version.
    """
    rng = np.random.default_rng(seed)
    g = rng.normal(0, 1, (34, 34))
    for _ in range(3):
        g = (g + np.roll(g, 1, 0) + np.roll(g, -1, 0)
             + np.roll(g, 1, 1) + np.roll(g, -1, 1)) / 5
    yy, xx = np.mgrid[0:34, 0:34]
    rad = np.sqrt(((xx - 17) / 15.) ** 2 + ((yy - 17) / 17.) ** 2)
    img = np.clip((g - g.min()) / (np.ptp(g) + 1e-9) * .8 + .2, 0, 1) * (rad < 1)
    ax.imshow(img, cmap="gray", extent=[x, x + w, y, y + h], zorder=z,
              aspect="auto", interpolation="bilinear")
    ax.add_patch(Rectangle((x, y), w, h, fc="none", ec=ec, lw=.6, zorder=z + 1))
    if mask:
        ax.add_patch(Ellipse((x + w * .62, y + h * .60), w * .26, h * .22,
                             fc=mask_c, ec="white", lw=.5, alpha=.9, zorder=z + 2))
    if label:
        ax.text(x + w / 2, y - .020, label, fontsize=fs, ha="center", va="top",
                zorder=z + 3)
    return x + w


def embedding_space(ax, cx, cy, rx=.055, ry=.30, seed=0, z=5, n_cls=3, per=6,
                    cols=("#c0392b", "#2f7fc1", "#e8b84b"), blob_fc="#e9e9ef",
                    link=True, jitter=.62, bg_pts=0, bg_cols=None, dot=.085,
                    anchor_scale=1.55):
    """Contrastive embedding space: an irregular blob with anchored clusters.

    This is the panel that usually accompanies an InfoNCE / contrastive term.

    ``per`` below ~8 leaves the blob looking empty; published figures are
    typically 10-16 points per cluster. ``bg_pts`` adds faint unclustered
    points to fill the space, and the first point of each cluster is drawn
    larger as the anchor, with links radiating from it.
    """
    rng = np.random.default_rng(seed)
    t = np.linspace(0, 2 * np.pi, 200)
    rr = 1 + .16 * np.sin(3 * t + rng.uniform(0, 6)) + .09 * np.sin(5 * t + rng.uniform(0, 6))
    ax.add_patch(Polygon(np.c_[cx + rx * rr * np.cos(t), cy + ry * rr * np.sin(t)],
                         closed=True, fc=blob_fc, ec="#b9b9c4", lw=.6, zorder=z))
    if bg_pts:
        bg_cols = bg_cols or ("#f2c9c0", "#c9dcef", "#f5e6bd", "#dcd3ea", "#ffffff")
        for k in range(bg_pts):
            a, u = rng.uniform(0, 2 * np.pi), np.sqrt(rng.uniform(0, 1))
            _circ(ax, (cx + rx * .88 * u * np.cos(a), cy + ry * .88 * u * np.sin(a)),
                  rx * dot * .80, fc=bg_cols[k % len(bg_cols)], ec="white",
                  lw=.35, alpha=.95, zorder=z + 1)
    for ci in range(n_cls):
        a0 = 2 * np.pi * ci / n_cls + rng.uniform(-.3, .3)
        ax0, ay0 = cx + rx * .50 * np.cos(a0), cy + ry * .50 * np.sin(a0)
        pts = [(ax0, ay0)]
        for _ in range(per - 1):
            pts.append((ax0 + rng.normal(0, rx * .26 * jitter),
                        ay0 + rng.normal(0, ry * .26 * jitter)))
        if link:
            for px, py in pts[1:]:
                ax.plot([pts[0][0], px], [pts[0][1], py], color=cols[ci % len(cols)],
                        lw=.45, alpha=.75, zorder=z + 2)
        for j, (px, py) in enumerate(pts):
            r = rx * dot * (anchor_scale if j == 0 else 1.)
            _circ(ax, (px, py), r, fc=cols[ci % len(cols)], ec="white", lw=.45,
                  zorder=z + 3 + (1 if j == 0 else 0))


def loss_tag(ax, x, y, tex, c="#8e44ad", fs=8, z=25, ha="center"):
    """Loss annotation, e.g. ``r'$L_{NCE}$'``. Mathtext renders out of the box."""
    ax.text(x, y, tex, fontsize=fs, color=c, ha=ha, va="center", zorder=z)


def bracket(ax, x0, x1, y, c="#8e8e8e", lw=.8, tick=.012, z=8, down=True):
    """Horizontal span bracket, to annotate a range of modules."""
    s = -1 if down else 1
    ax.plot([x0, x1], [y, y], color=c, lw=lw, zorder=z)
    for xx in (x0, x1):
        ax.plot([xx, xx], [y, y + s * tick], color=c, lw=lw, zorder=z)
