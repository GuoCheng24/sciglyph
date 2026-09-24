"""A CONSORT flow diagram, with the counts reconciled before anything is drawn.

Run it and you get gallery/consort.png. Change any number so the flow stops
adding up and it refuses to draw, naming the step and the shortfall.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from sciglyph import consort, set_canvas, RC

plt.rcParams.update(RC)

SPINE = [
    ("Assessed for eligibility", 1240),
    ("Enrolled", 915),
    ("Allocated to the intervention arm", 458),
    ("Included in the primary analysis", 441),
]

EXCLUDED = [
    [("Did not meet inclusion criteria", 202),
     ("Declined to participate", 78),
     ("Other reasons", 45)],
    [("Allocated to the comparator arm", 457)],
    [("Lost to follow-up", 11),
     ("Withdrew consent", 6)],
]

fig, problems = consort.figure(SPINE, EXCLUDED)   # canvas sized from the content
assert not problems                               # strict=True would have raised

fig.savefig("gallery/consort.png", bbox_inches="tight", facecolor="white")
print("saved gallery/consort.png")

# What it does when the numbers stop adding up — the reason to draw this in
# code rather than in PowerPoint, where a stale count is silent.
broken = [("Assessed for eligibility", 1240), ("Enrolled", 900)]
try:
    consort.figure(broken, [[("Did not meet inclusion criteria", 202),
                            ("Declined to participate", 78)]])
except consort.ConsortError as e:
    print("\nrefused to draw:\n%s" % e)
