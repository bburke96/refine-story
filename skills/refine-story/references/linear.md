# Tracker Adapter — Linear

Used when `config.tracker === "linear"`. Reads config from `config.linear` (see `references/config.md`).

Integration is via the **Linear MCP server** (`https://mcp.linear.app/mcp`, OAuth). Install for Claude
Code with:

```
claude mcp add --transport http linear-server https://mcp.linear.app/mcp
```

The server exposes tools for finding, creating, and updating Linear objects. Exact names depend on
the server version; commonly available tools include `get_issue`, `list_issues`, `create_issue`,
`update_issue`, `list_teams`, `list_projects`, `list_issue_statuses` (workflow states), and
`list_issue_labels`. **Do not assume tool names** — inspect the available `mcp__*linear*` tools at
runtime and map them to the operations below. If no Linear tool is available, tell the user Linear
integration requires the Linear MCP server and stop (still deliver the refined-story text).

## Input parsing

- `ENG-123` (team-key dash number) → a Linear issue identifier. Read it before refining.
- This is the **same shape as a Jira key**, so rely on `config.tracker` to disambiguate: when
  `tracker` is `linear`, treat `TEAM-123` as a Linear identifier.
- A bare `#12` or integer is not Linear-native; confirm with the user what they mean.

## Reading a ticket

Call the "get issue" tool with the identifier (e.g. `ENG-123`). Extract title, description, and
current state.

## Creating a new issue

Call the "create issue" tool with:

- `team`: `config.linear.teamKey` (resolve to a team id via a "list teams" tool if the create tool
  requires an id rather than a key).
- `title`: the refined story title.
- `description`: the rendered ticket body from Step 6 (mirroring the Golden Story's style) as
  Markdown — Linear descriptions are Markdown.
- `project`: `config.linear.projectName` if set (resolve to a project id if needed).
- `estimate`: the Step 4 point value. **Estimate is a native numeric field in Linear** — set it
  directly, no custom field id required. (The team must have estimation enabled; if it isn't, report
  that rather than failing silently.)
- `labels` (optional): `config.linear.featureLabel` for user-facing stories, `config.linear.taskLabel`
  for infrastructure/tooling stories, when configured.

## Updating an existing issue (input was a Linear identifier)

Call the "update issue" tool to overwrite the description with the refined content and set `estimate`.
**Do not** change the assignee.

## Setting the workflow state → Ready

Linear status is a **team workflow state**, not a free-form field:

1. List the team's workflow states (e.g. `list_issue_statuses` for `config.linear.teamKey`).
2. Find the state whose name equals `config.linear.readyStateName`.
3. Set the issue's state to it via the "update issue" tool.

If the team has no state matching `readyStateName`, report the available state names to the user
rather than guessing.

## Notes

- Unlike Jira, Linear needs no Story-Points custom field — `estimate` is built in.
- Keep acceptance criteria implementation-neutral in the description, exactly as in `methodology.md`.
