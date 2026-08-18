"""Biological and omics glyphs for Nature/Science-style overview figures.

These figures -- the ones that open a paper and summarise the whole study --
are usually drawn in BioRender or Illustrator. This module draws them in plain
matplotlib instead, which buys you three things a subscription tool cannot:
the figure is **reproducible**, it is **diffable** under version control, and
it can be **driven by your actual data**.

All coordinates are in figure-fraction space, i.e. set up your axes as::

    fig = plt.figure(figsize=(7.2, 8.2), dpi=400)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    sciglyph.bio.set_canvas(fig)          # <- required, see below

Fonts: Arial/Helvetica are often unavailable on Linux. `RC` falls back to
Liberation Sans (metric-compatible with Arial) and sets ``pdf.fonttype = 42``
so that text stays editable in the PDF -- a hard requirement at most journals.
"""

import numpy as np
from matplotlib.patches import (FancyBboxPatch, Ellipse, PathPatch,
                                FancyArrowPatch, Rectangle, Polygon)
from matplotlib.path import Path
from matplotlib.textpath import TextPath
from matplotlib.transforms import Affine2D
from matplotlib.font_manager import FontProperties

from ._canvas import set_canvas, aspect
from ._canvas import circle as _circ

__all__ = ["RC", "set_canvas", "person", "dna", "cell", "lipid", "metabolite",
           "nucleosome_chain", "umap_layer", "seq_logo", "stacked_planes",
           "rbox", "arr"]

_FP = FontProperties(family="Liberation Sans", weight="bold")

#: Drop-in rcParams for journal figures: ``plt.rcParams.update(sciglyph.bio.RC)``
RC = {"font.family": "Liberation Sans", "font.size": 7, "axes.linewidth": 0.6,
      "pdf.fonttype": 42, "ps.fonttype": 42}

# Aspect-ratio compensation lives in `_canvas` so that `bio` and `arch` share
# one canvas registration -- calling `set_canvas` once covers both modules.


def person(ax, x, y, s=1.0, fc="#e88a72", z=3):
    """Human silhouette, for cohort/population panels.

    Returns the glyph's actual width -- use it to set the spacing instead of
    guessing. Getting this wrong is the classic failure: with a torso wider
    than the step between glyphs, a row of people fuses into a solid wall.
    A safe rule is ``step >= 1.3 * person(...)``.
    """
    _circ(ax, (x, y + .62 * s), .15 * s, fc=fc, ec="none", zorder=z)
    k = s / aspect()
    body = Path([(x - .16 * k, y + .46 * s), (x - .17 * k, y - .04 * s),
                 (x - .07 * k, y - .04 * s), (x - .065 * k, y - .52 * s),
                 (x - .015 * k, y - .52 * s), (x - .010 * k, y - .04 * s),
                 (x + .010 * k, y - .04 * s), (x + .015 * k, y - .52 * s),
                 (x + .065 * k, y - .52 * s), (x + .07 * k, y - .04 * s),
                 (x + .17 * k, y - .04 * s), (x + .16 * k, y + .46 * s),
                 (x - .16 * k, y + .46 * s)],
                [Path.MOVETO] + [Path.LINETO] * 11 + [Path.CLOSEPOLY])
    ax.add_patch(PathPatch(body, fc=fc, ec="none", zorder=z))
    return .34 * s


def dna(ax, x, y, w=.5, h=1., n=3, cols=("#e94f37", "#2f7fc1"), z=3, lw=1.6):
    """DNA double helix: two sine strands in antiphase plus base-pair rungs."""
    t = np.linspace(0, n * 2 * np.pi, 240)
    yy = y + (t / t.max() - .5) * h
    x1, x2 = x + w / 2 * np.sin(t), x + w / 2 * np.sin(t + np.pi)
    ax.plot(x1, yy, color=cols[0], lw=lw, solid_capstyle="round", zorder=z)
    ax.plot(x2, yy, color=cols[1], lw=lw, solid_capstyle="round", zorder=z)
    for i in range(0, len(t), 11):
        ax.plot([x1[i], x2[i]], [yy[i], yy[i]], color="#bbb", lw=.45, zorder=z - 1)


def cell(ax, x, y, r=.3, fc="#cfe3f5", ec="#5f9fd4", nuc="#4a7fb5", z=3,
         gran=7, seed=0):
    """Immune cell: membrane, off-centre nucleus, cytoplasmic granules.

    ``seed`` is explicit so the granule scatter is reproducible -- never leave
    randomness unseeded in a figure you intend to regenerate.
    """
    rng = np.random.default_rng(seed)
    _circ(ax, (x, y), r, fc=fc, ec=ec, lw=.9, zorder=z)
    _circ(ax, (x - .08 * r, y + .06 * r), .46 * r, fc=nuc, ec="none",
          alpha=.85, zorder=z + 1)
    for _ in range(gran):
        a, rr = rng.uniform(0, 2 * np.pi), rng.uniform(.55, .85) * r
        _circ(ax, (x + rr / aspect() * np.cos(a), y + rr * np.sin(a)), .07 * r,
              fc=ec, ec="none", alpha=.55, zorder=z + 1)


def lipid(ax, x, y, s=.3, fc="#f3c14a", z=3):
    """Lipid molecule: polar head group with two wavy hydrophobic tails."""
    _circ(ax, (x, y + .5 * s), .20 * s, fc=fc, ec="#c9971f", lw=.7, zorder=z)
    for dx in (-.08 * s, .08 * s):
        t = np.linspace(0, 1, 36)
        ax.plot(x + dx + .045 * s * np.sin(t * 9), y + .40 * s - t * .85 * s,
                color="#c9971f", lw=.9, zorder=z - 1)


