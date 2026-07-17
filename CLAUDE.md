# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with
code in this repository.

## What this repo is

This is a **Claude Code plugin** (`refine-story`), distributed as its own plugin
marketplace. It contains no application code, build system, tests, or
dependencies — it is entirely Markdown skills plus a JSON config contract.
"Working in this repo" means editing skill instructions, the methodology,
adapter references, and the config schema — not compiling or running anything.
There is nothing to build, lint, or test; verification is reading the prose for
consistency.

The plugin refines a story idea or tracker ticket into a well-formed backlog
item using Robert C. Martin's _Clean Agile_ principles (INVEST review,
Given/When/Then acceptance tests, relative story-point sizing against a Golden
Story, and split patterns), then optionally writes the result to GitHub Issues,
Jira/Atlassian, or Linear.

## Architecture: one methodology, many adapters

The central design principle is a **strict separation between the tool-neutral
methodology and every tool binding**. Preserve this separation in any edit.

- `skills/refine-story/methodology.md` — **the single source of truth.** A
  tool-neutral Clean Agile playbook (Steps 1–6) that names no agent, tracker,
  cloud, or codebase. It must stay reusable by any agent, not just Claude Code.
  Do not add Claude-specific, tracker-specific, or project-specific detail here.
- `skills/refine-story/SKILL.md` — a **thin Claude Code adapter** and the entry
  point. It loads config, delegates the actual refinement to `methodology.md`
  (Steps 1–5), then hands off to a tracker adapter for Step 6. It hardcodes
  nothing about any project.
- `skills/refine-story/references/{github,jira,linear}.md` — per-tracker
  adapters for Step 6. Each detects the available MCP/CLI tools at runtime and
  maps them to read/create/update/transition operations, using field ids
  supplied by config.
- `skills/refine-story/references/config.md` — how to resolve
  `.refine-story.json` and what each field means (prose only; the shape lives in
  the schema, see below).
- `skills/refine-story-setup/SKILL.md` — interview-style setup that
  auto-discovers what it can and writes a validated `.refine-story.json` **into
  the consuming project**, not into this repo.
- `skills/update-golden-story/SKILL.md` — sets/refreshes the sizing anchor by
  retrieving a ticket and caching its full body into config.

## Two configuration invariants (do not violate)

These two rules recur across every skill and are the most important things to
get right:

1. **Nothing project-specific is hardcoded in a skill.** Everything specific to
   a consuming project — tracker choice, owner/repo, field ids, Golden Story —
   comes from a `.refine-story.json` at the root of _that_ project (never this
   repo). The only safe built-in defaults are the generic sizing ones (`scale`,
   `splitThreshold`). When a needed value is missing, skills prompt for it and
   offer to write it back.

2. **The config shape is owned by `config.schema.json`** (repo root), with
   `.refine-story.example.json` as the filled-in example. Prose files
   (`config.md`, the SKILLs) deliberately do **not** restate the field shape —
   they point at the schema. When you change the config structure, edit
   `config.schema.json` **and** `.refine-story.example.json`, then confirm the
   prose still matches; never let a skill invent a field that isn't in the
   schema.

## The Golden Story

Sizing is **relative**, not hours-based. Stories are estimated by comparison to
the team's **Golden Story** — a real completed story agreed to be a solid medium
(3 points). Its full body is **cached in config** (`sizing.goldenStory.body`);
the `refine-story` skill sizes against that saved snapshot and **must not
re-fetch the anchor from the tracker**. Only `refine-story-setup` and
`update-golden-story` read the tracker to (re)populate that snapshot.

## Conventions when editing skills

- Skills are Markdown with YAML frontmatter (`name`, `description`, and for the
  two write-capable skills, an explicit `tools:` allowlist). The `description`
  is what triggers the skill — keep it specific about when to invoke.
- The `refine-story` flow is **interactive**: it pauses for user review after
  each section (title/user-story, acceptance tests, estimate, splits) and must
  not emit the whole output at once. Preserve that pacing in any wording change.
- Config resolution walks up from the cwd to the git root and uses the first
  `.refine-story.json` found; on JSON parse failure, stop and tell the user
  rather than guessing.
- Keep author/owner references pointed at `bburke96/refine-story` (see
  `.claude-plugin/*.json` and README install instructions). Bump `version` in
  **both** `.claude-plugin/plugin.json` and `.claude-plugin/marketplace.json`
  together when releasing.
