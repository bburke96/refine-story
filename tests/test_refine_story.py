"""Headless execution of the refine-story skill, verifying output-style mirroring.

The same story is refined against two differently-written Golden Stories; each test asserts
the output adopts that anchor's style. Marked `llm`: slow and consumes tokens. Deselect with
`-m "not llm"`; they skip automatically if `claude` isn't on PATH.

Assertions are structural, not exact-match (model output isn't deterministic).
"""

import re

import pytest

import fixtures_data as fx
from _util import has_point_value, rendered_body, requires_claude, run_refine

pytestmark = [pytest.mark.llm, requires_claude]

# "As a ... I want ... so that ..." — the user-story ritual we must NOT force on lean anchors.
USER_STORY_RE = re.compile(r"as a\b.*\bi want\b.*\bso that\b", re.I | re.S)


def _has_gherkin(text: str) -> bool:
    return bool(re.search(r"\bgiven\b", text, re.I) and re.search(r"\bthen\b", text, re.I))


def test_mirrors_a_gherkin_style_golden_story():
    out = run_refine(fx.STORY, fx.CONFIG_GHERKIN)
    body = rendered_body(out)

    # The anchor uses a user-story sentence + Given/When/Then, so the body should too.
    assert USER_STORY_RE.search(body), body
    assert _has_gherkin(body), body

    # Sizing (Step 4) always produces a point value somewhere in the run. (Whether it
    # lands in the body or a separate field is style/tracker-dependent, so check the
    # whole output, not the mirrored body.)
    assert has_point_value(out), out


def test_mirrors_a_concise_linear_style_golden_story():
    out = run_refine(fx.STORY, fx.CONFIG_LINEAR)
    body = rendered_body(out)

    # The anchor is a concise checklist with no ritual, so the body should match:
    # checkbox-style acceptance criteria...
    assert re.search(r"^\s*[-*]\s*\[ \]", body, re.M), body
    # ...and NOT the user-story sentence or Given/When/Then it never asked for.
    assert not USER_STORY_RE.search(body), body
    assert not _has_gherkin(body), body

    # Sizing still happens even though this lean anchor's body carries no estimate.
    assert has_point_value(out), out
