"""CONSORT / cohort flow diagrams, with the arithmetic checked.

Every trial and most cohort papers need one of these, and journals require it
for randomised trials. R has three packages for it; Python has had none, so the
standing advice was to draw the boxes and arrows yourself in matplotlib.

The reason to draw one in code rather than PowerPoint is that the numbers move.
You re-clean the data, forty patients drop out of the eligible set, and the
figure is stale — usually silently, because nobody re-adds the boxes by hand.

So this does the one thing a drawing tool can do that a drawing surface cannot:
**it checks that the numbers add up**. At every step the count entering minus
the exclusions must equal the count leaving. Where it does not, you are told
exactly which step and by how much, before the figure is drawn. Reviewers check
this arithmetic; it is better to fail here.
"""

from matplotlib.patches import FancyBboxPatch

__all__ = ["figure", "diagram", "check", "natural_height", "ConsortError"]

INK = "#1a1a1a"
MUTE = "#5a5a5a"
BOX_FC = "#f4f6f8"
BOX_EC = "#5f93bd"
EXC_FC = "#fbf4ee"
EXC_EC = "#c98a5a"
ARROW = "#4a4a4a"


class ConsortError(ValueError):
    """The counts in the flow do not reconcile."""


def _norm(spine, excluded):
    """Validate shapes and return (spine, excluded) in canonical form.

    `excluded` has one entry per gap between consecutive spine nodes, so it is
    always one shorter than `spine`. Passing None, or None for a single gap,
    means nothing was excluded there.
    """
    spine = [(str(label), int(n)) for label, n in spine]
    if len(spine) < 2:
        raise ValueError("a flow needs at least two stages")
    gaps = len(spine) - 1
    if excluded is None:
        excluded = [None] * gaps
    excluded = list(excluded)
    if len(excluded) != gaps:
        raise ValueError(
            "excluded must have one entry per gap between stages: "
            "%d stages leave %d gaps, got %d" % (len(spine), gaps, len(excluded))
        )
    out = []
    for e in excluded:
        if e is None:
            out.append([])
        elif isinstance(e, (int, float)):          # a bare total, unlabelled
            out.append([("Excluded", int(e))])
        else:
            out.append([(str(label), int(n)) for label, n in e])
    return spine, out


def check(spine, excluded=None):
    """Reconcile the counts. Returns a list of problems; empty means it adds up.

    Each problem is (step_index, entering, leaving, excluded_total, shortfall),
    where shortfall is what is unaccounted for: entering - excluded - leaving.
    A positive shortfall means patients vanished; negative means more left the
    step than entered it.
    """
    spine, excluded = _norm(spine, excluded)
    problems = []
    for i, exc in enumerate(excluded):
        entering = spine[i][1]
        leaving = spine[i + 1][1]
        total = sum(n for _, n in exc)
        shortfall = entering - total - leaving
        if shortfall != 0:
            problems.append((i, entering, leaving, total, shortfall))
    return problems


def _fmt_problems(spine, problems):
    lines = []
    for i, entering, leaving, total, short in problems:
        lines.append(
            "  step %d  %r (%d) -> %r (%d), excluded %d: %s %d"
            % (i + 1, spine[i][0], entering, spine[i + 1][0], leaving, total,
               "unaccounted for" if short > 0 else "over-counted by",
               abs(short))
        )
    return "\n".join(lines)


