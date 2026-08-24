"""The point of drawing a CONSORT flow in code is that the numbers move, so the
arithmetic is what gets tested hardest: a flow that does not reconcile must be
refused, and one that does must not be.

Reviewers check this addition. Failing here is cheaper than failing there.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pytest

from sciglyph import consort


GOOD = [("Assessed", 1000), ("Enrolled", 700), ("Analysed", 690)]
GOOD_EXC = [[("Ineligible", 210), ("Declined", 90)],
            [("Lost to follow-up", 10)]]


class TestArithmetic:
    def test_a_flow_that_adds_up_has_no_problems(self):
        assert consort.check(GOOD, GOOD_EXC) == []

    def test_missing_patients_are_caught(self):
        """1000 - 300 excluded is 700, so declaring 650 leaves 50 unexplained."""
        bad = [("Assessed", 1000), ("Enrolled", 650)]
        probs = consort.check(bad, [[("Ineligible", 210), ("Declined", 90)]])
        assert len(probs) == 1
        step, entering, leaving, total, short = probs[0]
        assert (step, entering, leaving, total, short) == (0, 1000, 650, 300, 50)

    def test_over_counting_is_caught_too(self):
        """More leaving than entering is just as wrong, and the sign says so."""
        bad = [("Assessed", 100), ("Enrolled", 120)]
        probs = consort.check(bad, [None])
        assert probs[0][-1] == -20

    def test_every_bad_step_is_reported_not_just_the_first(self):
        bad = [("A", 100), ("B", 80), ("C", 50)]
        probs = consort.check(bad, [None, None])
        assert [p[0] for p in probs] == [0, 1]

    def test_no_exclusions_means_the_counts_must_match(self):
        assert consort.check([("A", 50), ("B", 50)], None) == []
        assert consort.check([("A", 50), ("B", 49)], None) != []

    def test_a_bare_integer_is_accepted_as_an_unlabelled_total(self):
        assert consort.check([("A", 100), ("B", 60)], [40]) == []


class TestRefusal:
    def test_drawing_is_refused_when_it_does_not_reconcile(self):
        with pytest.raises(consort.ConsortError) as e:
            consort.figure([("Assessed", 1000), ("Enrolled", 650)],
                           [[("Ineligible", 210)]])
        msg = str(e.value)
        assert "does not reconcile" in msg
        assert "Assessed" in msg and "Enrolled" in msg      # names the step
        # 1000 entering, 210 excluded, 650 declared -> 140 unaccounted for
        assert "140" in msg                                 # names the shortfall

    def test_strict_false_draws_anyway_and_still_reports(self):
        """An escape hatch that stays honest: it hands back the problems."""
        fig, problems = consort.figure(
            [("Assessed", 1000), ("Enrolled", 650)], [[("Ineligible", 210)]],
            strict=False)
        assert len(problems) == 1
        plt.close(fig)

    def test_a_good_flow_is_never_refused(self):
        fig, problems = consort.figure(GOOD, GOOD_EXC)
        assert problems == []
        plt.close(fig)


class TestShape:
    def test_excluded_length_must_match_the_number_of_gaps(self):
        with pytest.raises(ValueError, match="one entry per gap"):
            consort.check(GOOD, [[("Ineligible", 300)]])       # 2 gaps, 1 given

    def test_a_single_stage_is_not_a_flow(self):
        with pytest.raises(ValueError, match="at least two stages"):
            consort.check([("Assessed", 10)])

    def test_the_canvas_grows_with_the_content(self):
        """Two stages and eight stages must not land on the same canvas; that is
        what produced either cramped boxes or a band of dead space."""
        short = consort.natural_height([("A", 10), ("B", 10)], None)
        long = consort.natural_height([("A%d" % i, 10) for i in range(8)],
                                      [[("r", 0)] * 3] * 7)
        assert long > short

    def test_it_draws_on_a_supplied_axis_too(self):
        fig = plt.figure(figsize=(6, 6))
        ax = fig.add_axes([0, 0, 1, 1]); ax.set_xlim(0, 1); ax.set_ylim(0, 1)
        assert consort.diagram(ax, GOOD, GOOD_EXC) == []
        assert ax.patches, "nothing was drawn"
        plt.close(fig)
