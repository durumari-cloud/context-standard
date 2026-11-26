# 9. Writing conventions

These conventions make documents findable and readable by agents. An implementation
checks them after a save and returns **warnings**; it MUST NOT reject a write because of
them.

## 9.1 Rules

1. **Kind.** Choose the most specific kind (chapter 3); `action` is for work logs,
   `report` for finished results, `note` only when nothing else fits.
2. **Title** `<topic> — <conclusion>`, 8–80 characters, for example
   `Retry policy — exponential backoff with a 30 s cap`. Leave out kind prefixes
   (`Decision:`, `[QA]`), issue keys and dates: the kind, tags and revision history
   carry them. Exceptions: work logs (`Work log — …(KEY)`, chapter 8) and Policies
   (`Policy — …`).
3. **No duplicates.** Before creating, search the title; revise the existing document on
   the same topic instead of adding a second one.
4. **Summary.** One or two sentences; **the first sentence states the conclusion.**
5. **Body.** Use Markdown headings so that sections can be read and revised alone.
6. **Tags.** The issue key of the work item, one area tag when the space uses them, and the
   reserved tags only for their meaning: `work-log`, `done`, `policy`, `qa`.
7. **Provenance.** Record the person's words, documents relied on and agent work
   (chapter 5).

## 9.2 Issue keys become tags

On a save, keys of known prefixes (chapter 7.4) found in the title, summary and body
SHOULD be added as tags, in order of first appearance, without exceeding the tag limit.
On a revision only keys the change introduced are added, so a tag someone removed on
purpose is not put back.

## 9.3 Warning codes

| Code | Condition |
|---|---|
| `summary_missing` | The summary is blank. |
| `tags_missing` | There are no tags. |
| `sections_missing` | No section has a heading. |
| `title_length` | The trimmed title is shorter than 8 or longer than 80 characters. |
| `title_kind_prefix` | The title starts with a bracketed label or a kind word followed by `:`, `—`, `–` or `-` (except the work-log and Policy forms). |
| `title_issue_key` | The title contains an issue key of a known prefix (except one parenthesized key in a work-log title). |
| `title_date` | The title contains a date `20YY-MM-DD`. |
| `title_file_name` | The title is only a file name or an id. |
| `title_duplicate` | Another active document in the space has the same title. |

Implementations MAY add codes (e.g. for retired product names); clients MUST ignore
codes they do not know. The checks are `writing_warnings` in `conformance/reference.py`
(except `title_duplicate`, which needs the space).
