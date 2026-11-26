# 4. Document types and properties

## 4.1 Types over kinds

Every document has exactly one **document type**. A type is a classification above the
stored kind: either a **standard type** defined by this standard, the system type
`unsorted`, or a **custom type** defined by the people of a cloud (a group of spaces).

The type of a document is determined as follows (normative):

1. If the document stores an explicit `type_id`, that is its type (custom types,
   `unsorted`, and standard types marked *explicit* such as `sprint`).
2. Otherwise the type follows from the kind of its current revision (table 4.2).

Changing a document's type between custom types changes only its properties. Changing
to a standard type changes the kind; changing the kind clears an explicit custom type.

## 4.2 Standard types

The registry `registry/standard-types.json` is normative. Display names are informative.

| Type id | Name | Kinds that map to it | Kind of a new document | Default view |
|---|---|---|---|---|
| `work-log` | Work log / 작업 기록 | action, plan | action | dedicated |
| `spec` | Spec / 명세 | spec, architecture | spec | table |
| `proposal` | Proposal / 제안 | idea, request | idea | table |
| `decision` | Decision / 결정 | decision | decision | dedicated |
| `issue` | Issue / 이슈 | issue | issue | table |
| `sprint` | Sprint / 스프린트 | — (explicit `type_id`, stored as kind `plan`) | plan | table |
| `resource` | Resource / 자원 | resource | resource | table |
| `report` | Report / 보고 | report | report | table |
| `policy` | Policy | instruction | instruction | dedicated |
| `unsorted` | Unsorted / 분류 없음 | note, glossary | note | table |

A `plan` document whose explicit type is `sprint` is a sprint, not a work log.
`unsorted` exists in every cloud, cannot be deleted or renamed, and accepts added
columns. A document of a custom type is stored with kind `note`.

## 4.3 Columns

A type has **columns**. A column is `{id, name, kind, options, position, base, readonly}`.

- **Automatic columns** every type shows and nobody stores: `title`, `tags`,
  `created_by`, `created_at`, `updated_by`, `updated_at`.
- **Base columns** of a standard type are fixed by this standard (ids are prefixed with
  the type id, e.g. `issue.status`); they cannot be deleted or retyped. Their ids and
  choice ids are normative (see the registry).
- **Added columns** are created by a cloud on a standard, `unsorted` or custom type.
  Their ids are opaque.

Column kinds and value formats (normative):

| Column kind | JSON value | Rule |
|---|---|---|
| `text` | string | at most 2,000 characters |
| `number` | number | finite; option `format`: `number`, `percent` or `won` |
| `date` | string | `YYYY-MM-DD`, or a range `YYYY-MM-DD/YYYY-MM-DD` with start ≤ end |
| `select` | string | a choice id of the column |
| `multi_select` | array of strings | choice ids, no duplicates, at most 50 |
| `status` | string | a choice id; every choice has a `group` of `todo`, `doing` or `done` |
| `checkbox` | boolean | |
| `person` | array of strings | user ids, at most 20 |
| `url` | string | `http` or `https` URL, at most 2,000 characters |
| `email` | string | an e-mail address |
| `phone` | string | `+`, digits, spaces, `-`, `(` and `)`, 4–30 characters |
| `file` | array of `{name, url}` | at most 20, `http`/`https` URLs |
| `relation` | array of strings | document ids, at most 50; options `max`, `target_type`, `parent` |
| `unique_id` | integer | assigned by the implementation, never written by a client (chapter 7) |
| `created_by`, `created_at`, `updated_by`, `updated_at` | — | derived from the document, never stored |

`null` clears a value. Choice options are `{id, name, color?, group?}`; a `status`
column has a `default` choice (its first choice unless stated) and MAY define
`transitions` (`{from_choice: [to_choice, …]}`; a missing entry allows any move, an
empty list is a dead end), `require_reason` (choice ids) and `reason_column` (the
column that must hold a value when moving to such a choice).

## 4.4 Properties

A document's **properties** are `{type_id, values}` where `values` maps column ids to
values. Properties are not part of revision history: changing a value does not create a
revision and does not need the current `base_revision`. Clients MAY address columns and
choices by name; implementations store ids.

## 4.5 Property events

Every change of one column value of one document produces one **property event**,
stored atomically with the change, and none when the value does not change:

| Field | Rule |
|---|---|
| `column_id`, `column_name`, `column_kind` | The column as it was at the time of the change. |
| `before`, `after` | Values before and after (`null` when empty). |
| `labels` | OPTIONAL map of choice id → choice name at the time, so the event stays readable after renames. |
| `actor_kind` | `person`, `agent`, `integration`, `import` or `system` (a default or number given by the implementation). |
| `via` | `web`, `mcp`, `rest`, `cli`, `webhook` or `import`. |
| `cause` | `{kind, ref?}`; kind is `edit`, `default`, `unique_id`, `column_added`, `column_deleted`, `column_retyped`, `choice_deleted` or `sprint_close`. |
| `at` | RFC 3339 timestamp. |

## 4.6 Base columns of the standard types

| Type | Base columns |
|---|---|
| work-log | `work-log.status` status (read-only, from the work log), `work-log.agent` text, `work-log.remaining` text |
| spec | `spec.status` status (`s1` draft · `s2` in review · `s3` final · `s4` discarded), `spec.owner` person |
| proposal | `proposal.status` status (`p1` proposed · `p2` in review · `p3` adopted · `p4` rejected), `proposal.proposer` person |
| decision | `decision.effect` status (read-only: `valid` · `needs_review` · `superseded`, from efficacy), `decision.date` date, `decision.basis` relation |
| issue | `issue.status` status (`i1` to do · `i2` in progress · `i5` review · `i3` done · `i4` closed; closing requires `issue.close_reason`), `issue.severity` select (`v1`–`v4` low…urgent), `issue.assignee` person, `issue.key` unique_id (numbered per space), `issue.type` select (`t1` epic · `t2` story · `t3` task · `t4` bug), `issue.close_reason` select (`c1` duplicate · `c2` replaced · `c3` cancelled), `issue.parent` relation (max 1, parent), `issue.sprint` relation (max 1, target `sprint`), `issue.due` date |
| sprint | `sprint.period` date, `sprint.goal` text, `sprint.status` status (`sp1` planned · `sp2` active · `sp3` closed) |
| resource | `resource.type` select (`r1` document · `r2` tool · `r3` repository · `r4` data · `r5` other), `resource.link` url, `resource.owner` person |
| report | `report.period` date, `report.reporter` person |
| policy | none |

Full definitions, including status groups, are in `registry/standard-types.json`.
Caps such as the number of columns per type or choices per column are
implementation-defined.
