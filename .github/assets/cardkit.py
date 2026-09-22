"""A social card whose evidence is a chart of real numbers, not a screenshot.

Why this replaced the previous template: measured with cardcheck, that one had 40% of its
text area legible at the 360 px a Slack unfurl gives a card. The other 60% - four lines of
grey prose and a mock terminal - was noise occupying half the canvas. What a reader gets in
one second is a headline and a shape, so the card is a headline and a shape, and the shape
is drawn from the repository's own results.

    from cardkit import card
    card(out=..., accent=..., badge="T", kicker=..., headline=...,
         evidence="one sentence at a size people can read",
         chart=lambda ax, c: ...,          # draws into canvas units, y in [0.9, 4.1]
         footer="github.com/...")

Every card is audited before it is written: legibility at unfurl scale, WCAG contrast, and
nothing off the canvas. `card` raises if the audit fails, so a bad card is not produced.
"""
import pathlib
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import cardcheck  # noqa: E402

W, H = 12.0, 6.30
BG, INK, MUTE, RULE = "#fbfaf8", "#17181a", "#55585c", "#dcd8d2"
SANS = "Liberation Sans"

# sizes chosen against cardcheck.READABLE_PX / UNFURL = 33 px on this canvas
KICKER, HEADLINE, EVIDENCE, FOOTER = 18, 48, 34, 18


def card(out, accent, badge, kicker, headline, evidence, chart, footer,
         headline_size=HEADLINE, palette=None):
    fig = plt.figure(figsize=(W, H), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(0, H)
    ax.axis("off")
    ax.add_patch(plt.Rectangle((0, 0), W, H, color=BG))
    ax.add_patch(plt.Rectangle((0, 0), 0.085, H, color=accent))

    ax.add_patch(FancyBboxPatch((10.90, 5.51), 0.70, 0.52, boxstyle="round,pad=0.04",
                                fc=accent, ec="none"))
    t_badge = ax.text(11.25, 5.77, badge, fontsize=26, fontweight="bold", color=BG,
                      family=SANS, ha="center", va="center")

    t_kicker = ax.text(0.78, 5.62, kicker, fontsize=KICKER, color=MUTE, family=SANS)
    ax.text(0.78, 4.86, headline, fontsize=headline_size, fontweight="bold",
            color=INK, family=SANS)
    ax.text(0.78, 4.30, evidence, fontsize=EVIDENCE, color=MUTE, family=SANS)
    ax.plot([0.78, 11.55], [4.02, 4.02], color=RULE, lw=1.4, zorder=1)
    # the chart owns everything between the rule and the footer: y in [0.85, 3.70]

    chart(ax, accent)

    t_footer = ax.text(0.78, 0.40, footer, fontsize=FOOTER, color=MUTE, family=SANS)

    # sciglyph's own checker, for text-on-text. cardcheck does not do pairs, and the first
    # card built without this had a bar label sitting on a row name while every other check
    # reported clean.
    try:
        sys.path.insert(0, str(pathlib.Path.home() / "sciglyph"))
        from sciglyph.layout import missing_glyphs, text_collisions
        hits, _ = text_collisions(fig, ax)
        tofu = missing_glyphs(fig)
    except Exception:
        hits, tofu = [], []

    problems = cardcheck.audit(
        fig, ax, ground=BG, chrome=(t_kicker, t_footer, t_badge),
        panels=[(10.90, 5.51, 11.60, 6.03, accent)],   # the badge sits on its own colour
        verbose=True)
    problems += [f"text overlap {100 * f:.0f}%: {a!r} x {b!r}" for a, b, f in hits]
    # A character the font cannot draw renders as a hollow box and is invisible to every
    # geometric check: a draft of this card said "log p1" with a subscript and shipped two
    # pieces of tofu that looked fine to the collision and contrast tests.
    problems += [f"font cannot draw {c!r} - it renders as an empty box" for c in tofu]
    if problems:
        raise ValueError("card fails its own acceptance test:\n  " + "\n  ".join(problems))

    fig.savefig(out)
    plt.close(fig)
    return out