def diagram(ax, spine, excluded=None, *, strict=True, box_w=.44, exc_w=.42,
            fs=8.2, fs_exc=7.4, x_spine=.25, x_exc=.54, line=.034, pad=.020):
    """Draw the flow on `ax`, which should span [0,1] in both directions.

    spine     [(label, n), ...] top to bottom — the main path through the study
    excluded  one entry per gap: [(label, n), ...], a bare int, or None
    strict    raise ConsortError when the counts do not reconcile (default).
              Set False to draw anyway; the mismatch is still returned.
    line      vertical space one line of text occupies, before scaling
    pad       padding inside a box, above the first line and below the last

    Both boxes and gaps are sized from their contents rather than sharing the
    height evenly: a stage with a long label and a branch listing five reasons
    need different amounts of room, and splitting the axis n ways gives one of
    them far too much while the other overflows.

    Returns the list of problems from `check`, so a caller that passed
    strict=False can still report them.
    """
    spine, excluded = _norm(spine, excluded)
    problems = check(spine, excluded)
    if problems and strict:
        raise ConsortError(
            "the flow does not reconcile — %d step(s) do not add up:\n%s\n"
            "Fix the counts, or pass strict=False to draw it anyway."
            % (len(problems), _fmt_problems(spine, problems))
        )

    n = len(spine)
    # Spine labels wrap onto a second line only if they are long; the count is
    # always its own line. Two lines is the common case.
    spine_h = [2 * line + 2 * pad] * n
    # A branch needs a heading line plus one line per reason.
    gap_h = []
    for exc in excluded[:n - 1]:
        if exc:
            gap_h.append(max(.055, (1 + len(exc)) * line + 2 * pad))
        else:
            gap_h.append(.055)                    # bare arrow, still needs room

    # Scale the whole stack to fill the axis exactly. Proportions stay
    # content-driven; only the common factor changes. Leaving it unscaled
    # strands whitespace at the bottom that bbox_inches="tight" cannot reach,
    # because the gap is inside the axes rather than around them.
    total = sum(spine_h) + sum(gap_h)
    scale = 1.0 / total
    spine_h = [h * scale for h in spine_h]
    gap_h = [h * scale for h in gap_h]

    y = 1.0
    for i, (label, count) in enumerate(spine):
        h = spine_h[i]
        top, bot = y, y - h
        _box(ax, x_spine - box_w / 2, bot, box_w, h, BOX_FC, BOX_EC)
        ax.text(x_spine, bot + h / 2, "%s\n(n = %s)" % (label, f"{count:,}"),
                ha="center", va="center", fontsize=fs, color=INK, zorder=6,
                linespacing=1.5)
        y = bot
        if i == n - 1:
            break

        g = gap_h[i]
        y_next = y - g
        ax.annotate("", xy=(x_spine, y_next), xytext=(x_spine, y),
                    arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=1.1),
                    zorder=4)

        exc = excluded[i]
        if exc:
            # the branch fills the gap it was sized for, less a hair either side
            eh = g - .010
            ye = y_next + .005
            y_mid = ye + eh / 2
            _box(ax, x_exc, ye, exc_w, eh, EXC_FC, EXC_EC, lw=.9)
            ax.annotate("", xy=(x_exc, y_mid), xytext=(x_spine, y_mid),
                        arrowprops=dict(arrowstyle="-|>", color=ARROW, lw=.9),
                        zorder=4)
            ax.text(x_exc + .018, ye + eh - pad * scale * .8,
                    "Excluded (n = %s)" % f"{sum(c for _, c in exc):,}",
                    ha="left", va="top", fontsize=fs_exc, color=INK,
                    weight="bold", zorder=6)
            ax.text(x_exc + .028, ye + eh - pad * scale * .8 - line * scale,
                    "\n".join("%s (n = %s)" % (lab, f"{c:,}") for lab, c in exc),
                    ha="left", va="top", fontsize=fs_exc - .5, color=MUTE,
                    zorder=6, linespacing=1.55)
        y = y_next

    return problems


def natural_height(spine, excluded=None, width=7.4, row=.42):
    """Figure height, in inches, that gives this flow room without stretching.

    A four-stage flow with three short branches wants a different canvas from a
    two-stage one, and guessing wrong is what produces either cramped boxes or
    a band of dead space no `bbox_inches` can trim.
    """
    spine, excluded = _norm(spine, excluded)
    rows = 2 * len(spine)                                   # label + count each
    for exc in excluded[:len(spine) - 1]:
        rows += (1 + len(exc)) if exc else 1
    return max(3.0, round(rows * row, 2))


def figure(spine, excluded=None, *, width=7.4, strict=True, **kw):
    """Build a correctly proportioned figure and draw the flow on it.

    The one-call form, and the one to reach for: it sizes the canvas from the
    content so nothing is stretched or stranded.

        fig, problems = consort.figure(spine, excluded)
        fig.savefig("consort.pdf", bbox_inches="tight")
    """
    import matplotlib.pyplot as plt
    from ._canvas import set_canvas

    h = natural_height(spine, excluded, width=width)
    fig = plt.figure(figsize=(width, h), dpi=kw.pop("dpi", 200))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    set_canvas(fig)
    problems = diagram(ax, spine, excluded, strict=strict, **kw)
    return fig, problems


def _box(ax, x, y, w, h, fc, ec, lw=1.1, r=.010):
    ax.add_patch(FancyBboxPatch(
        (x, y), w, h, boxstyle="round,pad=0,rounding_size=%f" % r,
        fc=fc, ec=ec, lw=lw, zorder=5))
