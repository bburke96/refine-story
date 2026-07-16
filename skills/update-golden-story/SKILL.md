---
name: update-golden-story
description: Set or refresh the Golden Story (the relative-estimation anchor) for refine-story. Takes a project tracker ref, retrieves the ticket, and copies its full content into .refine-story.json under sizing.goldenStory. Use when the user wants to set, change, refresh, or re-anchor the Golden Story / sizing baseline.
tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# Update the Golden Story

Point the team's relative-estimation anchor at a tracker ticket and cache its full content in config,
so the `refine-story` skill sizes against a stable saved snapshot instead of re-fetching the anchor
every run.

Clean Agile calls this the **Golden Story**: a real, completed story everyone agrees is a solid
"medium" worth **3 points**. Teams re-anchor it as their sense of "medium" drifts — that's what this
skill is for.

The config shape is owned by `config.schema.json`; `sizing.goldenStory` holds `{ ref, title, points,
summary, body }`. This skill writes that block. Read `references/config.md` for resolution rules.

## Input

The user provides a tracker ref for the story to anchor on:

- `#42` (or a bare integer) → GitHub issue
- `PROJ-42` → Jira issue key
- `ENG-42` → Linear issue identifier (same shape as a Jira key — use `config.tracker` to disambiguate)

If they don't give one, ask for it. If they describe a story with no ticket, fall back to collecting
`title` / `summary` / `points` / `body` by hand (paste), but prefer a real ticket.

## Steps

1. **Locate config.** Find `.refine-story.json` from the current project (walk up from the cwd to the
   git root, per `references/config.md`). If none exists, tell the user to run `refine-story-setup`
   first, or offer to create a minimal file containing just the `sizing.goldenStory` block.

2. **Determine the tracker.** Use `config.tracker` if set. If the ref format contradicts it (e.g. a
   `PROJ-42` key when `tracker` is `github`), confirm with the user. If no tracker is configured,
   ask which one the ref belongs to.

3. **Retrieve the ticket** via the matching adapter:
   - GitHub → `references/github.md` (read via GitHub MCP or `gh issue view … --json title,body`)
   - Jira → `references/jira.md` (get issue by key; read summary + description)
   - Linear → `references/linear.md` (get issue by identifier; read title + description)

   Pull the **title** and the **full body** (description + acceptance tests). Do not summarize away
   detail — the body is the point.

4. **Assemble `sizing.goldenStory`:**
   - `ref` — the input ref.
   - `title` — from the ticket.
   - `body` — the full retrieved content (the saved snapshot sizing compares against).
   - `summary` — a 1–3 sentence implementation-neutral description; derive it from the body and
     confirm with the user.
   - `points` — default `3`; confirm, since the Golden Story is the 3-point anchor by definition.
     If the user insists on a non-3 anchor, keep their value but note that 3 is the convention.

5. **Write it back.** Merge `sizing.goldenStory` into the existing `.refine-story.json`, preserving
   every other key (tracker config, other sizing fields). Do not touch anything outside
   `sizing.goldenStory`.

6. **Validate & show.** Confirm the file still parses and conforms to `config.schema.json` (use
   `ajv-cli` or Python `jsonschema` if available, else a parse + required-field check). Show the user
   the updated `sizing.goldenStory` block.

7. **Remind** them to commit `.refine-story.json` so the team shares the new anchor.

## Notes

- This skill only ever writes `sizing.goldenStory`. It never edits tracker tickets or other config.
- If retrieval fails (no tracker access, ticket not found), report it and offer the manual-paste path
  rather than saving a partial or guessed anchor.
