"""Mention the repo once or twice, to people who are actually using this.

Deliberately quiet: never on the first run, never when stderr is not a
terminal (so piped and redirected output stays clean), never in CI, and
never more than twice in the lifetime of an install. `SCIGLYPH_NO_NUDGE=1`
turns it off for good.
"""
import os
import sys
import json
from pathlib import Path

REPO = "GuoCheng24/sciglyph"
_SHOW_AT = (5, 25)          # run counts at which we say something
_ENV_OFF = "SCIGLYPH_NO_NUDGE"


def _state_path():
    base = os.environ.get("XDG_STATE_HOME") or (Path.home() / ".local" / "state")
    return Path(base) / "sciglyph" / "usage.json"


def _quiet():
    if os.environ.get(_ENV_OFF):
        return True
    if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS"):
        return True
    # Not a terminal means someone is piping or redirecting us; stay out of it.
    return not (hasattr(sys.stderr, "isatty") and sys.stderr.isatty())


def record_run():
    """Count this run and, at two points, print a single line to stderr.

    Any failure here is swallowed: a nudge must never break the tool or
    change its exit status.
    """
    if _quiet():
        return
    try:
        p = _state_path()
        try:
            data = json.loads(p.read_text())
        except Exception:
            data = {}
        n = int(data.get("runs", 0)) + 1
        data["runs"] = n
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(data))
        if n in _SHOW_AT:
            print(
                "\n── sciglyph has been useful " + str(n) + " times. If it saved you time,\n"
                "   a star helps other people find it: https://github.com/" + REPO + "\n"
                "   (silence this with SCIGLYPH_NO_NUDGE=1)",
                file=sys.stderr,
            )
    except Exception:
        pass
