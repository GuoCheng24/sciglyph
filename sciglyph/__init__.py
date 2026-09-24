"""sciglyph - publication-quality scientific illustration in pure matplotlib.

Two glyph families plus a layout checker:

* :mod:`sciglyph.bio`    biological / omics glyphs for Nature-style overview figures
* :mod:`sciglyph.arch`   neural-network architecture glyphs (TPAMI / CVPR style)
* :mod:`sciglyph.layout` pre-flight text-collision detection

Quick start::

    import matplotlib.pyplot as plt
    from sciglyph import bio, set_canvas, RC, report

    plt.rcParams.update(RC)
    fig = plt.figure(figsize=(7.2, 4.0), dpi=300)
    ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    set_canvas(fig)                      # required on non-square canvases

    bio.dna(ax, .2, .5, w=.05, h=.4, n=2)
    bio.cell(ax, .4, .5, r=.05, seed=1)

    report(fig, ax)                      # check for text collisions
    fig.savefig("figure.pdf", bbox_inches="tight")
"""

from ._canvas import set_canvas, aspect
from . import bio
from . import arch
from . import consort

RC = bio.RC

__version__ = "0.2.1"
__all__ = ["bio", "arch", "consort", "layout", "set_canvas", "aspect",
           "text_collisions", "report", "RC", "__version__"]


def __getattr__(name):
    # layout is imported on first use rather than here. Imported eagerly, it was
    # already in sys.modules when `python -m sciglyph.layout` ran it again as
    # __main__, and every run of the README's own command opened with a
    # RuntimeWarning about unpredictable behaviour.
    if name in ("layout", "text_collisions", "report"):
        # import_module, not `from . import layout`: the from-import asks this
        # very function for "layout" and recurses without end.
        import importlib
        _layout = importlib.import_module(".layout", __name__)
        return _layout if name == "layout" else getattr(_layout, name)
    raise AttributeError(f"module 'sciglyph' has no attribute {name!r}")
