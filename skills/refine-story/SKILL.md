---
name: refine-story
description: Refine a tracker ticket or story idea using Clean Agile principles (INVEST, acceptance criteria, relative sizing), written in the style of the team's Golden Story rather than a fixed format. Works with GitHub Issues, Jira/Atlassian, or Linear via a per-project config file. Use when the user asks to refine a story, groom a ticket, or wants help writing acceptance criteria.
---

# Story Refinement — Clean Agile

Refine a story using the principles from Robert C. Martin's *Clean Agile* (2019), producing a
refined story with acceptance criteria, a relative sizing estimate, and any recommended splits —
written in the **style of the team's Golden Story**, not a fixed format — then optionally write it to
the project's issue tracker (GitHub, Jira/Atlassian, or Linear).

This SKILL is a thin Claude Code adapter. The methodology itself is project- and tool-agnostic and
lives in a separate file so it can be reused by other agents.

## How to run

1. **Load configuration.** Follow `references/config.md` to locate and read the project's
   `.refine-story.json`. If it is missing or incomplete, prompt the user for the values you need and
   offer to write them back. `config.tracker` selects the tracker; the Golden Story under
   `config.sizing.goldenStory` is required before sizing (Step 4). Size against the **saved**
   `goldenStory.body`, and write the output in that anchor's style — do not re-fetch the anchor from
   the tracker. If no Golden Story is configured, point the user at the `refine-story-setup` or
   `update-golden-story` skill.

2. **Execute the methodology.** Follow `methodology.md` exactly, Steps 1–6. It is **interactive** —
   pause for user review after each section (title/description, acceptance criteria, estimate,
   splits, rendered body). Do not emit the whole output at once. The output format is **not fixed**:
   **Step 6 renders the ticket body by mirroring the Golden Story** (structure, acceptance-criteria
   form, tone, length) — there is no template to configure.

3. **Persist to the tracker (Step 7).** When the user approves, hand off to the adapter for
   `config.tracker`:
   - `github` → `references/github.md`
   - `jira` → `references/jira.md`
   - `linear` → `references/linear.md`

   The adapter reads/writes the ticket and sets Status → Ready and the point estimate using the
   field identifiers from configuration. Nothing about any specific project is hardcoded in this
   skill — it all comes from `.refine-story.json`.

## Files in this skill

- `methodology.md` — the tool-neutral Clean Agile playbook (single source of truth).
- `references/config.md` — config schema, resolution order, and interactive fallback rules.
- `references/github.md` — GitHub Issues + Projects adapter.
- `references/jira.md` — Jira / Atlassian adapter.
- `references/linear.md` — Linear adapter.
