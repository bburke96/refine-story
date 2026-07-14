# Story Refinement — Clean Agile Methodology

A tool-neutral playbook for refining a story using the principles from Robert C. Martin's
*Clean Agile* (2019). Its output is a refined story with acceptance tests, a relative sizing
estimate, and any recommended splits.

This file is the **single source of truth** for the methodology. It contains no references to any
particular agent, tool, tracker, cloud provider, or codebase. A Claude Code skill, a Cursor rule,
a custom prompt, or a human can follow it directly. Anything project-specific (which tracker, the
reference story, field identifiers) comes from **configuration** — see `references/config.md`.

**This workflow is interactive.** After writing each section of the refined story, pause and ask
the user to review it before continuing to the next section. Do not write the entire output at once.

---

## Input

The user will provide one of:

- A tracker ticket identifier (e.g. `#12` for GitHub, `PROJ-45` for Jira)
- A raw story idea in free-form text
- A story already written but needing review

If a ticket identifier is given, read it from the configured tracker before proceeding.

---

## Refinement Workflow

### Step 1 — Understand the story

Parse the raw input. Extract:

- **Who** is the user or beneficiary?
- **What** do they want to do?
- **Why** does it matter (business value)?

If the story is missing any of these, infer from context where possible. Flag gaps explicitly.

**Pause here.** Present the title and user story sentence (As a / I want to / So that), then ask
the user to confirm or correct before continuing.

### Step 2 — Apply the INVEST criteria

Evaluate and improve the story against each criterion:

| Criterion | Question to ask |
|-----------|----------------|
| **Independent** | Can this story be built and shipped without depending on another unfinished story? If not, reorder or split. |
| **Negotiable** | Is it written as a constraint ("must use a message queue") rather than a need ("process work asynchronously")? Rewrite to preserve optionality. |
| **Valuable** | Does completing this story deliver something a user or operator would notice? If it's purely internal, combine with a user-facing story or reframe. |
| **Estimable** | Does the team have enough information to size it? If not, recommend a Spike. |
| **Small** | Can it be done in one iteration (≤ 1 week for a small team)? If not, split it (see Step 5). |
| **Testable** | Can you write a concrete acceptance test for it right now? If not, the story is too vague. |

### Step 3 — Write acceptance tests

Write 3–6 acceptance tests in **Given / When / Then** format. These are the definition of done —
not implementation tasks.

Rules (from Clean Agile):

- **Acceptance tests describe a change in the external behavior of the system from the user's
  perspective.** If a test cannot be verified by watching what happens on screen or in a response
  to the user, it is not an acceptance test.
- Each test must be verifiable by a non-developer (QA, PM, stakeholder) without reading the code.
- Tests describe behavior, not implementation — no mentions of database schema, background jobs,
  caching, retries, idempotency, or other internal concerns.
- Tests are the story's contract — if they all pass, the story is done.
- Include at least one unhappy-path / error case that the user would observe.

If internal implementation concerns arise (e.g. idempotency, retry logic, schema design), capture
them separately under **Implementation Notes** — not in the acceptance tests.

**Pause here.** Present the acceptance tests and implementation notes, then ask the user to review
before continuing.

### Step 4 — Size the story using relative pointing

Story points are **relative**, not absolute. Do not estimate in hours or days. Size the story by
comparing it to the **Reference Story** — the team's established anchor for a "medium" story worth
**3 points**.

#### The Reference Story (relative-estimation anchor)

The reference story comes from configuration (`sizing.referenceStory` — see `references/config.md`).
It is a real, completed story from *this* team that everyone agrees is a solid "medium," worth
**3 points** by consensus: it touches multiple parts of the system, has clear acceptance tests, and
is fully deliverable in one iteration.

If no reference story is configured, **ask the user to name one** before sizing — a good anchor is
essential to relative estimation. Offer to save it to the config for future runs.

*The reference story should be revisited as the team completes work and its sense of "medium" drifts.*

