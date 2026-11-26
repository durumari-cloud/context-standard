# 7. Stable keys

Two kinds of stable key make writes and references robust: **request keys**, which make
a write idempotent, and **document keys**, which give a document a human name.

## 7.1 Request keys

Every write (create, revise, work-log update, append) carries a client-chosen
`request_key` of at most 128 characters.

- The implementation stores a receipt per (space, actor, request key) together with a
  fingerprint of the request. Resending the same key with the same request MUST return
  the original receipt and MUST NOT write again. Resending it with a different request
  MUST be rejected as a conflict.
- A request key SHOULD name the work, e.g. `release-notes-2-result`, and MUST NOT be
  reused for an unrelated write. After a lost or unclear reply, a client MUST recover with
  the same key (asking for the operation's status) instead of writing with a new key.
- Only a receipt from the implementation confirms that a write was stored.

## 7.2 Document keys

A column of kind `unique_id` numbers the documents of a type. Its key is
`PREFIX-number`:

- `PREFIX` is 2–10 characters: an upper-case ASCII letter followed by upper-case letters
  or digits (`^[A-Z][A-Z0-9]{1,9}$`). `number` is a positive integer without leading
  zeros.
- Option `numbering` is `cloud` (one counter for the whole cloud, with a column
  `prefix`) or `space` (each space has its own prefix and counter, like a tracker's
  project key). It cannot change after the column is created.
- A space prefix is unique within its cloud. Numbers are assigned under a lock and never
  reused, even after deletion.
- Keys are compared case-insensitively and stored upper-cased.

## 7.3 Aliases

Changing a space prefix keeps every old key as an **alias** of its document. Changing
back to an old prefix makes the alias current again. A key record is
`{key, context_id, kind: current | alias, source: number | prefix_change | import}`.

Wherever a document id is accepted (read, revise, delete, restore, history, relation),
an implementation SHOULD also accept a current key or alias of the same space. A key
that is missing, deleted or not readable MUST produce the same "not found" answer.

## 7.4 Issue keys in text

Text that names a key of a **known prefix** (a prefix already used as a tag in the
space, or a space/alias prefix of a key column) refers to that work item. Strings that
look like keys but are standards or units (`UTF-8`, `SHA-256`, `ISO-8601`, …) are never
keys. See chapter 9 for turning keys in text into tags.
