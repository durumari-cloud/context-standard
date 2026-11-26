# 6. Supersession and efficacy

Revisions are never edited, so replacing old knowledge is explicit: a newer document
**supersedes** a revision of another document, wholly or in part. The superseded text
stays readable as history but leaves default current reading.

## 6.1 Supersession references

A revision MAY carry up to 16 **supersession references**:

| Field | Rule |
|---|---|
| `context_id` | REQUIRED. The superseded document. |
| `revision` | REQUIRED. The superseded revision (≥ 1). |
| `scopes` | OPTIONAL. Omitted or `null` supersedes the whole revision; otherwise 1–32 scopes. |

A **scope** is `{section_id, before_sha256, start?, end?}`. `before_sha256` MUST equal
the sha256 of that section in the superseded revision; `start` and `end` (character
offsets, `0 ≤ start < end ≤ len(text)`) MUST be given together, and their absence means
the whole section. Scopes of one reference MUST NOT overlap. An implementation MUST
reject a reference whose scope does not match.

## 6.2 Effects

Storing a reference creates an **effect** on the target document:

```
{id, source_id, source_revision, target_revision, scopes, unresolved?, review_sections?}
```

- `id` is the first 24 hex digits of the SHA-256 of the canonical JSON array
  `[source_id, target_revision, scopes]` (sorted keys, separators `,` and `:`), where
  `scopes` is the requested scope list with absent optional fields omitted, or `null`.
  `source_id` is the superseding document.
- `scopes` is `null` (whole document) or a list of **anchors**
  `{section_id, start, end, whole}` resolved against the target revision's sections.
- When the target document later gets new revisions, each anchor is carried forward: a
  whole-section anchor follows a section whose title is unique before and after; a
  partial anchor follows its exact text when that text occurs exactly once in the new
  body. Otherwise the effect becomes `unresolved: true`, with `review_sections` naming a
  known unchanged section that bounds the uncertainty, or empty when the whole document
  must be reviewed. A person resolves it by giving new scopes.

## 6.3 Efficacy

The **effective state** of a document is computed from its state and its effects
(normative; `projected` in `conformance/reference.py`):

| Effective state | When |
|---|---|
| (state) | The current revision is not `active`: `stale`, `withdrawn` or `deleted`. |
| `superseded` | A whole-document effect from one source, or partial effects that leave no visible text. |
| `needs_review` | Whole-document effects from more than one source, any unresolved effect, or overlapping effects from different sources. |
| `partial` | Some text is superseded and some remains visible. |
| `active` | No effects. |

The efficacy summary a reader receives is
`{current_revision, current_state, status, decision_count, generation}`, where `status` is
the effective state, `decision_count` the number of effects and `generation` a counter
that increases whenever the set of effects changes.

## 6.4 Current reading

A current read MUST return only the visible text: superseded ranges are removed from
each section, sections left empty are dropped, and each visible section carries the
sha256 of its visible text. A document whose effective state is `superseded`,
`needs_review` without review bounds, or not `active` has no visible current text and
SHOULD be left out of default search and lists. A pinned read is never masked.

Reactivating a superseded document requires clearing the effects of active documents
that supersede it first. The maximum number of effects per document is
implementation-defined.
