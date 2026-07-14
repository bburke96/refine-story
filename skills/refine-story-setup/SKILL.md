---
name: refine-story-setup
description: Interactive setup for the refine-story plugin. Interviews the user for tracker and sizing details, auto-discovers what it can, and writes a validated .refine-story.json into the current project. Use when the user wants to install, set up, configure, initialize, or onboard refine-story for a project.
tools: Read, Write, Edit, Glob, Grep, Bash, AskUserQuestion
---

# refine-story — Project Setup

Guide the user through creating a `.refine-story.json` for the project they're working in, so the
`refine-story` skill has everything it needs. This is an **interview**: ask for one group of values
at a time, auto-discover anything you can, confirm, then write the file and validate it.

The config shape is owned by `config.schema.json` (repo root); per-field meaning lives in
`references/config.md`. Read both before starting so you prompt for exactly the right fields and can
validate the result. Do not invent fields that aren't in the schema.

Keep it conversational and skippable — every optional block can be declined. Never fabricate an id
(GitHub Project ids, Jira cloud/field ids); if you can't discover or the user doesn't have it, leave
that block out rather than guessing.

## Before you start

1. **Confirm the target project.** The config belongs at the root of the project the user is working
   in — *not* in the refine-story plugin repo. Determine the project root: prefer the top of the
   current git repo (`git rev-parse --show-toplevel`), else the current working directory. State
   where you'll write `.refine-story.json` and confirm.
2. **Check for an existing config.** If `.refine-story.json` already exists there, read it and offer
   to **edit/complete** it rather than overwrite. Preserve keys the user doesn't change.

## The interview

Ask in this order. Use a multiple-choice prompt for the tracker and yes/no branches; use free-text
for names, keys, and the reference story.

### 1. Tracker

Ask which tracker Step 6 should write to:

- **GitHub Issues** → gather the `github` block (§2a)
- **Jira / Atlassian** → gather the `jira` block (§2b)
- **None (refined text only)** → skip the tracker block entirely; `tracker` is omitted

### 2a. GitHub

- **owner / repo** — try to infer first: `git remote get-url origin` and parse
  `github.com[:/]<owner>/<repo>(.git)`. Present the inferred values and let the user confirm or override.
- **defaultMilestone** (optional) — offer to list existing milestones so they can pick one:
  `gh api repos/<owner>/<repo>/milestones --jq '.[].title'`. Skippable.
- **GitHub Projects automation?** (optional) — ask if they want Status→Ready + Estimate written to a
  Project (v2). If yes, discover the ids rather than asking the user to hunt for them:
  ```bash
  gh project list --owner <owner> --format json          # find the project number
  gh project view <number> --owner <owner> --format json # -> project nodeId (PVT_…)
  gh project field-list <number> --owner <owner> --format json  # -> Status field + "Ready" option, Estimate field
  ```
  From the field list, pull the Status field id, the option id whose name is "Ready" (or ask which
  status means ready), and the number/estimate field id. Populate `github.project`. If they decline
  or the project isn't found, omit the whole `github.project` block.

Requires the GitHub MCP server or an authenticated `gh` CLI. If neither is available, still collect
owner/repo by hand and note that field automation can't be auto-discovered.

### 2b. Jira / Atlassian

- **site** — ask for the site URL (`https://<org>.atlassian.net`). If an Atlassian MCP server is
  available, resolve the `cloudId` from it (e.g. the "accessible resources" tool) and store that;
  otherwise store `siteUrl` and let the skill resolve it later.
- **projectKey** — e.g. `PROJ`.
- **issue types** — `issueTypeForFeature` (default `Story`) and `issueTypeForTask` (default `Task`).
  Offer the defaults; only ask if they want to change them.
- **storyPointsFieldId** — this varies per site (commonly `customfield_10016`). If an Atlassian MCP
  is available, try to discover it from the project's field metadata; otherwise ask, and tell them
  how to find it (project settings → fields). Skippable if they don't track points in Jira.
- **readyStatusName** — the status to transition to when refinement is done (default `Ready`).

### 3. Sizing (all trackers)

- **referenceStory** — the most important value. Explain: *"Estimates are relative, so I anchor every
  story to one your team agrees is a solid medium — 3 points. What's a real, completed story like
  that?"* Collect `title`, a 1–3 sentence implementation-neutral `summary`, `points` (default 3),
  and optionally its tracker `ref`. Don't skip this — without it, sizing has no anchor.
- **scale / splitThreshold** (optional) — mention the defaults (`[1,2,3,5,8]`, split at `8`) and only
  capture overrides if the team uses a different scale.

## Write & validate

1. Assemble the object from the answers, including only the blocks the user provided. Add
   `"$schema": "<relative or absolute path to config.schema.json>"` at the top so their editor gets
   autocomplete (use a URL if the plugin is installed outside the project).
2. Write `.refine-story.json` to the project root. If completing an existing file, merge — don't drop
   keys the user kept.
3. **Validate** against `config.schema.json` before declaring success. If `ajv-cli` or Python's
   `jsonschema` is available, run it; otherwise at minimum confirm the JSON parses and every
   tracker-required field for the chosen `tracker` is present. Report any gap and offer to fix it.
4. Show the user the final file.

## Finish

- Remind them to **commit `.refine-story.json`** to their repo so the whole team shares the tracker
  target and the reference story. (It's project data, not plugin data — the plugin itself is
  installed once, globally.)
- Tell them how to use it: just ask to *"refine this story"*, *"groom `<ticket-id>`"*, or *"write
  acceptance tests for …"* — the `refine-story` skill will pick up this config automatically.
- If the `refine-story` skill isn't installed/available, point them at the plugin's README for the
  install step (marketplace add, or copy `skills/refine-story/` into `.claude/skills/`).
