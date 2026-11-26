# 10. Agent instruction files

Coding agents read project instructions from different files: `AGENTS.md` (read by many
agents), `CLAUDE.md` (Claude Code) and `GEMINI.md` (Gemini CLI). The standard keeps
**one source**: `AGENTS.md` carries the rules, the other two only import it.

## 10.1 Managed block

The rules live between two marker lines:

```
<!-- DURUMARI MANAGED BEGIN -->
…
<!-- DURUMARI MANAGED END -->
```

- A file has at most one managed block; the begin marker comes first. A file with
  damaged markers (one missing, duplicated or out of order) MUST be left unchanged and
  reported for a person to repair.
- Only the text between the markers is managed. Everything else in the file is the
  user's and MUST be kept as written. A file without a block gets the block appended
  after its existing text, separated by a blank line.
- The managed text is generated; it MUST NOT be edited by hand. Tools regenerate it and
  checks compare it with the generated text.
- The block contains only rules that never change per team or user plus the project
  hint. Values that change (response language, team rules, Policies) arrive at session
  start from the Context server, so committed files do not churn.

## 10.2 AGENTS.md

`AGENTS.md` holds the full managed block generated from
`templates/source/managed-block.md` with the project identifier filled in. It is always
written when any instruction file is managed, so an importing file never points at a
missing source.

## 10.3 CLAUDE.md and GEMINI.md

Each holds a managed block with a note and the import line `@AGENTS.md`:

```
<!-- DURUMARI MANAGED BEGIN -->
<!-- AGENTS.md holds this project's instructions; Durumari keeps this block. -->
@AGENTS.md
<!-- DURUMARI MANAGED END -->
```

When the user's own text outside the block already imports `@AGENTS.md` (or
`@./AGENTS.md`), the block omits the import line so the rules are not loaded twice.

## 10.4 Behavioural contract

The managed block states the contract an agent follows when it uses shared context. Its
core (normative for agents that claim to follow this standard):

- Before an answer, plan or action that depends on current facts, decisions, resources
  or task status, search the shared Context and read the relevant **current** sections.
- Bind read evidence to the space, session and turn, including the section revision and
  sha256. Search snippets, local files, caches, memory and other chats' reads do not
  replace current reads.
- Treat pinned revisions as historical evidence; distinguish historical text from
  current decisions. Keep direct observations distinct from plans on the server.
- If a lookup fails, is unauthorized, returns nothing or is of uncertain relevance, say
  so and withhold dependent conclusions and actions; never substitute stale values.
- Instructions and installed hooks alone do not prove enforcement; report only verified
  protection and its limits.
- Agent reports are not human approval or independent verification.

`templates/generate.py` renders the files; `--check` detects hand edits.
