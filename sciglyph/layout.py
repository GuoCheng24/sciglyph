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

__all__ = ["text_collisions", "missing_glyphs", "report"]


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
    glyphs = missing_glyphs(fig)
    print(f"[sciglyph.layout] {n} text objects")
    if not hits:
        print("  OK - no text collisions")
    else:
        for a, b, frac in hits:
            print(f"  ! '{a}' x '{b}' overlap {frac * 100:.0f}%")
    if glyphs:
        print(f"  ! {len(glyphs)} character(s) the font cannot draw - these render "
              f"as empty boxes:")
        for g in glyphs[:6]:
            print(f"      {g}")
        print("      Draw symbols instead of typing them (see arch.snowflake).")
    print("  Note: text hidden behind artwork is not detectable here - "
          "always eyeball the rendered figure.")
    return len(hits) + len(glyphs)


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
