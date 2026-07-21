# Tracker Adapter — Jira / Atlassian

Used when `config.tracker === "jira"`. Reads config from `config.jira` (see `references/config.md`).

Integration is via an **Atlassian MCP server**. Which tools exist depends on the server installed:

- **Atlassian's official Remote MCP** (`mcp.atlassian.com`) — camelCase tools, e.g.
  `getAccessibleAtlassianResources`, `getJiraIssue`, `createJiraIssue`, `editJiraIssue`,
  `getTransitionsForJiraIssue`, `transitionJiraIssue`, `searchJiraIssuesUsingJql`.
- **`sooperset/mcp-atlassian`** — snake_case tools, e.g. `jira_get_issue`, `jira_create_issue`,
  `jira_update_issue`, `jira_transition_issue`, `jira_search`.

**Do not assume tool names.** Inspect the available `mcp__*` tools at runtime and map them to the
operations below. If no Atlassian tool is available, tell the user Jira integration requires an
Atlassian MCP server and stop (still deliver the refined-story text).

## Resolving the site

Jira Cloud operations need a site/cloud identifier. Use `config.jira.cloudId` if present; otherwise
resolve it from `config.jira.siteUrl` via the server's "accessible resources" tool (e.g.
`getAccessibleAtlassianResources`) and offer to save the `cloudId` back to config.

## Input parsing

- `PROJ-45` (letters-dash-number) → a Jira issue key. Read it before refining.
- A bare `#12` or integer → treat as GitHub-style; if `tracker` is `jira`, confirm with the user
  (they may mean the Jira issue `PROJ-12`).

## Reading a ticket

Call the "get issue" tool (`getJiraIssue` / `jira_get_issue`) with the issue key and the resolved
cloud id. Extract summary, description, and current status.

## Creating a new issue

Call the "create issue" tool (`createJiraIssue` / `jira_create_issue`) with:

- `projectKey`: `config.jira.projectKey`
- `summary`: the refined story title
- `description`: the rendered ticket body from Step 6 (mirroring the Golden Story's style). Provide
  Markdown; the server converts to ADF as needed.
- `issueType`: `config.jira.issueTypeForFeature` for user-facing stories, `issueTypeForTask` for
  infrastructure/tooling stories.
- Story points: set `config.jira.storyPointsFieldId` to the Step 4 point value (pass it in the
  fields map, e.g. `{ "customfield_10016": 3 }`).

## Updating an existing issue (input was a Jira key)

Call the "edit/update issue" tool (`editJiraIssue` / `jira_update_issue`) to overwrite the
description with the refined content and set the story-points field. **Do not** change the assignee.

## Setting Status → Ready and Estimate

- **Estimate:** written as the `storyPointsFieldId` custom field during create/update (above).
- **Status:** Jira status changes go through **transitions**, not direct field writes.
  1. List transitions for the issue (`getTransitionsForJiraIssue` / `jira_transition_issue` list mode).
  2. Find the transition whose target status name equals `config.jira.readyStatusName`.
  3. Execute that transition (`transitionJiraIssue` / `jira_transition_issue`).

  If no transition leads to the configured "Ready" status from the issue's current status, report
  that to the user rather than forcing it — the workflow may not allow it yet.

## Notes

- Story Points is a custom field whose id varies per site (commonly `customfield_10016`). If
  unknown, the create/edit tools or a field-listing tool can reveal it; offer to save it to config.
- Keep acceptance criteria implementation-neutral in the description, exactly as in `methodology.md`.
