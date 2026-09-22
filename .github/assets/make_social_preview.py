"""Generate the GitHub social-preview card (1200x630). Reproducible: python3 make_social_preview.py

This library draws schematic figures, so its card is one - built from the same glyphs the README
documents, at a size a reader can see rather than as a thumbnail. An encoder, a latent space, a
decoder and a loss tag: four calls, which is the pitch.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent))
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from cardkit import SANS, card  # noqa: E402

import sciglyph.arch as A  # noqa: E402
from sciglyph import set_canvas  # noqa: E402


def chart(ax, accent):
    set_canvas(ax.figure)
    INK, MUTE = "#17181a", "#55585c"
    A.feature_stack(ax, 0.95, 2.13, n=4, w=0.17, h=1.04, d=0.09, gap=0.05, z=3)
    A.trapezoid(ax, 2.55, 2.13, 0.95, 1.04, shrink=0.42, fc="#cfe0f2", z=4)
    A.cuboid(ax, 4.40, 2.34, 0.62, 0.62, d=0.13, z=4)
    A.trapezoid(ax, 5.95, 2.13, 0.95, 1.04, shrink=-0.42, fc="#cfe0f2", z=4)
    A.feature_stack(ax, 7.85, 2.13, n=4, w=0.17, h=1.04, d=0.09, gap=0.05, z=3)
    # Horizontal, on the measured centre line. An earlier edit rewrote only the first
    # coordinate of each pair, leaving three arrows tilted while the card passed every check -
    # geometry cannot tell a deliberate diagonal from a typo.
    for a, b in [(1.90, 2.48), (3.55, 4.33), (5.15, 5.88), (7.00, 7.80)]:
        A.flow(ax, (a, 2.65), (b, 2.65), c=MUTE, lw=2.4, ms=13)
    A.bracket(ax, 0.95, 8.70, 2.02, c="#b9b5ae", lw=1.6, tick=0.02, down=True)

    for x, label in [(1.35, "input"), (3.02, "encoder"), (4.66, "latent"),
                     (6.42, "decoder"), (8.25, "output")]:
        ax.text(x, 1.52, label, fontsize=34, color=INK, family=SANS, ha="center")
    ax.text(0.80, 1.00, "five glyphs, five calls, matplotlib only", fontsize=36,
            fontweight="bold", color=accent, family=SANS, va="center")


out = card(
    out=str(pathlib.Path(__file__).parent / "social-preview.png"),
    accent="#1f6feb", badge="S",
    kicker="PYTHON PACKAGE  ·  pip install sciglyph",
    headline="Publication figures as code",
    evidence="no BioRender, no Illustrator, and it checks itself",
    chart=chart,
    footer="github.com/GuoCheng24/sciglyph",
    headline_size=46,
)
print(f"written {pathlib.Path(out).name}")