#### Fibonacci scale

| Points | Meaning | Relative to the Reference Story |
|--------|---------|--------------------------------|
| **1** | Tiny — a single well-understood change | Much smaller; only one part touched, no unknowns |
| **2** | Small — a few moving parts, low uncertainty | Smaller; fewer parts or less complexity than the anchor |
| **3** | Medium — the Reference Story benchmark | Roughly equivalent scope and uncertainty |
| **5** | Large — significantly more complexity or unknowns | Noticeably bigger; more parts, more risk, or harder to test |
| **8** | Very large — must be split before it can be worked | Much bigger; completing this in one iteration is unlikely |
| **Spike** | Can't estimate — too much unknown | Time-box exploration (1–2 days) then re-estimate |

**Any story estimated at the split threshold (8 by default) must be split.** Do not let it into a sprint.

#### How to compare to the Reference Story

Think through the implementation steps for both the target story and the reference story, then ask:

1. How many parts of the system does this touch compared to the reference story? (e.g. UI,
   API/service, data store, external integrations, infrastructure)
2. How many distinct moving parts or integration points does it have?
3. How much of the implementation is unknown or requires discovery?
4. How confident are you that the acceptance tests are complete and correct?

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

### Step 6 — Persist to the tracker

After presenting the refined story output, ask the user: **"Should I create/update this in the tracker?"**

If yes (or if the user already confirmed upfront), hand off to the tracker adapter for the tracker
named in `config.tracker`:

- GitHub → `references/github.md`
- Jira / Atlassian → `references/jira.md`

The adapter is responsible for writing the ticket body/type/milestone (or Jira equivalents) and,
where the tracker supports it, setting the workflow **Status to "Ready"** and recording the
**point estimate** from Step 4 using the field identifiers in configuration.

---

## Output Format

```
## Refined Story

**Title:** [concise, action-oriented title]

**As a** [user type],
**I want to** [action],
**So that** [benefit].

---

### Acceptance Tests

1. **Given** [precondition] **When** [action] **Then** [expected outcome]
2. **Given** [precondition] **When** [action] **Then** [expected outcome]
3. ...

### Implementation Notes

> Internal concerns the developer must solve that are not user-observable. Not acceptance
> criteria — no test will verify these directly.

- [e.g. writes must be idempotent in case the operation is retried]
- [e.g. data model TBD — may extend an existing table or introduce a new one]

---

### Estimate

**Comparison to the Reference Story** ("[reference title]", [reference points] pts):
- Parts touched: [list parts for this story] vs. [parts for the reference story]
- Moving parts: [count/description] vs. the reference story's [count]
- Unknowns: [low / medium / high] vs. the reference story's [low/medium/high]
- Test confidence: [high / medium / low]

**Estimate: [1 / 2 / 3 / 5 / 8 / Spike]** — [one sentence rationale anchored to the reference comparison]

> If it reaches the split threshold: this story must be split before it enters a sprint
> (see Recommended Splits below).

---

### Recommended Splits (if applicable)

- **[Story A title]** — [what it covers] (estimated X pts)
- **[Story B title]** — [what it covers] (estimated X pts)
```

---

## Clean Agile Principles to Apply

- **Stories are placeholders for a conversation**, not specs. The acceptance tests are the spec.
- **Velocity is a planning tool**, not a performance metric. Don't inflate estimates to look productive.
- **Small stories reduce risk.** A story that takes more than a week is a liability — it delays
  feedback. A story at the split threshold must be split before it enters a sprint.
- **Points are relative, not absolute.** Always anchor estimates to the Reference Story, not to
  hours or days. The scale is Fibonacci (1, 2, 3, 5, 8).
- **Spikes are not optional.** If you can't estimate it, spiking is the right move, not guessing.
- **Acceptance tests are the definition of done.** Not "code merged", not "deployed" — tests passing.
- **Stories should deliver value independently.** If a story only has value when combined with three
  others, it's a task, not a story. Combine or reframe.
