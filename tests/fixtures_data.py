"""Fixture stories and `.refine-story.json` configs used by the tests.

The Golden Story is both the sizing anchor and the *style exemplar*: Step 6 renders the
refined story to mirror its structure, acceptance-criteria form, tone, and length. So the
headline tests run the SAME story against two very differently-written anchors and check
that the output style follows the anchor.

Configs deliberately omit `tracker` so the skill has nothing to persist to during a test
(a belt-and-braces complement to the read-only tool allowlist).
"""

# A Clean-Agile-style anchor: a user-story sentence + numbered Given/When/Then criteria.
GOLDEN_GHERKIN = {
    "title": "Password reset via email link",
    "points": 3,
    "summary": (
        "A signed-out user requests a reset, receives an email link, and sets a new "
        "password. Touches the sign-in UI, an API endpoint, email delivery, and the user store."
    ),
    "body": (
        "As a signed-out user, I want to reset my password via an emailed link, so that I "
        "can regain access without contacting support.\n\n"
        "Acceptance Tests:\n"
        "1. Given I'm on the sign-in screen When I request a reset for my registered email "
        "Then I'm told a reset link has been sent.\n"
        "2. Given I open a valid, unexpired reset link When I submit a new password Then my "
        "password is changed and I can sign in with it.\n"
        "3. Given I open an expired or already-used reset link When the page loads Then I'm "
        "told the link is no longer valid and offered a new one."
    ),
}

# A Linear-style anchor: concise action title, one-line description, checklist criteria,
# no user-story ritual and no Gherkin.
GOLDEN_LINEAR = {
    "title": "Rate-limit the public API",
    "points": 3,
    "summary": "Per-key rate limiting on the public API so one client can't exhaust capacity.",
    "body": (
        "Add per-key rate limiting to the public API so a single client can't exhaust "
        "capacity for everyone else.\n\n"
        "Acceptance criteria\n"
        "- [ ] Requests over a key's limit get a 429 with a Retry-After header\n"
        "- [ ] Requests under the limit are unaffected\n"
        "- [ ] The limit is configurable per key"
    ),
}

CONFIG_GHERKIN = {"sizing": {"goldenStory": GOLDEN_GHERKIN}}
CONFIG_LINEAR = {"sizing": {"goldenStory": GOLDEN_LINEAR}}

# One small, single-iteration story, refined against both anchors so the only variable is
# the Golden Story's style.
STORY = (
    "On the account settings page, add a copy-to-clipboard button next to each API key so "
    "users can copy a key without selecting the text by hand."
)
