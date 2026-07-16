# refine-story

Refine a story idea or tracker ticket into a well-formed backlog item using the principles from
Robert C. Martin's *Clean Agile* — **INVEST** review, **Given/When/Then** acceptance tests,
**relative** story-point sizing against a Golden Story, and Clean Agile **split** patterns for
stories that are too big. Then, optionally, write the result to your issue tracker.

It works with **GitHub Issues** or **Jira/Atlassian**, is **infrastructure- and
implementation-agnostic**, and hardcodes **nothing** about any one project — everything specific
comes from a small per-project config file.

## What it produces

An interactive, review-at-each-step refinement that yields:

- A tightened **title** and `As a / I want to / So that` user story
- 3–6 **acceptance tests** in Given/When/Then, verifiable by a non-developer, plus separate
  **implementation notes** for internal concerns
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
│       └── jira.md         # Jira / Atlassian adapter
├── refine-story-setup/
│   └── SKILL.md            # interview-style setup — writes a project's .refine-story.json
└── update-golden-story/
    └── SKILL.md            # set/refresh the sizing anchor from a tracker ticket
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
with no tool bindings; supply your own tracker integration for Step 6, or run Steps 1–5 and paste
the output into your tracker by hand.

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
| `tracker` | `"github"` or `"jira"` — which adapter Step 6 uses. |
| `sizing.goldenStory` | **The Golden Story** — the estimation anchor. A real completed story your team agrees is a solid medium (3 points). Its `body` is the full story copied from the tracker; sizing compares against that saved snapshot. Required before sizing. |
| `sizing.scale` / `sizing.splitThreshold` | Optional. Fibonacci scale (default `[1,2,3,5,8]`) and the point value at/above which a story must be split (default `8`). |
| `github.owner` / `github.repo` | Target repository. |
| `github.defaultMilestone` | Optional milestone attached on create. |
| `github.project` | Optional GitHub Projects (v2) field ids for automating Status + Estimate. Omit to skip. |
| `jira.projectKey` | Target Jira project. |
| `jira.cloudId` / `jira.siteUrl` | Atlassian site; `cloudId` is resolved from `siteUrl` if omitted. |
| `jira.issueTypeForFeature` / `issueTypeForTask` | Issue types for user-facing vs. tooling stories. |
| `jira.storyPointsFieldId` | Story Points custom field id (commonly `customfield_10016`). |
| `jira.readyStatusName` | Status to transition to when refinement is done. |

### GitHub setup

Requires the GitHub MCP server or the `gh` CLI authenticated for your repo. To populate
`github.project`, discover the ids once with `gh project field-list` / `gh project view` — see
`skills/refine-story/references/github.md`.

### Jira / Atlassian setup

Requires an Atlassian MCP server (Atlassian's official Remote MCP, or `sooperset/mcp-atlassian`).
The adapter detects the available tools at runtime and maps them to read/create/update/transition
operations — see `skills/refine-story/references/jira.md`.

## The Golden Story (why it matters)

Story points are **relative**, not hours. The skill sizes each story by comparing it to *your*
**Golden Story** (Clean Agile's term for the estimation anchor) rather than to an absolute scale,
which keeps estimates honest and team-specific. The Golden Story's full body is **cached in config**
(`sizing.goldenStory.body`), so sizing compares against a stable snapshot and never re-fetches the
anchor from the tracker.

Set it — and refresh it as your team's sense of "medium" drifts — with the setup skill or by asking
*"update the Golden Story to `#123`"*, which retrieves that ticket and copies its content into config.

## License

MIT — see [LICENSE](LICENSE).
