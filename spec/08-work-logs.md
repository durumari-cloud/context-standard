# 8. Work logs

A **work log** records one task that agents and people carry out: its goal, progress,
remaining steps and who is working on it, so that another agent or session can take it
over. Keep **one work log per task**; continue the existing log instead of creating a
document per checkpoint.

Two forms are standard. An implementation SHOULD offer the dedicated form and MUST be
able to read the Context form.

## 8.1 Dedicated work record

| Field | Rule |
|---|---|
| `id` | Opaque identifier. |
| `title` | 1–200 characters, not blank. |
| `status` | `unknown`, `in_progress`, `waiting`, `complete` or `stopped`. |
| `summary`, `completed`, `remaining`, `next_action`, `constraints`, `waiting_reason` | Text, at most 2,000 characters each. |
| `assignee_id` | OPTIONAL person id. |
| `agent` | OPTIONAL name of the agent working on it, at most 100 characters. |
| `session_ref` | OPTIONAL opaque session reference, at most 256 characters. |
| `evidence` | At most 20 entries, each at most 2,000 characters (commit, test run, link). |
| `revision` | Starts at 1 and increases by 1 with each change. |
| `source_context_id`, `source_revision` | OPTIONAL link to a Context-form work log it was imported from. |
| `events` | Append-only list of events, one per revision. |

An **event** is `{revision, actor_kind, agent?, kind, text, created_at}`:

- `actor_kind` is `human` or `agent`.
- `kind` is `reported`, `verified` or `human_confirmed`. An agent MUST only write
  `reported` events; `verified` and `human_confirmed` need a separate verification or a
  person.
- `text` is 1–4,000 characters.

Updates name the `base_revision` they read. Taking over an unfinished record from another
agent or session (`accept_handoff`) MUST name the receiving agent and session; the
implementation refuses a record another session is actively working on and records a
`reported` event of the handoff.

Status groups for tables: `in_progress` → doing; `waiting`, `unknown` → todo;
`complete`, `stopped` → done.

## 8.2 Context-form work log

Where the dedicated form is not adopted, a work log is a Context document with:

- kind `action` and the tag `work-log`; the issue key of the task as a tag when there is one;
- title `Work log — <task>(<issue key>)` (Korean: `작업 기록 — <task>(<issue key>)`);
  the issue key in parentheses is the only key allowed in a title;
- a summary of at most 300 characters that names **the current agent first**, then the
  goal and the remaining steps, repeated at the top of the body;
- below it an **append-only progress log**: one line per plan, stage, commit, and before
  ending or handing over, appended to the end of the log section (section append,
  chapter 2.6) without rewriting earlier lines;
- section headings without dates (`## Current state`, not `## Current state (2026-01-02)`);
  date the summary and the log lines instead;
- when the task is complete, its result recorded and the tag `done` added.

## 8.3 Log line format

```
agent-N(display_name) HH:MM branch@SHA: action · status
```

- `N` numbers the agents working on the task; `display_name` is the account's display
  name. When it is not available, write `agent-N(name unconfirmed)`; never infer a name
  from a local user name, device or branch.
- `HH:MM` is the local time of the step.
- `branch@SHA` are read from Git output (never remembered); they are omitted when the
  work has no repository.
- `action` says what was done, `status` how it stands, separated by ` · `
  (space, U+00B7 middle dot, space).

The regular expression `LOG_LINE` in `conformance/reference.py` is normative for v0.1.
Log lines MUST NOT contain conversation copies or credentials.
