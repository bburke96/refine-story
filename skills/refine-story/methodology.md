# Story Refinement — Clean Agile Methodology

A tool-neutral playbook for refining a story using the principles from Robert C. Martin's
*Clean Agile* (2019). Its output is a refined story with acceptance criteria, a relative sizing
estimate, and any recommended splits — written in the **style of the team's Golden Story**, not a
fixed format.

This file is the **single source of truth** for the methodology. It contains no references to any
particular agent, tool, tracker, cloud provider, or codebase. A Claude Code skill, a Cursor rule,
a custom prompt, or a human can follow it directly. Anything project-specific (which tracker, the
Golden Story, field identifiers) comes from **configuration** — see `references/config.md`.

**This workflow is interactive.** After writing each section of the refined story, pause and ask
the user to review it before continuing to the next section. Do not write the entire output at once.

---

## Input

The user will provide one of:

- A tracker ticket identifier (e.g. `#12` for GitHub, `PROJ-45` for Jira, `ENG-45` for Linear)
- A raw story idea in free-form text
- A story already written but needing review

If a ticket identifier is given, read it from the configured tracker before proceeding.

---

## Refinement Workflow

### Step 1 — Understand the story

Parse the raw input. Extract, for your own reasoning:

- **Who** is the user or beneficiary?
- **What** do they want to do?
- **Why** does it matter (business value)?

If the story is missing any of these, infer from context where possible. Flag gaps explicitly.

How you *write this up* is not fixed — **match the Golden Story's style** (see Step 6). Often that's a
concise, action-oriented title and a short description that directly states the work. Use an
`As a / I want to / So that` sentence only if that is how the Golden Story is written. Write only as
much as the story needs.

**Pause here.** Present the title and description, then ask the user to confirm or correct before
continuing.

### Step 2 — Apply the INVEST criteria

Evaluate and improve the story against each criterion:

| Criterion | Question to ask |
|-----------|----------------|
| **Independent** | Can this story be built and shipped without depending on another unfinished story? If not, reorder or split. |
| **Negotiable** | Does the story leave room for dev and business to negotiate scope against cost? Details are deliberately left out so the team can trade an expensive ask for a cheaper one that delivers the same value. |
| **Valuable** | Does completing this story deliver something a user or operator would notice? If it's purely internal, combine with a user-facing story or reframe. |
| **Estimable** | Does the team have enough information to size it? If not, recommend a Spike. |
| **Small** | Can it be done in one iteration (≤ 1 week for a small team)? If not, split it (see Step 5). |
| **Testable** | Can you write a concrete acceptance criterion for it right now? If not, the story is too vague. |

### Step 3 — Write acceptance criteria

Acceptance criteria are the definition of done — not implementation tasks. **Write them in the form
the Golden Story uses**: a checklist of outcomes, `Given / When / Then` scenarios, or short prose.
Don't impose Given/When/Then if the anchor doesn't use it.

Whatever the form, the Clean Agile principles still hold:

- **Describe user-observable behavior**, not implementation. If a criterion can't be checked by
  watching what happens on screen or in a response to the user, it isn't one — no database schema,
  background jobs, caching, retries, or idempotency here.
- Each must be verifiable by a non-developer (QA, PM, stakeholder) without reading the code.
- They are the story's contract — if they all hold, the story is done.
- Cover at least one edge / unhappy case the user would notice.
- **Write only as many as the story needs** — don't pad to hit a count.

If internal implementation concerns arise (e.g. idempotency, retry logic, schema design) *and* the
Golden Story tends to record them, capture them separately (e.g. under **Implementation Notes**) —
never mixed into the acceptance criteria. If the anchor keeps things lean, leave them out.

**Pause here.** Present the acceptance criteria (and any implementation notes), then ask the user to
review before continuing.

### Step 4 — Size the story using relative pointing

Story points are **relative**, not absolute. Do not estimate in hours or days. Size the story by
comparing it to the **Golden Story** — the team's established anchor for a "medium" story worth
**3 points**.

#### The Golden Story (Clean Agile)

The Golden Story comes from configuration (`sizing.goldenStory` — see `references/config.md`). It is
a real, completed story from *this* team that everyone agrees is a solid "medium," worth **3 points**
by consensus: it touches multiple parts of the system, has clear acceptance criteria, and is fully
deliverable in one iteration. It has a **dual role** — the sizing anchor here, and the **style
exemplar** the refined story is written to match in Step 6.

**Always compare against the saved copy in config, not the live tracker.** `sizing.goldenStory.body`
holds the full story content (description + acceptance criteria) copied into config precisely so
sizing is fast and stable — do **not** re-fetch the anchor from the tracker during refinement. Read
`sizing.goldenStory` (its `body`, `summary`, `title`, `points`) and reason against that snapshot. The
same saved `body` is the exemplar Step 6 mirrors for structure, format, and voice.

If no Golden Story is configured, **ask the user to name one** before sizing — a good anchor is
essential to relative estimation. Offer to save it via the `refine-story-setup` or
`update-golden-story` skill (they copy the full body from the tracker) so future runs have the
snapshot ready.

*The Golden Story should be revisited as the team completes work and its sense of "medium" drifts —
refresh the saved copy with the `update-golden-story` skill.*

#### Fibonacci scale

| Points | Meaning | Relative to the Golden Story |
|--------|---------|------------------------------|
| **1** | Tiny — a single well-understood change | Much smaller; only one part touched, no unknowns |
| **2** | Small — a few moving parts, low uncertainty | Smaller; fewer parts or less complexity than the anchor |
| **3** | Medium — the Golden Story benchmark | Roughly equivalent scope and uncertainty |
| **5** | Large — significantly more complexity or unknowns | Noticeably bigger; more parts, more risk, or harder to test |
| **8** | Very large — must be split before it can be worked | Much bigger; completing this in one iteration is unlikely |
| **Spike** | Can't estimate — too much unknown | Time-box exploration (1–2 days) then re-estimate |

