"""The layout checks are the part of sciglyph you are trusting when you ship a
figure, so they are the part that is tested: each test builds a figure with one
known defect and asserts the check finds it, plus the mirror case asserting it
does not fire on a clean figure."""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import pytest

from sciglyph import set_canvas, aspect
from sciglyph.layout import text_collisions, patch_collisions, missing_glyphs


def fig_ax(w=6.0, h=4.0):
    fig = plt.figure(figsize=(w, h), dpi=100)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.axis("off")
    set_canvas(fig)
    return fig, ax


class TestTextCollisions:
    def test_finds_overlapping_labels(self):
        fig, ax = fig_ax()
        ax.text(.50, .5, "CD4 Treg-FOXP3", fontsize=12)
        ax.text(.52, .5, "SMR", fontsize=12)          # deliberately on top
        hits, n = text_collisions(fig, ax)
        assert n == 2
        assert hits, "two labels drawn on the same spot must be reported"

    def test_silent_on_separated_labels(self):
        fig, ax = fig_ax()
        ax.text(.05, .9, "left", fontsize=8)
        ax.text(.85, .1, "right", fontsize=8)
        hits, n = text_collisions(fig, ax)
        assert n == 2 and not hits

    def test_threshold_is_honoured(self):
        fig, ax = fig_ax()
        ax.text(.50, .5, "AAAAAAAAAA", fontsize=12)
        ax.text(.56, .5, "BBBBBBBBBB", fontsize=12)
        loose, _ = text_collisions(fig, ax, thr=0.95)   # only near-total overlap
        strict, _ = text_collisions(fig, ax, thr=0.01)
        assert len(strict) >= len(loose)


class TestPatchCollisions:
    def test_finds_overlapping_boxes(self):
        fig, ax = fig_ax()
        ax.add_patch(Rectangle((.20, .40), .30, .20, fc="#ddd", ec="k"))
        ax.add_patch(Rectangle((.35, .45), .30, .20, fc="#ccc", ec="k"))
        assert patch_collisions(fig, ax), "half-overlapping boxes must be reported"

    def test_containment_is_not_a_collision(self):
        """A panel that contains its contents overlaps them completely. That is
        the normal case and must not be reported, or the check is unusable."""
        fig, ax = fig_ax()
        ax.add_patch(Rectangle((.10, .10), .80, .80, fc="none", ec="k"))
        ax.add_patch(Rectangle((.30, .30), .20, .20, fc="#ccc", ec="k"))
        assert not patch_collisions(fig, ax)

    def test_unfilled_dashed_annotation_is_ignored(self):
        """Dashed unfilled rings are drawn *around* things on purpose."""
        fig, ax = fig_ax()
        ax.add_patch(Rectangle((.30, .30), .20, .20, fc="#ccc", ec="k"))
        ax.add_patch(Rectangle((.25, .25), .30, .30, fc="none", ec="r", ls="--"))
        assert not patch_collisions(fig, ax)


class TestMissingGlyphs:
    def test_reports_a_character_the_font_cannot_draw(self):
        """U+E000 is private-use: no font defines it, so this holds whatever
        fonts the machine happens to have. Asserting on a symbol like the
        snowflake instead would pass or fail depending on the runner's fonts."""
        fig, ax = fig_ax()
        ax.text(.5, .5, "tofu \ue000")
        missing = missing_glyphs(fig)
        assert any("57344" in m for m in missing), missing

    def test_reports_the_real_world_case(self):
        """The case this check exists for: a snowflake typed as a literal, which
        DejaVu can draw and Liberation Sans cannot. Skipped where Liberation
        Sans is absent, since then there is nothing to detect."""
        from matplotlib.font_manager import findfont, FontProperties
        if "Liberation" not in findfont(FontProperties(family="Liberation Sans")):
            pytest.skip("Liberation Sans not installed on this machine")
        from sciglyph import RC
        plt.rcParams.update(RC)
        try:
            fig, ax = fig_ax()
            ax.text(.5, .5, "frozen \u2744")
            assert any("10052" in m for m in missing_glyphs(fig))
        finally:
            plt.rcParams.update(plt.rcParamsDefault)

    def test_plain_ascii_is_clean(self):
        fig, ax = fig_ax()
        ax.text(.5, .5, "frozen backbone")
        assert not missing_glyphs(fig)


class TestCanvas:
    @pytest.mark.parametrize("w,h,expected", [(6.0, 4.0, 1.5), (4.0, 4.0, 1.0), (12.0, 3.0, 4.0)])
    def test_aspect_tracks_the_figure(self, w, h, expected):
        fig, ax = fig_ax(w, h)
        assert abs(aspect() - expected) < 1e-9

    def test_circles_are_round_on_a_wide_canvas(self):
        """The reason set_canvas exists: r in [0,1] coords is r*W wide and r*H
        tall, so on a non-square figure an uncorrected circle is an ellipse."""
        from sciglyph._canvas import circle
        fig, ax = fig_ax(12.0, 3.0)
        c = circle(ax, (.5, .5), .05, fc="k")
        fig.canvas.draw()
        bb = c.get_window_extent()
        assert abs(bb.width / bb.height - 1.0) < 0.02
