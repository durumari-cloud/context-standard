# 1. Document model

## 1.1 Spaces

A **space** is the boundary that owns documents (a project, team area or repository's
shared context). Every document belongs to exactly one space. A space has an opaque
identifier. Access control is outside this standard: being able to name a space or a
document never grants access to it.

## 1.2 Documents

A **document** (also called a *Context*) is one unit of shared knowledge with a stable
identity and an ordered history of revisions.

| Field | Normative rule |
|---|---|
| `id` | Opaque, immutable identifier. In v0.1 a lower-case UUID string (36 characters). |
| `space_id` | Identifier of the owning space. |
| `revision` | Number of the current revision (see 1.3). |
| `state` | State of the current revision (1.4). |
| `effective_state` | Efficacy of the current revision after supersession (chapter 6). |
| `lifecycle` | Supersession effects currently applied to the document (chapter 6). |
| `key` | OPTIONAL human key such as `APP-12` (chapter 7). |
| `type_id`, `properties` | OPTIONAL document type and column values (chapter 4). |
| `tier` | OPTIONAL activity tier `hot`, `warm` or `cold` (chapter 11). |
| `revisions` | The revisions, oldest first, when a document is exchanged as a whole. |

The document's title, summary, tags, kind and body are those of its current revision.

## 1.3 Revisions

A **revision** is an immutable snapshot. A change to a document's title, summary,
tags, kind, body, state, provenance or supersession creates a new revision; a revision
is never edited after it is stored.

- Revision numbers start at 1 and increase by exactly 1. An exchanged document's
  `revisions` array MUST be consecutive and its last entry MUST equal `revision`.
- A writer that changes a document MUST state the revision it read (`base_revision`).
  If that is no longer the current revision, the implementation MUST reject the write
  (optimistic concurrency) unless the change only appends to the end of sections
  (section append, chapter 2.6).
- Column values (chapter 4) are **not** part of revision history.

Revision fields:

| Field | Rule |
|---|---|
| `context_id`, `revision` | Identity of the revision. |
| `title` | 1–200 characters, not blank. |
| `summary` | 0–500 characters. |
| `tags` | At most 20 tags, each 1–40 characters after trimming, no duplicates. |
| `kind` | One of the 13 kinds (chapter 3). |
| `state` | `active`, `stale`, `withdrawn` or `deleted`. |
| `trust` | Trust level of the content (1.5). |
| `body` | Markdown text. |
| `sections` | The body split per chapter 2. The concatenation of section texts MUST equal `body`. |
| `provenance` | 0–16 provenance entries (chapter 5). |
| `supersedes` | 0–16 supersession references (chapter 6). |
| `created_at` | RFC 3339 timestamp when the revision was stored. |
| `author` | OPTIONAL actor `{kind, id?, label?}`; kind is `person`, `agent`, `integration`, `import` or `system`. |

The body is UTF-8 text without NUL characters. Its maximum size is implementation-defined.

## 1.4 States

| State | Meaning |
|---|---|
| `active` | Current and in effect (subject to supersession). |
| `stale` | Kept for history, no current effect. A restored old revision that a person did not re-activate is `stale`. |
| `withdrawn` | Retracted by its owner; kept for history. |
| `deleted` | Removed from default reading; history is kept and the document can be restored. |

A document that is not `active` has no visible current sections (chapter 6.4). Reading
a pinned older revision MUST return its stored text unchanged.

## 1.5 Trust

`trust` states how far the content is confirmed:

| Value | Meaning |
|---|---|
| `reported` | The writer's own account; not independently verified. Default, and the only value an agent MAY set on its own. |
| `verified` | Reserved in v0.1: checked by a separate verification step. |
| `human_confirmed` | Reserved in v0.1: a person confirmed it directly. |

Choosing a kind such as `decision` never makes a document confirmed by a person.

## 1.6 Reading current and pinned revisions

A reader asks either for the **current** document or for a **pinned** revision.

- A current read returns the sections still in effect (chapter 6) and reports
  `reference_mode: "current"`.
- A pinned read returns the stored revision exactly and reports `reference_mode: "pinned"`.
  Pinned text is historical evidence; it MUST NOT be presented as a current decision.
- Every returned section carries its `id` and `sha256`. An agent that relies on a section
  SHOULD bind its evidence to the document id, revision, section id and section sha256.

Reads MAY be paged. A paged response states `truncated` and an opaque continuation
`next_after`; a client MUST follow continuations before replacing a section it has
only partly read. Page sizes and token bounds are implementation-defined.
