# Tracker Adapter — GitHub Issues + Projects

Used when `config.tracker === "github"`. Reads config from `config.github` (see `references/config.md`).

Two integration surfaces:

- **GitHub MCP** (`mcp__github__issue_read` / `mcp__github__issue_write`) — for reading and writing
  the issue itself. If the GitHub MCP is not available, fall back to the `gh` CLI
  (`gh issue view` / `gh issue create` / `gh issue edit`).
- **`gh` CLI** — for GitHub Projects (v2) field updates (Status, Estimate), which the issue API
  does not cover.

## Reading a ticket (input was e.g. `#12`)

An input of the form `#<number>` (or a bare integer) is a GitHub issue. Read it before refining:

- MCP: `mcp__github__issue_read` with `owner`, `repo`, `issue_number`.
- CLI fallback: `gh issue view <number> --repo <owner>/<repo> --json title,body,labels`.

## Creating a new issue

Use `mcp__github__issue_write` with:

- `owner`: `config.github.owner`
- `repo`: `config.github.repo`
- `title`: the refined story title
- `body`: the rendered ticket body from Step 6 (mirroring the Golden Story's style) as Markdown
- `type`: `Feature` for user-facing stories, `Task` for infrastructure/tooling stories
- `milestone`: `config.github.defaultMilestone` if set (resolve its number if the API needs one)

CLI fallback: `gh issue create --repo <owner>/<repo> --title "…" --body-file <file> [--milestone "…"]`.

## Updating an existing issue (input was an issue number)

Use `mcp__github__issue_write` with the same fields plus `issue_number` to overwrite the body with
the refined content. **Do not** change the issue's `state` or `assignee`.

CLI fallback: `gh issue edit <number> --repo <owner>/<repo> --body-file <file>`.

## Setting Project fields (Status → Ready, Estimate)

Only if `config.github.project` is present. These fields live on the **project item**, not the issue,
so they must be set with the `gh` CLI. All ids come from config — do not hardcode.

```bash
# 1. Find the project item id for this issue
gh project item-list <config.github.project.number> --owner <config.github.owner> --format json \
  | jq '.items[] | select(.content.number == <ISSUE_NUMBER>) | .id'

# 2. Set Status to "Ready"
gh project item-edit \
  --project-id <config.github.project.nodeId> \
  --id <ITEM_ID> \
  --field-id <config.github.project.statusFieldId> \
  --single-select-option-id <config.github.project.readyOptionId>

# 3. Set Estimate (number field) to the Step 4 point value
gh project item-edit \
  --project-id <config.github.project.nodeId> \
  --id <ITEM_ID> \
  --field-id <config.github.project.estimateFieldId> \
  --number <POINT_VALUE>
```

If the environment provides a `GH_TOKEN`, pass it through (`GH_TOKEN="$GH_TOKEN" gh …`).

## Discovering Project field ids (one-time, to populate config)

```bash
# Project node id + field ids/options
gh project field-list <PROJECT_NUMBER> --owner <OWNER> --format json
gh project view <PROJECT_NUMBER> --owner <OWNER> --format json   # includes the project node id
```

Copy the resulting `nodeId`, Status `statusFieldId` + "Ready" `readyOptionId`, and Estimate
`estimateFieldId` into `config.github.project`.
