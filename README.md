# refine-story

Refine a story idea or tracker ticket into a well-formed backlog item using the principles from
Robert C. Martin's *Clean Agile* — **INVEST** review, **acceptance criteria**, **relative**
story-point sizing against a Golden Story, and Clean Agile **split** patterns for stories that are too
big. The output isn't forced into a fixed shape: it's **written in the style of your Golden Story**,
so concise Linear-style tickets and fuller Given/When/Then ones are equally at home. Then, optionally,
write the result to your issue tracker.

It works with **GitHub Issues**, **Jira/Atlassian**, or **Linear**, is **infrastructure- and
implementation-agnostic**, and hardcodes **nothing** about any one project — everything specific
comes from a small per-project config file.

## What it produces

An interactive, review-at-each-step refinement that yields:

- A tightened **title and description**, in your Golden Story's voice (a concise action title, or an
  `As a / I want to / So that` sentence — whatever the anchor uses)
- **Acceptance criteria** — a checklist, Given/When/Then, or prose (matching the anchor), verifiable
  by a non-developer, only as many as the story needs
- A **relative estimate** (Fibonacci: 1, 2, 3, 5, 8, or Spike) anchored to your team's Golden Story
- **Recommended splits** when a story is too large to fit one iteration
- Optionally, a created/updated ticket with **Status → Ready** and the **point estimate** recorded

## Architecture: one methodology, many adapters

```
skills/
├── refine-story/
│   ├── SKILL.md            # Claude Code adapter (entry point)
│   ├── methodology.md      # ★ tool-neutral Clean Agile playbook — the single source of truth
│   └── references/
│       ├── config.md       # config schema, resolution, interactive fallback
│       ├── github.md       # GitHub Issues + Projects adapter
│       ├── jira.md         # Jira / Atlassian adapter
│       └── linear.md       # Linear adapter
├── refine-story-setup/
│   └── SKILL.md            # interview-style setup — writes a project's .refine-story.json
└── update-golden-story/
    └── SKILL.md            # set/refresh the sizing anchor from a tracker ticket

tests/                      # pytest suite — schema guards + headless skill execution
```

The methodology is deliberately separated from any tool or model. `methodology.md` names no agent,
tracker, cloud, or codebase — so it is reusable well beyond Claude Code (see below).

## Install

### Claude Code (plugin)

Add this repo as a plugin marketplace, then install the `refine-story` plugin:

```
/plugin marketplace add bburke96/refine-story
/plugin install refine-story
```

Or, for a single project, copy `skills/refine-story/` into that project's `.claude/skills/`.

Invoke it by asking Claude to *"refine this story"*, *"groom `#123`"*, or *"help me write acceptance
tests for …"*.

### Any other agent or tool (model-agnostic)

Point your agent (Cursor rule, custom prompt, an MCP prompt, or a teammate) at
`skills/refine-story/methodology.md` and a `.refine-story.json`. The methodology is plain Markdown
with no tool bindings; supply your own tracker integration for Step 7 (persist), or run Steps 1–6
and paste the rendered body into your tracker by hand.

## Configure

**Guided (recommended):** run the setup skill — *"set up refine-story for this project"* — and it
will interview you for the tracker and Golden Story, auto-discover what it can (GitHub owner/repo
from your git remote, Project field ids via the `gh` CLI, Jira cloud/field ids via the Atlassian
MCP), then write and validate `.refine-story.json` in your project root.

**Manual:** copy `.refine-story.example.json` to `.refine-story.json` at your project root and edit
it. The `refine-story` skill also fills gaps on the fly — when a needed value is missing it asks and
offers to save it back, so you can even start from an empty file. Schema: `config.schema.json`.

