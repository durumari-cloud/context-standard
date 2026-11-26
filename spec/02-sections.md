# 2. Sections

A body is split into **sections** so that a reader can fetch, cite and revise one part
without the rest. Section boundaries, ids and hashes are normative: two conforming
implementations MUST produce identical sections for identical text. The reference
algorithm is `conformance/reference.py` (`split_sections`); the test vectors in
`conformance/vectors/sections.json` are part of this chapter.

## 2.1 Lines

The body is divided into lines. A line ends with `\r\n`, `\r` or `\n`; the terminator
belongs to the line. A final line without a terminator is still a line. No other
character (form feed, vertical tab, U+0085, U+2028, …) ends a line.

## 2.2 Headings

A line is a **heading** when it matches

```
^ {0,3}(#{1,6})\s+(.+?)\s*$
```

(Python `re` semantics, where `\s` is Unicode whitespace and `$` also matches before a
final line terminator). In words: at most three leading spaces, one to six `#`, at
least one whitespace character, then non-empty text. A tab before `#`, four or more
leading spaces, `#title` without a space, seven `#` and Setext underlines (`===`,
`---`) are not headings.

- The heading **level** is the number of `#`.
- The **id basis** is the captured text (group 2), truncated to 200 characters.
- The **title** is the id basis with a closing run of `#` removed when that run is
  preceded by a space or tab and something precedes the run; the result is trimmed.
  `## Goal ##` has title `Goal` and id basis `Goal ##`; `# C#` keeps `C#`.

## 2.3 Code fences and front matter

- A line matching `^ {0,3}(`{3,}|~{3,})(.*)$` opens a **fence**, except a backtick
  fence whose rest of line contains a backtick (that is inline code). Inside a fence no
  line is a heading. The fence closes at a line of the same character, at least as
  long, with nothing but whitespace after it. An unclosed fence runs to the end.
- A leading **YAML front matter** block is not split: when the first line is `---`,
  the second line is a `key: value` line, every following line until a closing `---`
  or `...` looks like YAML (blank, comment, indented, list item or `key:` line) and no
  line is a heading, the whole block through the closing line is body text before the
  first heading. Otherwise the leading `---` is ordinary text.

## 2.4 Splitting

Walk the lines in order. Text before the first heading forms a section with an empty
title and id basis `body`. Each heading starts a new section that contains the heading
line and every following line up to the next heading. An empty preamble produces no
section. An empty body produces exactly one section with empty text.

The concatenation of all section texts, in order, MUST equal the body byte for byte.

## 2.5 Section id and sha256

- **id**: let *basis* be the id basis (`body` for the untitled first section) and *n*
  the number of earlier sections with the same basis (0 for the first). The id is the
  first 16 lower-case hex digits of `SHA-256(UTF-8(basis + ":" + n))`.
  Ids therefore stay the same when text under a heading changes, and differ for
  repeated headings.
- **sha256**: lower-case hex `SHA-256` of the section text encoded as UTF-8,
  including its heading line and line terminators.

A section object is `{id, title, text, sha256}`; outline views MAY add `level`,
`chars` and `bytes` and omit `text`.

## 2.6 Revising sections

A writer revises a section by sending its `id`, the `before_sha256` it read and the new
text. The implementation MUST reject the change when the current section's sha256
differs (the section changed since it was read). A writer MAY instead **append** text to
the end of a named section without reading it; appends are applied to the current text
and never conflict with each other.

An implementation MAY ask for explicit confirmation when a change shrinks a section a
lot; the threshold is implementation-defined. The maximum number of sections per body
is implementation-defined.
