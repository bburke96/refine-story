# Configuration — `.refine-story.json`

All project-specific values live in a `.refine-story.json` file at the root of the consuming
project. Nothing is hardcoded in the skill. This file documents the schema, how to resolve it, and
what to do when it is missing or incomplete.

The authoritative machine-readable schema is `config.schema.json` at the repo root; a filled-in
example is `.refine-story.example.json`.

## Resolution order

1. Look for `.refine-story.json` in the current working directory, then walk up parent directories
   to the project/repo root. Use the first one found.
2. Parse it as JSON. If it fails to parse, tell the user and stop — do not guess.
3. For each value a given run needs, if it is present, use it. If it is **absent**, ask the user for
   it, then **offer to write it back** to `.refine-story.json` so future runs don't re-ask.
4. Never substitute a default that is tied to any particular project. The only safe built-in
   defaults are the generic sizing ones (`scale`, `splitThreshold`).

## Schema

```jsonc
{
  // Which tracker Step 6 writes to. Required if the user wants to persist the story.
  "tracker": "github",                     // "github" | "jira"

  "sizing": {
    "scale": [1, 2, 3, 5, 8],              // optional; Fibonacci points, defaults shown
    "splitThreshold": 8,                   // optional; stories at/above this must be split

    // The relative-estimation anchor. REQUIRED before Step 4 sizing.
    // If absent, ask the user to name a real "medium / 3-point" story, then offer to save it.
    "referenceStory": {
      "ref": "#5",                         // tracker id of the anchor story (optional but nice)
      "title": "A representative medium story",
      "points": 3,
      "summary": "1–3 implementation-neutral sentences describing the anchor story."
    }
  },

  // Present when tracker === "github".
  "github": {
    "owner": "your-org-or-user",
    "repo": "your-repo",
    "defaultMilestone": "Backlog",         // optional; milestone title to attach on create

    // Optional. GitHub Projects (v2) field ids for Status + Estimate. Omit the whole block to
    // skip Project-field updates. Look these up once with the gh CLI (see references/github.md).
    "project": {
      "number": 3,
      "nodeId": "PVT_xxxxxxxx",
      "statusFieldId": "PVTSSF_xxxxxxxx",
      "readyOptionId": "xxxxxxxx",         // option id of the "Ready" Status value
      "estimateFieldId": "PVTF_xxxxxxxx"   // number field for story points
    }
  },

  // Present when tracker === "jira".
  "jira": {
    "cloudId": "your-atlassian-cloud-id",  // or "siteUrl": "https://your.atlassian.net"
    "projectKey": "PROJ",
    "issueTypeForFeature": "Story",        // issue type for user-facing stories
    "issueTypeForTask": "Task",            // issue type for infra/tooling stories
    "storyPointsFieldId": "customfield_10016", // the Story Points custom field id
    "readyStatusName": "Ready"             // status to transition to when refinement is done
  }
}
```

## Field notes

- **`tracker`** — drives which adapter Step 6 uses. If the user only wants the refined-story text
  and no ticket write, `tracker` is not needed.
- **`sizing.referenceStory`** — the single most important config value. Relative estimation is
  meaningless without a shared anchor. When missing, prompt: *"What's a completed story your team
  agrees is a solid medium — worth 3 points? I'll use it as the sizing anchor."*
- **`github.project`** — GitHub Projects field ids are stable per project; capture them once. See
  `references/github.md` for the discovery commands. Omit the block entirely if the project doesn't
  use Projects or you don't want field automation.
- **`jira.storyPointsFieldId`** — Story Points is a custom field; its id varies per Jira site
  (commonly `customfield_10016`). Confirm it via the Atlassian MCP if unknown.

## Writing config back

When you collect a missing value interactively, merge it into the existing `.refine-story.json`
(preserving other keys) and write the file. Show the user the diff/result. If no file exists yet,
create one containing only the keys gathered so far.
