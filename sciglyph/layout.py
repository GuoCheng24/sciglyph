"""Pre-flight collision detection for figure layouts.

Why this exists: when you assemble a publication figure from many primitives,
the primitives themselves are rarely the problem -- the layout is. Titles get
covered by artwork, labels overlap, panels drift out of their box.

This module catches text-vs-text overlaps *before* you save, using the real
rendered bounding boxes. No manual bookkeeping is required.

A note on what it does NOT cover: text hidden *behind artwork* (a title covered
by a shaded panel) is invisible to this check. Always look at the rendered PNG
with your own eyes as the final step.
"""

__all__ = ["text_collisions", "patch_collisions", "missing_glyphs", "report"]


def missing_glyphs(fig):
    """Characters the chosen font cannot draw.

    Matplotlib renders a missing character as an empty box and only mentions it
    in a warning, which is easy to miss in a long build log and invisible in a
    thumbnail. Symbols are the usual casualty: a snowflake, a check mark or a
    cross typed as a literal will silently become tofu in most sans fonts.

    Draw such marks instead of typing them.
    """
    import warnings

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        fig.canvas.draw()
        out = []
        for w in caught:
            msg = str(w.message)
            if "missing from font" in msg:
                out.append(msg.split(" missing from")[0].replace("Glyph ", "").strip())
    return sorted(set(out))


def patch_collisions(fig, ax, thr=0.06, min_frac=0.004):
    """Artwork that overlaps when it should not.

    Containment is deliberately ignored. A background panel overlaps everything
    inside it completely, and that is the layout working as intended; the same
    is true of a label sitting on its own box. What actually breaks a figure is
    two *sibling* shapes whose edges cross - a row of boxes laid out slightly
    too wide, so each one bleeds into the next and covers its neighbour's text.

    Text-level checks cannot see this: the strings themselves may not overlap
    at all while one box is drawn straight over another.

    Returns ``[(index_a, index_b, overlap_fraction), ...]``, worst first.
    """
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    fw, fh = fig.canvas.get_width_height()
    page = float(fw * fh) or 1.0

    items = []
    for i, p in enumerate(ax.patches):
        try:
            bb = p.get_window_extent(renderer)
        except Exception:
            continue
        area = bb.width * bb.height
        if area / page < min_frac:      # hairlines, ticks, markers
            continue
        # An unfilled dashed shape is an annotation - a ring drawn around the
        # thing it refers to. Overlapping is the entire point of it, so it is
        # excluded rather than reported every single time.
        fc = p.get_facecolor()
        unfilled = len(fc) > 3 and fc[3] < 0.01
        ls = p.get_linestyle()
        dashed = not (ls in ("solid", "-") or (isinstance(ls, tuple) and ls[1] is None))
        if unfilled and dashed:
            continue
        items.append((i, bb, area, type(p).__name__))

    hits = []
    for a in range(len(items)):
        for b in range(a + 1, len(items)):
            ia, ba, area_a, na = items[a]
            ib, bb_, area_b, nb = items[b]
            dx = min(ba.x1, bb_.x1) - max(ba.x0, bb_.x0)
            dy = min(ba.y1, bb_.y1) - max(ba.y0, bb_.y0)
            if dx <= 0 or dy <= 0:
                continue
            inter = dx * dy
            smaller = min(area_a, area_b)
            # containment: the smaller shape sits (almost) entirely inside the
            # larger one -> a panel and its contents, not a collision
            if inter / smaller > 0.92:
                continue
            frac = inter / smaller
            if frac > thr:
                hits.append((f"{na}#{ia}", f"{nb}#{ib}", frac))
    return sorted(hits, key=lambda h: -h[2])


def text_collisions(fig, ax, thr=0.10):
    """Return ``([(text_a, text_b, overlap_fraction), ...], n_text_objects)``.

    Overlap is measured as the intersection area divided by the area of the
    *smaller* of the two text boxes, so a small label swallowed by a big title
    is reported at close to 1.0.

    Parameters
    ----------
    fig, ax : matplotlib Figure and Axes
    thr : float
        Report a pair when the overlap fraction exceeds this value.
    """
    fig.canvas.draw()  # bounding boxes do not exist before the first draw
    renderer = fig.canvas.get_renderer()
    items = [
        (t.get_text().replace("\n", "/")[:26], t.get_window_extent(renderer))
        for t in ax.texts
        if t.get_text().strip()
    ]
    hits = []
    for i in range(len(items)):
        for j in range(i + 1, len(items)):
            (name_a, box_a), (name_b, box_b) = items[i], items[j]
            dx = min(box_a.x1, box_b.x1) - max(box_a.x0, box_b.x0)
            dy = min(box_a.y1, box_b.y1) - max(box_a.y0, box_b.y0)
            if dx > 0 and dy > 0:
                smaller = min(box_a.width * box_a.height, box_b.width * box_b.height)
                frac = dx * dy / max(smaller, 1e-9)
                if frac > thr:
                    hits.append((name_a, name_b, frac))
    return sorted(hits, key=lambda h: -h[2]), len(items)


def report(fig, ax, thr=0.10):
    """Print a human-readable collision report. Returns the number of hits."""
    hits, n = text_collisions(fig, ax, thr)
    patches = patch_collisions(fig, ax)
    glyphs = missing_glyphs(fig)
    print(f"[sciglyph.layout] {n} text objects, {len(ax.patches)} patches")
    if not hits:
        print("  OK - no text collisions")
    else:
        for a, b, frac in hits:
            print(f"  ! '{a}' x '{b}' overlap {frac * 100:.0f}%")
    if patches:
        print(f"  ! {len(patches)} pair(s) of artwork overlap without one containing "
              f"the other:")
        for a, b, frac in patches[:5]:
            print(f"      {a} x {b}  ({frac * 100:.0f}% of the smaller)")
        print("      Sibling shapes drawn over each other - check the row widths.")
    if glyphs:
        print(f"  ! {len(glyphs)} character(s) the font cannot draw - these render "
              f"as empty boxes:")
        for g in glyphs[:6]:
            print(f"      {g}")
        print("      Draw symbols instead of typing them (see arch.snowflake).")
    print("  Note: these are geometric checks. Whether the figure actually reads "
          "well still needs your eyes.")
    return len(hits) + len(patches) + len(glyphs)


if __name__ == "__main__":
    import sys
    import runpy

    if len(sys.argv) < 2:
        sys.exit("usage: python -m sciglyph.layout <figure_script.py>  "
                 "(the script must expose `fig` and `ax` at module level)")
    ns = runpy.run_path(sys.argv[1])
    if "fig" not in ns or "ax" not in ns:
        sys.exit("script does not expose `fig` / `ax` at module level")
    sys.exit(1 if report(ns["fig"], ns["ax"]) else 0)
