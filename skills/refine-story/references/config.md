# Configuration — `.refine-story.json`

All project-specific values live in a `.refine-story.json` file at the root of the consuming
project. Nothing is hardcoded in the skill. This file explains how to resolve that config, what each
field means, and what to do when it is missing or incomplete.

The authoritative machine-readable structure is `config.schema.json` at the repo root; a filled-in
example is `.refine-story.example.json`. This file does not restate the shape — it points at those.

## Resolution order

1. Look for `.refine-story.json` in the current working directory, then walk up parent directories
   to the project/repo root. Use the first one found.
2. Parse it as JSON. If it fails to parse, tell the user and stop — do not guess.
3. For each value a given run needs, if it is present, use it. If it is **absent**, ask the user for
   it, then **offer to write it back** to `.refine-story.json` so future runs don't re-ask.
4. Never substitute a default that is tied to any particular project. The only safe built-in
   defaults are the generic sizing ones (`scale`, `splitThreshold`).

## Shape

The full structure — every field, its type, defaults, and which fields are required when — is
defined once in **`config.schema.json`** (the source of truth). A filled-in, copy-paste starter is
**`.refine-story.example.json`**. Read those for the literal shape rather than duplicating it here.

Top-level keys: `tracker`, `sizing` (with `scale`, `splitThreshold`, `goldenStory`), `github`,
and `jira`. The notes below cover only what the schema can't express — when each value matters and
how to source it.

## Field notes

- **`tracker`** — drives which adapter Step 6 uses. If the user only wants the refined-story text
  and no ticket write, `tracker` is not needed.
- **`sizing.goldenStory`** — the Golden Story (Clean Agile), the single most important config value.
  Relative estimation is meaningless without a shared anchor. Its **`body`** holds the full story
  content copied from the tracker; sizing compares against that saved snapshot, so the `refine-story`
  skill never re-fetches the anchor from the tracker. Populate it with the `refine-story-setup` or
  `update-golden-story` skill (both read the tracker via `ref`). When it's missing entirely, prompt:
  *"What's a completed story your team agrees is a solid medium — worth 3 points? I'll use it as the
  sizing anchor."*
- **`github.project`** — GitHub Projects field ids are stable per project; capture them once. See
  `references/github.md` for the discovery commands. Omit the block entirely if the project doesn't
  use Projects or you don't want field automation.
- **`jira.storyPointsFieldId`** — Story Points is a custom field; its id varies per Jira site
  (commonly `customfield_10016`). Confirm it via the Atlassian MCP if unknown.

## Writing config back

When you collect a missing value interactively, merge it into the existing `.refine-story.json`
(preserving other keys) and write the file. Show the user the diff/result. If no file exists yet,
create one containing only the keys gathered so far.
