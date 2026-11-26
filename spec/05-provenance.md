# 5. Provenance

A revision records where its content came from as a list of **provenance entries**
(at most 16 per revision). Provenance is evidence for readers; it never grants access
to the source it names.

| Field | Rule |
|---|---|
| `kind` | REQUIRED. `user` (a person's own words), `agent` (an agent's work) or `document` (another document relied on). |
| `source_id` | OPTIONAL, at most 128 characters. For `document`, the id of the document relied on; a writer SHOULD set it, and implementations MAY derive a graph link from it. |
| `session_id` | OPTIONAL, at most 128 characters. An opaque reference to the session that produced the content. |
| `source_url` | OPTIONAL `http`/`https` URL, at most 2,048 characters, without user name, password or control characters. |
| `excerpt` | OPTIONAL quotation, at most 800 characters. |

No other field is allowed.

Normative rules:

- A writer MUST NOT store raw conversation transcripts, credentials or secrets in
  provenance. An `excerpt` is a short quotation, not a copy of a session.
- An agent SHOULD add a `user` entry for the person's words it acted on, a `document`
  entry (with `source_id`) for each document it relied on, and an `agent` entry for its
  own work.
- A reader of provenance receives the entries as data. When the original evidence of a
  revision is retained elsewhere (an archive of captured material), the implementation
  MAY report only that it exists (`availability: "retained_in_archive"` with a count),
  never its content, unless the reader is separately authorized.

Provenance pages are read like sections: each entry is serialized as JSON with sorted
keys, non-ASCII characters kept as is and the separators `", "` and `": "`, and carries
the sha256 of the UTF-8 serialization, so a reader can cite an entry by hash. Entry ids
are `provenance-<n>` for provenance and `supersedes-<n>` for supersession references,
numbered from 0.
