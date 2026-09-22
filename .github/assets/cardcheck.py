"""Objective acceptance tests for a social card, so "does it look good" stops being taste.

A card is drawn at 1200x630 and unfurled at about 360 px wide in Slack, a scale of 0.30.
Three things are then checkable rather than arguable:

LEGIBILITY  Text a reader is meant to read must still be >= 10 px after that scale, i.e.
            >= 33 px on the canvas. Anything smaller is texture by definition, and a card
            that is mostly texture is mostly noise. The check reports how much of the ink
            is in each class.

CONTRAST    WCAG 2.1 relative luminance ratio for every text against the ground it sits
            on. 4.5:1 for body, 3:1 for large text - the same bar a web page has to clear.

FRAME       Nothing runs past the canvas, and nothing readable sits on a panel whose
            colour is close to its own.
"""
UNFURL = 360 / 1200
READABLE_PX = 10.0


def _lum(c):
    def f(v):
        return v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4
    return 0.2126 * f(c[0]) + 0.7152 * f(c[1]) + 0.0722 * f(c[2])


def contrast(fg, bg):
    """WCAG 2.1 contrast ratio between two matplotlib colours."""
    from matplotlib.colors import to_rgb
    a, b = _lum(to_rgb(fg)), _lum(to_rgb(bg))
    hi, lo = max(a, b), min(a, b)
    return (hi + 0.05) / (lo + 0.05)


def audit(fig, ax, ground, panels=(), chrome=(), min_ratio=4.5, verbose=True):
    """Return a list of problems. Empty list means the card passes.

    ``chrome`` is the set of Text objects that carry no message - a kicker, a footer URL -
    which nobody needs to read in a thumbnail. Everything else is the message and must clear
    the legibility floor. The role cannot be inferred from geometry, so the caller declares
    it; an earlier version measured legible *area* instead and was dominated by the length of
    the footer, which made every card fail the harder it tried.

    ``panels`` is a list of ``(x0, y0, x1, y1, colour)`` in canvas units, for regions whose
    background is not ``ground``.
    """
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    W, H = (v * 100 for v in fig.get_size_inches())
    floor = READABLE_PX / UNFURL
    problems, chrome_area, message_area = [], 0.0, 0.0
    chrome = set(id(t) for t in chrome)

    for t in ax.texts:
        s = t.get_text().strip()
        if not s:
            continue
        box = t.get_window_extent(r)
        size_px = t.get_fontsize()
        area = box.width * box.height

        cx, cy = (box.x0 + box.x1) / 2 / 100, (box.y0 + box.y1) / 2 / 100
        if box.x1 > W - 20 or box.x0 < 0 or box.y1 > H or box.y0 < 0:
            problems.append(f"off canvas: {s[:40]!r} ends at x={box.x1:.0f} of {W:.0f}")

        bg = ground
        for x0, y0, x1, y1, col in panels:
            if x0 <= cx <= x1 and y0 <= cy <= y1:
                bg = col
        ratio = contrast(t.get_color(), bg)
        need = 3.0 if size_px >= 24 else min_ratio
        if ratio < need:
            problems.append(
                f"contrast {ratio:.1f}:1 (needs {need}:1) for {s[:36]!r} on {bg}")

        declared = any(x0 <= cx <= x1 and y0 <= cy <= y1 for x0, y0, x1, y1, _ in panels)
        # Text on top of filled artwork the caller did not declare. The 128-tile grid on one
        # card was drawn as patches, so every check passed while a headline sat on top of it.
        for pt in (() if declared else ax.patches):
            pb = pt.get_window_extent()
            fc = pt.get_facecolor()
            if len(fc) > 3 and fc[3] < 0.5:
                continue
            if pb.width * pb.height > 0.55 * (W * H):      # the card's own background
                continue
            dx = min(box.x1, pb.x1) - max(box.x0, pb.x0)
            dy = min(box.y1, pb.y1) - max(box.y0, pb.y0)
            # Any real overlap, not a share of the text box. A row of tiles crossing a
            # headline covers a few percent of that box and is still a headline with tiles
            # through it; the first threshold here was 12% and passed it twice.
            if dx > 2 and dy > 2:
                problems.append(
                    f"{s[:32]!r} sits on undeclared artwork "
                    f"({dx:.0f}x{dy:.0f} px of its box)")
                break

        if id(t) in chrome:
            chrome_area += area
            continue
        message_area += area
        if size_px < floor:
            problems.append(
                f"{size_px:.0f} px is {size_px * UNFURL:.1f} px at 360 - unreadable: {s[:40]!r}")

    # Texts that merely touch are not an overlap and pass the collision test, but they read
    # as one run-on word: "SUSPECT10.9999/..." and "ERRORthe table has...". A gap of less than
    # a third of a character between two texts on the same line is reported.
    items = [(t, t.get_window_extent(r)) for t in ax.texts if t.get_text().strip()]
    for i in range(len(items)):
        for j in range(len(items)):
            if i == j:
                continue
            (ta, ba), (tb, bb) = items[i], items[j]
            same_line = min(ba.y1, bb.y1) - max(ba.y0, bb.y0) > 0.4 * min(ba.height, bb.height)
            gap = bb.x0 - ba.x1
            per_char = ba.width / max(len(ta.get_text().strip()), 1)
            # gap may be negative: the boxes genuinely overlap, by an area too small for
            # the collision test to notice. Both cases read the same way on the page.
            if same_line and gap < 0.33 * per_char and bb.x0 > ba.x0:
                problems.append(
                    f"{ta.get_text()[:22]!r} and {tb.get_text()[:22]!r} are {gap:.0f} px "
                    "apart and read as one word")

    if message_area and chrome_area > 0.45 * message_area:
        problems.append(
            f"chrome is {100 * chrome_area / (chrome_area + message_area):.0f}% of the "
            "text area; it should stay out of the way")
    if verbose:
        print(f"  [cardcheck] message text all >= {floor:.0f} px on canvas "
              f"(= {READABLE_PX:.0f} px at 360); chrome "
              f"{100 * chrome_area / max(chrome_area + message_area, 1):.0f}% of text area")
        for p_ in problems:
            print(f"  ! {p_}")
        if not problems:
            print("  [cardcheck] passes: legibility, contrast, frame")
    return problems
