"""Shared canvas state: aspect-ratio compensation for round primitives.

In a [0,1] x [0,1] coordinate system a "circle" of radius r is physically
r*W wide and r*H tall, where W and H are the figure size in inches. On any
non-square canvas circles therefore render as ellipses -- measured on a 6x2
canvas, human heads and cells came out badly flattened.

Every round primitive in sciglyph divides its horizontal extent by this ratio,
so you get visually round shapes on any canvas. Call `set_canvas(fig)` once,
right after creating the figure.
"""

from matplotlib.patches import Ellipse

__all__ = ["set_canvas", "aspect", "circle"]

_STATE = {"ar": 1.0}


def set_canvas(fig):
    """Register the figure aspect ratio. **Required on any non-square canvas.**

    Returns the ratio (width / height), mostly so you can assert on it.
    """
    w, h = fig.get_size_inches()
    _STATE["ar"] = float(w) / float(h)
    return _STATE["ar"]


def aspect():
    """Current width/height ratio (1.0 until `set_canvas` is called)."""
    return _STATE["ar"]


def circle(ax, xy, r, **kw):
    """A visually round circle, corrected for the canvas aspect ratio."""
    return ax.add_patch(Ellipse(xy, width=2 * r / _STATE["ar"], height=2 * r, **kw))
