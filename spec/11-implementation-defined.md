# 11. Implementation-defined values

The values below are **operational choices**, not part of the format. An implementation
picks its own and SHOULD publish them. The column "Durumari reference" shows the values
of the Durumari reference implementation at the time of v0.1, for information only;
they may change without a new version of this standard.

## 11.1 Activity tiers

A document MAY carry a tier derived from real activity:

| Tier | Meaning (normative) |
|---|---|
| `hot` | Current; ranked normally. |
| `warm` | Idle; ranked lower in search. |
| `cold` | Long idle; left out of default lists and search, **never deleted**. |

Any real read or edit, or an explicit wake, returns a document to `hot`. Tiering never
changes revisions, content or `updated_at`. Bulk activity (one actor touching many
documents in a short window) is not real activity.

| Value | Durumari reference |
|---|---|
| Idle time before a hot document is put on notice | 14 days |
| Grace period from notice to `warm` | 7 days |
| Time in `warm` before `cold` | 30 days |
| Idle time before a `done` work log becomes `warm` (no notice) | 7 days |
| Sweep detection | 20 or more distinct documents by one actor within 10 minutes |
| Kinds kept `hot` | decision, spec, architecture, glossary, instruction; also favorites and documents a current document cites |
| Superseded documents | `warm` without notice |

A hot document on notice MAY report when it will become warm (`tier_warm_at`).

## 11.2 Token bounds and paging

Reads are paged so that one response fits an agent's context budget. The shape of a
page (`sections`, `truncated`, `next_after`, `coverage`, `token_bound`) is normative;
the estimator and limits are not.

| Value | Durumari reference |
|---|---|
| `token_bound` label | `estimated_tokens` |
| Estimator | min(UTF-8 bytes of the JSON response, ⌈1.1 × weighted characters⌉) with weights: ASCII letter 0.4, digit 1, punctuation 0.5, whitespace 0.25, Hangul syllable 1.5, other non-ASCII = UTF-8 bytes |
| Continuation | opaque URL-safe base64 cursor bound to document id, revision and view; a changed document invalidates it |
| Page reservation | every page reserves room for a continuation |

## 11.3 Size limits

| Limit | Durumari reference |
|---|---|
| Body | 100,000 characters and 262,144 UTF-8 bytes |
| Sections per body | 512 |
| Supersession scopes per reference | 32 (normative maximum in the schema) |
| Effects per document | 128 |
| Columns per type | 60 |
| Custom types per cloud | 200 |
| Choices per column | 100 |
| Largest starting number of a `unique_id` column | 10^12 |
| Section appends / section patches per write | 32 each |
| Relations per write (`relates_to`) | 8 |
| Large-shrink confirmation | required when a change shrinks a section a lot (`allow_shrink`) |

## 11.4 Relations between documents

The reference implementation lets a write link documents with
`relates_to: [{context_id, relation, revision?}]` where `relation` is `references`,
`supports`, `implements` or `blocks`. Relation vocabularies beyond provenance and
supersession are outside v0.1.
