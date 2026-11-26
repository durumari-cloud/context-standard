# Durumari Context Standard v0.1 — Specification

Status: **Draft, version 0.1.0**. Licensed under CC BY 4.0 (see `LICENSE-docs`).

The Durumari Context Standard defines how a team's shared context — decisions,
specifications, plans, reports, rules and work records — is stored as documents that any
AI agent or person can read and write the same way. It fixes the *format* of a document
and its revisions, the way a document body is split into addressable sections, the
vocabulary of document kinds and types, how a document records where it came from and
what it replaces, the format of work logs, writing conventions, and the instruction
block that tells an agent to use shared context.

## Reading this specification

The key words MUST, MUST NOT, REQUIRED, SHOULD, SHOULD NOT, RECOMMENDED, MAY and
OPTIONAL are to be interpreted as described in RFC 2119 and RFC 8174 when, and only
when, they appear in all capitals.

Each chapter separates two kinds of statements:

- **Normative** rules define the format and behaviour every conforming implementation
  shares. Changing one is a breaking change of the standard.
- **Implementation-defined** values are operational choices (day counts, token limits,
  page sizes, numeric caps). An implementation chooses its own values and SHOULD
  publish them. The values used by the Durumari reference implementation are listed in
  [11-implementation-defined.md](11-implementation-defined.md) for information only.

## Chapters

| # | Chapter | Content |
|---|---|---|
| 1 | [Document model](01-document-model.md) | Spaces, documents, revisions, states, trust |
| 2 | [Sections](02-sections.md) | Splitting a body, section ids, section sha256 |
| 3 | [Kinds and writing templates](03-kinds-and-templates.md) | The 13 kinds and their section templates |
| 4 | [Document types and properties](04-document-types-and-properties.md) | Standard types, columns, values, property events |
| 5 | [Provenance](05-provenance.md) | Where a revision came from |
| 6 | [Supersession and efficacy](06-supersession-and-efficacy.md) | Replacing documents, effective state |
| 7 | [Stable keys](07-stable-keys.md) | Request keys, document keys and aliases |
| 8 | [Work logs](08-work-logs.md) | Work record format and log lines |
| 9 | [Writing conventions](09-writing-conventions.md) | Titles, summaries, tags, warnings |
| 10 | [Agent instruction files](10-agent-instructions.md) | AGENTS.md managed block, CLAUDE.md, GEMINI.md |
| 11 | [Implementation-defined values](11-implementation-defined.md) | Tiers, token bounds, limits |

## Conformance

An implementation conforms to v0.1 when:

1. every document, revision, section, provenance entry, supersession reference,
   document type, property set and work log it exchanges validates against the JSON
   Schemas in `schemas/` (draft 2020-12);
2. it splits bodies into sections exactly as chapter 2 specifies (the test vectors in
   `conformance/vectors/sections.json` MUST reproduce);
3. it follows the MUST-level rules of chapters 1–10.

The suite in `conformance/` checks (1), (2) and the mechanically checkable parts of (3).

## Versioning

The standard uses semantic versioning. Within 0.x a minor version MAY change normative
rules; every change is listed in `CHANGELOG.md`. Documents do not carry the standard
version; exchanged bundles MAY state it in a `standard` field (`"durumari-context/0.1"`).