def metabolite(ax, x, y, s=.3, fc="#7fc4a8", z=3):
    """Metabolite: a six-membered ring skeleton with vertex atoms."""
    a = np.linspace(0, 2 * np.pi, 7)
    px = x + s * .45 / aspect() * np.cos(a)
    py = y + s * .45 * np.sin(a)
    ax.plot(px, py, color=fc, lw=1.3, zorder=z)
    for i in range(6):
        _circ(ax, (px[i], py[i]), .06 * s, fc=fc, ec="none", zorder=z + 1)


def nucleosome_chain(ax, x0, y, n=4, gap=.020, w=.018, h=.012,
                     fc="#f3b6c6", ec="#d9829b", z=4):
    """Beads-on-a-string chromatin, e.g. to denote accessible peaks."""
    for i in range(n):
        ax.add_patch(Ellipse((x0 + i * gap, y), w, h, fc=fc, ec=ec, lw=.6,
                             zorder=z, angle=-12))
    ax.plot([x0 - gap * .45, x0 + (n - 1) * gap + gap * .45], [y, y],
            color=ec, lw=.7, zorder=z - 1)


def umap_layer(ax, x0, y0, w, h, seed, cmap, shear=.36, npts=850, z=3, alpha=.9):
    """One sheared UMAP card, for the stacked "atlas" look.

    Call repeatedly with increasing ``x0`` and ``z`` to build the familiar
    diagonal stack of embedding panels. The pseudo-perspective comes from an
    affine skew, so the panels stay vector and scale cleanly.
    """
    rng = np.random.default_rng(seed)
    k = rng.integers(4, 8)
    cx, cy = rng.uniform(.2, .8, k), rng.uniform(.2, .8, k)
    idx = rng.integers(0, k, npts)
    px = np.clip(cx[idx] + rng.normal(0, .075, npts), 0, 1)
    py = np.clip(cy[idx] + rng.normal(0, .075, npts), 0, 1)
    tr = Affine2D().skew(0, np.arctan(shear)).scale(w, h).translate(x0, y0) + ax.transData
    ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec="#9a9a9a", lw=.6,
                           alpha=.6, transform=tr, zorder=z - 1))
    ax.scatter(px, py, s=1.0, c=idx, cmap=cmap, alpha=alpha, linewidths=0,
               transform=tr, zorder=z)


def seq_logo(ax, x0, y0, letters, w=.055, hmax=.30, z=5, cols=None):
    """Sequence logo where glyph height encodes information content.

    ``letters`` is ``[("A", 0.5), ("T", 0.35), ...]`` with heights in [0, 1].
    Implemented by scaling the actual glyph outline (``TextPath``) rather than
    drawing text, so the letters stay crisp and fully vector at any size.
    """
    cols = cols or {"A": "#3aa76d", "C": "#2f7fc1", "G": "#f6a01a", "T": "#e94f37"}
    for i, (ch, hh) in enumerate(letters):
        tp = TextPath((0, 0), ch, size=1, prop=_FP)
        bb = tp.get_extents()
        tr = (Affine2D().translate(-bb.x0, -bb.y0)
              .scale(w / bb.width, (hmax * hh) / bb.height)
              .translate(x0 + i * w * 1.06, y0) + ax.transData)
        ax.add_patch(PathPatch(tp, transform=tr, fc=cols[ch], ec="none", zorder=z))


def stacked_planes(ax, x0, y0, w, h, cols, dy=.022, shear=.42, npts=40,
                   seed=0, z=3):
    """Stacked scatter planes, e.g. multi-omics layers over shared components."""
    rng = np.random.default_rng(seed)
    for i, c in enumerate(cols):
        tr = (Affine2D().skew(0, np.arctan(shear)).scale(w, h)
              .translate(x0, y0 + i * dy) + ax.transData)
        ax.add_patch(Rectangle((0, 0), 1, 1, fc="white", ec=c, lw=.9, alpha=.8,
                               transform=tr, zorder=z + i))
        ax.scatter(rng.uniform(.08, .92, npts), rng.uniform(.1, .9, npts), s=1.3,
                   c=c, alpha=.8, linewidths=0, transform=tr, zorder=z + i + 1)


def rbox(ax, x, y, w, h, fc, ec="none", lw=.8, r=.012, z=1):
    """Rounded container box."""
    ax.add_patch(FancyBboxPatch((x, y), w, h,
                                boxstyle=f"round,pad=0,rounding_size={r}",
                                fc=fc, ec=ec, lw=lw, zorder=z))


def arr(ax, p, q, c="#5a5a5a", lw=1.0, rad=0., z=6, style="-|>", ms=7):
    """Curved arrow. Use ``style='|-|'`` for an inhibition (T-bar) connector."""
    ax.add_patch(FancyArrowPatch(p, q, connectionstyle=f"arc3,rad={rad}",
                                 arrowstyle=style, mutation_scale=ms, lw=lw,
                                 color=c, zorder=z, shrinkA=2, shrinkB=2))

# --- Readability note ----------------------------------------------------
# Stacking several translucent `fill_between` bands in the same region blends
# them into one muddy colour and destroys the grouping you were trying to show.
# If you need overlapping distributions to stay distinguishable: keep the fill
# very light (alpha <= 0.15), stroke each curve with a solid line, AND offset
# the peaks. Tuning alpha alone is not enough.
