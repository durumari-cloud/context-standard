# Changelog

All notable changes to the Durumari Context Standard. The standard follows semantic
versioning; within 0.x a minor version may change normative rules.

## 0.1.0 — 2026-11-27

First public draft.

### Added

- Specification (`spec/`): document model with immutable revisions, states and trust;
  normative section splitting with 16-hex section ids and per-section SHA-256; the 13
  kinds and their writing templates; standard document types, column kinds, property
  values and property events; provenance entries; supersession references, effects and
  efficacy; request keys and `PREFIX-number` document keys with aliases; work logs
  (dedicated record and Context form, log-line format); writing conventions and warning
  codes; the `AGENTS.md` managed block imported by `CLAUDE.md` and `GEMINI.md`.
- Implementation-defined values separated into chapter 11 (activity tiers, token
  bounds, size limits), with the Durumari reference values for information.
- JSON Schemas (draft 2020-12): common, section, revision, document, provenance,
  supersession, document-type, properties, work-log, registry.
- Registries: kinds with templates, standard types with base columns.
- Instruction templates generated from one source by `templates/generate.py`.
- Synthetic examples and a conformance suite (pytest + jsonschema) with section test
  vectors and invalid fixtures; CI on GitHub-hosted Ubuntu runners.
