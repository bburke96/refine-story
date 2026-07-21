"""Shared helpers for the refine-story test suite.

The LLM tests execute the real `refine-story` skill headlessly: they spin up a
throwaway workspace containing a fixture `.refine-story.json`, load this repo as a
plugin (`claude -p --plugin-dir <repo>`), and drive one non-interactive refinement.
Assertions are structural (section presence, no un-substituted tokens), never exact
string matches, because model output is not deterministic.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = REPO_ROOT / "config.schema.json"

CLAUDE = shutil.which("claude")
MODEL = os.environ.get("REFINE_STORY_TEST_MODEL", "sonnet")
TIMEOUT = int(os.environ.get("REFINE_STORY_TEST_TIMEOUT", "300"))

# Skip the LLM tests (rather than fail) when the CLI isn't available, so the suite
# is still green for contributors without the `claude` CLI on their PATH.
requires_claude = pytest.mark.skipif(
    CLAUDE is None,
    reason="`claude` CLI not on PATH; skipping headless skill-execution tests",
)

# Read-only tools only. The skill needs to read files and invoke itself; it must
# never write to a tracker or shell out during a test, so Bash/Write/Edit/MCP are
# intentionally excluded (unlisted tools are auto-denied in non-interactive mode).
ALLOWED_TOOLS = ["Read", "Glob", "Grep", "Skill", "TodoWrite"]

BODY_MARKER = "RENDERED TICKET BODY:"

PROMPT = f"""\
You are running an automated, non-interactive test of the "refine-story" skill.
Use the refine-story skill to refine the story below.

Test conditions (important):
- This is fully automated. There is NO human to review, so do NOT pause between
  steps and do NOT ask questions. Make reasonable assumptions and proceed through
  every step of the methodology to the end.
- Produce the COMPLETE result in a single response: the refined title and
  description, the acceptance criteria, and the estimate WITH a numeric
  story-point value. Follow the methodology's format guidance — the written shape
  (user-story sentence or not, checklist vs. Given/When/Then, verbosity) must
  mirror the Golden Story in the configured .refine-story.json, not a fixed format.
- Then render the final ticket body for Step 6 and print it verbatim after a line
  containing exactly:
{BODY_MARKER}
- Do NOT create, update, or write to any tracker or external system. Output only.

Story to refine:
{{story}}
"""


def run_refine(story: str, config: dict) -> str:
    """Execute the skill headlessly against `story` with `config` and return stdout."""
    if CLAUDE is None:  # guarded by requires_claude, but be defensive
        pytest.skip("`claude` CLI not on PATH")

    with tempfile.TemporaryDirectory() as d:
        workspace = Path(d)
        (workspace / ".refine-story.json").write_text(json.dumps(config, indent=2))

        cmd = [
            CLAUDE,
            "-p",
            PROMPT.format(story=story),
            "--plugin-dir",
            str(REPO_ROOT),
            "--add-dir",
            str(REPO_ROOT),
            "--model",
            MODEL,
            "--output-format",
            "text",
            "--allowedTools",
            *ALLOWED_TOOLS,
        ]

        try:
            proc = subprocess.run(
                cmd,
                cwd=workspace,
                capture_output=True,
                text=True,
                timeout=TIMEOUT,
            )
        except subprocess.TimeoutExpired as exc:
            pytest.fail(f"`claude` timed out after {TIMEOUT}s\n{exc.stdout or ''}")

        if proc.returncode != 0:
            pytest.fail(
                f"`claude` exited {proc.returncode}\n"
                f"--- stderr ---\n{proc.stderr}\n--- stdout ---\n{proc.stdout}"
            )
        return proc.stdout


def rendered_body(output: str) -> str:
    """Return the rendered ticket body (everything after the last body marker)."""
    idx = output.rfind(BODY_MARKER)
    return output[idx + len(BODY_MARKER):] if idx != -1 else output


def section(body: str, heading: str) -> str:
    """Return the text under a Markdown `heading` up to the next heading of any level."""
    lines = body.splitlines()
    out: list[str] = []
    capturing = False
    for line in lines:
        if re.match(r"^#{1,6}\s", line):
            if capturing:
                break
            if line.strip().lstrip("#").strip().lower() == heading.lower():
                capturing = True
            continue
        if capturing:
            out.append(line)
    return "\n".join(out).strip()


def has_point_value(text: str) -> bool:
    """True if the text mentions a Fibonacci point value or a Spike."""
    return bool(re.search(r"\b(1|2|3|5|8)\b\s*(point|pt|pts)?", text, re.I)) or "spike" in text.lower()
