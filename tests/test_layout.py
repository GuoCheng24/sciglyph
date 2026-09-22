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

    @staticmethod
    def _ends_overlapping(fig, ax, glyph_overlap=1.2):
        """Two long labels whose ends bury `glyph_overlap` characters.

        Positioned by measuring the first label rather than by a hard-coded
        coordinate, so the case is the same one on any machine's default font.
        """
        left = "measured on the full set, thinking off"
        right = "and again on a rerun of the same batch"
        a = ax.text(0.5, 3.0, left, fontsize=18)
        fig.canvas.draw()
        box = a.get_window_extent(fig.canvas.get_renderer())
        per_char = box.width / len(left)
        ax.text((box.x1 - glyph_overlap * per_char) / 100.0, 3.0, right, fontsize=18)
        return left, right

    def test_long_labels_touching_at_their_ends_are_reported(self):
        """The case the area test alone was blind to.

        Two long strings colliding at their ends bury real characters while
        scoring near zero on intersection-over-smaller-area, because the
        denominator is a whole string. The measured case that prompted this:
        16.5 px of overlap, one and a half characters buried, 6.5% by area,
        reported as clean.
        """
        fig, ax = fig_ax(12.8, 6.4)
        ax.set_xlim(0, 12.8); ax.set_ylim(0, 6.4)
        self._ends_overlapping(fig, ax)
        hits, _ = text_collisions(fig, ax)
        assert hits, "an overlap that buries a character must be reported"
        assert hits[0][2] < 0.10, (
            "this pair is below the area threshold - it is the glyph test that "
            "has to catch it, and the test is worthless if the area test fires too")

    def test_glyph_test_can_be_switched_off(self):
        fig, ax = fig_ax(12.8, 6.4)
        ax.set_xlim(0, 12.8); ax.set_ylim(0, 6.4)
        self._ends_overlapping(fig, ax)
        hits, _ = text_collisions(fig, ax, glyphs=float("inf"))
        assert not hits, "glyphs=inf must fall back to the area test alone"

    def test_a_hair_of_overlap_is_not_a_collision(self):
        """Boxes that graze each other by a fraction of a character are fine."""
        fig, ax = fig_ax(12.8, 6.4)
        ax.set_xlim(0, 12.8); ax.set_ylim(0, 6.4)
        self._ends_overlapping(fig, ax, glyph_overlap=0.2)
        hits, _ = text_collisions(fig, ax)
        assert not hits, "a graze of a fifth of a character must not be reported"

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