| Key | Purpose |
|-----|---------|
| `tracker` | `"github"`, `"jira"`, or `"linear"` — which adapter the persist step uses. |
| `sizing.goldenStory` | **The Golden Story** — a real completed story your team agrees is a solid medium (3 points), with a **dual role**: the estimation anchor *and* the style exemplar the output is written to match. Its `body` (full story copied from the tracker) is the saved snapshot used for both. Required before sizing. See [The Golden Story](#the-golden-story-why-it-matters). |
| `sizing.scale` / `sizing.splitThreshold` | Optional. Fibonacci scale (default `[1,2,3,5,8]`) and the point value at/above which a story must be split (default `8`). |
| `github.owner` / `github.repo` | Target repository. |
| `github.defaultMilestone` | Optional milestone attached on create. |
| `github.project` | Optional GitHub Projects (v2) field ids for automating Status + Estimate. Omit to skip. |
| `jira.projectKey` | Target Jira project. |
| `jira.cloudId` / `jira.siteUrl` | Atlassian site; `cloudId` is resolved from `siteUrl` if omitted. |
| `jira.issueTypeForFeature` / `issueTypeForTask` | Issue types for user-facing vs. tooling stories. |
| `jira.storyPointsFieldId` | Story Points custom field id (commonly `customfield_10016`). |
| `jira.readyStatusName` | Status to transition to when refinement is done. |
| `linear.teamKey` | Team the stories live in (e.g. `ENG`). |
| `linear.projectName` | Optional Linear project to attach issues to. |
| `linear.featureLabel` / `linear.taskLabel` | Optional labels for user-facing vs. tooling stories. |
| `linear.readyStateName` | Workflow state to move the issue to when refinement is done. |

### GitHub setup

Requires the GitHub MCP server or the `gh` CLI authenticated for your repo. To populate
`github.project`, discover the ids once with `gh project field-list` / `gh project view` — see
`skills/refine-story/references/github.md`.

### Jira / Atlassian setup

Requires an Atlassian MCP server (Atlassian's official Remote MCP, or `sooperset/mcp-atlassian`).
The adapter detects the available tools at runtime and maps them to read/create/update/transition
operations — see `skills/refine-story/references/jira.md`.

### Linear setup

Requires the Linear MCP server:

```
claude mcp add --transport http linear-server https://mcp.linear.app/mcp
```

The adapter detects the available Linear tools at runtime and maps them to read/create/update
operations, sets the native `estimate` field, and moves the issue to your `readyStateName` workflow
state — see `skills/refine-story/references/linear.md`. Estimation must be enabled on the team for
points to take effect.

## The Golden Story (why it matters)

Story points are **relative**, not hours. The skill sizes each story by comparing it to *your*
**Golden Story** (Clean Agile's term for the estimation anchor) rather than to an absolute scale,
which keeps estimates honest and team-specific. The Golden Story's full body is **cached in config**
(`sizing.goldenStory.body`), so it compares against a stable snapshot and never re-fetches the anchor
from the tracker.

The anchor has a **dual role**: it's also the **style exemplar**. Rather than impose a fixed template,
the skill writes each refined story to match the Golden Story — its structure, its acceptance-criteria
form (checklist / Given/When/Then / prose), its tone, and its length. Pick an anchor written the way
you want your tickets to read and every refinement follows suit; there's nothing else to configure.

Set it — and refresh it as your team's sense of "medium" (or house style) drifts — with the setup
skill or by asking *"update the Golden Story to `#123`"*, which retrieves that ticket and copies its
content into config.

## Tests

The suite in `tests/` has two layers, run with `pytest`:

- **Fast schema guards** (`test_fixtures_valid.py`) — validate the example config and every test
  fixture against `config.schema.json`. No API, instant.
- **Headless skill execution** (`test_refine_story.py`, marked `llm`) — actually run the skill via
  `claude -p --plugin-dir .` against a fixture story in a throwaway workspace, and verify **output
  style follows the Golden Story**: the same story refined against a Gherkin-style anchor comes out
  with a user-story sentence + Given/When/Then, while against a concise Linear-style anchor it comes
  out as a checklist with *neither* the user-story ritual nor Gherkin — and both still carry a point
  estimate. Assertions are structural (not exact-match), since model output isn't deterministic.
  Tests use read-only tools and tracker-less configs, so a run never writes to any tracker.

```bash
python -m venv .venv && . .venv/bin/activate
pip install -r requirements-dev.txt

pytest                 # everything (the llm tests invoke `claude`, so they're slow + cost tokens)
pytest -m "not llm"    # fast schema guards only
```

The `llm` tests need the `claude` CLI on your PATH and authenticated; they **skip** (not fail) when
it's absent. Override the model with `REFINE_STORY_TEST_MODEL` (default `sonnet`) and the per-run
timeout with `REFINE_STORY_TEST_TIMEOUT` seconds.

## Output style — matched to your Golden Story

There's no template to configure and no house style baked in. The refined story is written to **mirror
your Golden Story**, so the same story comes out differently for different teams — both valid:

**Golden Story written Clean-Agile style → a fuller, Gherkin output**

```
**Title:** Export dashboard as PDF

**As a** report viewer, **I want to** export a dashboard as a PDF, **so that** I can share it offline.

### Acceptance Criteria
1. **Given** a dashboard **When** I choose Export → PDF **Then** a PDF of the current view downloads.
2. **Given** the export fails **When** I retry **Then** I see an error and the page stays usable.
```

**Golden Story written Linear style → a concise checklist output**

```
**Export dashboard as PDF**

Add a PDF export to the reports page so a viewer can download the current dashboard.

**Acceptance criteria**
- [ ] Export → PDF downloads the current view
- [ ] A failed export shows an error and leaves the page usable
```

The methodology's *thinking* (INVEST, testable/observable behavior, relative sizing, splits) is the
same either way — only the rendered shape follows the anchor, and the skill writes **only as much as
the story needs**. Change the style for everything by pointing the Golden Story at a differently-written
ticket (*"update the Golden Story to `#123`"*).

## License

MIT — see [LICENSE](LICENSE).