**Any story estimated at the split threshold (8 by default) must be split.** Do not let it into a sprint.

#### How to compare to the Golden Story

Think through the implementation steps for both the target story and the Golden Story (using the
saved `sizing.goldenStory.body`), then ask:

1. How many parts of the system does this touch compared to the Golden Story? (e.g. UI,
   API/service, data store, external integrations, infrastructure)
2. How many distinct moving parts or integration points does it have?
3. How much of the implementation is unknown or requires discovery?
4. How confident are you that the acceptance criteria are complete and correct?

If the target story touches fewer parts, has fewer unknowns, and is easier to test → it's smaller
(1 or 2). If it's roughly equivalent → 3. If it's broader, riskier, or harder to test → 5 or 8
(split if it reaches the threshold).

**Pause here.** Present the estimate block, then ask the user to confirm before continuing.

### Step 5 — Split large stories (if needed)

Common Clean Agile split patterns:

- **By workflow step** — split a multi-step flow into one story per step
- **By user role** — split if different users need different behavior
- **By happy/unhappy path** — ship the happy path first, unhappy paths as follow-on
- **By platform** — e.g., one platform first, the next second
- **Spike + implementation** — create a Spike story to de-risk, then an implementation story

Each split story must itself pass INVEST.

**Pause here.** If splits are recommended, present them and ask the user to confirm the breakdown
before proceeding to Step 6.

### Step 6 — Render the ticket body

Write the Markdown that becomes the tracker issue body by **mirroring the Golden Story**. There is no
template to configure — the anchor *is* the template.

Read `sizing.goldenStory.body` and match:

- its **structure and sections** (headings, or none) — don't add sections it doesn't have;
- its **acceptance-criteria form** (checklist / `Given-When-Then` / prose);
- its **tone and length** — if the anchor is terse, be terse; write only as much as is needed.

If the anchor includes a kind of content the methodology didn't itself produce (e.g. a test plan, a
rollout note, links), **infer it** from the refined story so the shape stays consistent. If the
anchor is lean and omits such things, omit them too.

The goal is a ticket that looks like it belongs next to the Golden Story in the same backlog — same
voice, same shape, same level of detail.

**Pause here.** Present the rendered body — noting anything you inferred — and ask the user to review
it before it is written to the tracker.

### Step 7 — Persist to the tracker

After presenting the rendered body, ask the user: **"Should I create/update this in the tracker?"**

If yes (or if the user already confirmed upfront), hand off to the tracker adapter for the tracker
named in `config.tracker`:

- GitHub → `references/github.md`
- Jira / Atlassian → `references/jira.md`
- Linear → `references/linear.md`

The adapter writes the **rendered body from Step 6** as the ticket body (choosing type/milestone or
Jira/Linear equivalents by whether the story is user-facing or tooling) and, where the tracker
supports it, sets the workflow **Status to "Ready"** and records the **point estimate** from Step 4
using the field identifiers in configuration.

---

## Output

The refined story has up to four parts — **title + description**, **acceptance criteria**,
**estimate**, and **recommended splits** (only when needed). Their wording, headings, and level of
detail are **not fixed**: mirror the Golden Story (Step 6). The same story can be written two very
different — both valid — ways depending on the anchor:

*Golden Story written Clean-Agile style → a fuller, Gherkin output:*

```
**Title:** Export dashboard as PDF

**As a** report viewer, **I want to** export a dashboard as a PDF, **so that** I can share it offline.

### Acceptance Criteria
1. **Given** a dashboard **When** I choose Export → PDF **Then** a PDF of the current view downloads.
2. **Given** the export fails **When** I retry **Then** I see an error and the page stays usable.

### Estimate
Compared to "Password reset via email link" (3 pts): similar parts, low unknowns → **3**.
```

*Golden Story written Linear style → a concise checklist output:*

```
**Export dashboard as PDF**

Add a PDF export to the reports page so a viewer can download the current dashboard.

**Acceptance criteria**
- [ ] Export → PDF downloads the current view
- [ ] A failed export shows an error and leaves the page usable

**Estimate:** 3 — similar scope to "Password reset via email link" (3 pts), few unknowns.
```

Whatever the shape, the **estimate** always carries two things: the comparison to the Golden Story
and a point value.

**Estimate: [1 / 2 / 3 / 5 / 8 / Spike]** — one-sentence rationale anchored to the Golden Story. If it
reaches the split threshold, the story must be split before it enters a sprint, and the splits are
listed in the anchor's style.

---

## Clean Agile Principles to Apply

- **Stories are placeholders for a conversation**, not specs. The acceptance criteria are the spec.
- **Velocity is a planning tool**, not a performance metric. Don't inflate estimates to look productive.
- **Small stories reduce risk.** A story that takes more than a week is a liability — it delays
  feedback. A story at the split threshold must be split before it enters a sprint.
- **Points are relative, not absolute.** Always anchor estimates to the Golden Story, not to
  hours or days. The scale is Fibonacci (1, 2, 3, 5, 8).
- **Spikes are not optional.** If you can't estimate it, spiking is the right move, not guessing.
- **Acceptance criteria are the definition of done** — in whatever form your team writes them
  (checklist, Given/When/Then, prose). Not "code merged", not "deployed" — the criteria hold.
- **Write only as much as the story needs.** Match the Golden Story; don't impose a heavier format
  (user-story sentences, Gherkin) than the anchor uses. Concise, direct issues are good issues.
- **Stories should deliver value independently.** If a story only has value when combined with three
  others, it's a task, not a story. Combine or reframe.
