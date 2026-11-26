# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""Reference algorithms of the Durumari Context Standard v0.1 (standard library only).

Every function here is normative in the sense of spec/: an implementation that produces
different section boundaries, section ids or section hashes for the same text does not
conform. Writing-rule checks only produce warnings, as the spec requires.
"""

from __future__ import annotations

import hashlib
import re
from typing import Any

KINDS = (
    "request",
    "idea",
    "spec",
    "architecture",
    "resource",
    "decision",
    "plan",
    "action",
    "issue",
    "instruction",
    "report",
    "glossary",
    "note",
)

# ---------------------------------------------------------------------------
# Sections (spec/02-sections.md)
# ---------------------------------------------------------------------------

_HEADING = re.compile(r"^ {0,3}(#{1,6})\s+(.+?)\s*$")
_LINE = re.compile(r"[^\r\n]*(?:\r\n|\r|\n)|[^\r\n]+")
_FENCE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
_FRONT_MATTER_LINE = re.compile(r"^(?:\s*(?:#.*)?|\s+\S.*|-\s.*|[^\s:#-][^:]*:(?:\s.*)?)$")
_HEADING_LINE = re.compile(r"^ {0,3}#{1,6}\s+\S")
_FRONT_MATTER_KEY = re.compile(r"^[^\s:#-][^:]*:(?:\s.*)?$")


def section_hash(text: str) -> str:
    """Lower-case hex SHA-256 of the section text encoded as UTF-8."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def section_id(basis: str, occurrence: int) -> str:
    """First 16 hex digits of SHA-256("<basis>:<occurrence>"); basis "body" when empty."""
    return hashlib.sha256(((basis or "body") + ":" + str(occurrence)).encode("utf-8")).hexdigest()[
        :16
    ]


def _heading(line: str) -> tuple[int, str, str] | None:
    heading = _HEADING.match(line)
    if heading is None:
        return None
    raw = heading[2]
    end = len(raw.rstrip("#"))
    shown = raw[:end].strip() if 0 < end < len(raw) and raw[end - 1] in " \t" else raw
    return len(heading[1]), shown[:200], raw[:200]


def heading_level(text: str) -> int:
    first = _LINE.match(text)
    heading = _heading(first[0]) if first else None
    return heading[0] if heading else 0


def _front_matter(lines: list[str]) -> int:
    if len(lines) < 2 or lines[0].rstrip() != "---":
        return 0
    if not _FRONT_MATTER_KEY.match(lines[1].rstrip()):
        return 0
    keyed = False
    for number, line in enumerate(lines[1:], 1):
        text = line.rstrip()
        if text in {"---", "..."}:
            return number + 1 if keyed else 0
        if _HEADING_LINE.match(text) or not _FRONT_MATTER_LINE.match(text):
            return 0
        keyed = keyed or bool(_FRONT_MATTER_KEY.match(text))
    return 0


def split_sections(raw: str) -> list[dict[str, str]]:
    """Split a Markdown body into sections: [{"id", "title", "text", "sha256"}].

    The concatenation of every section's text is exactly ``raw``.
    """
    pieces: list[dict[str, str]] = []
    occurrence: dict[str, int] = {}
    title, basis = "", ""
    fence_character, fence_length = "", 0
    lines = _LINE.findall(raw)
    skipped = _front_matter(lines)
    buffer = "".join(lines[:skipped])
    for line in lines[skipped:]:
        fence = _FENCE.match(line)
        if fence_character:
            buffer += line
            if (
                fence
                and fence[1][0] == fence_character
                and len(fence[1]) >= fence_length
                and not fence[2].strip()
            ):
                fence_character, fence_length = "", 0
            continue
        if fence and not (fence[1][0] == "`" and "`" in fence[2]):
            fence_character, fence_length = fence[1][0], len(fence[1])
            buffer += line
            continue
        heading = _heading(line)
        if heading is not None:
            if buffer:
                pieces.append({"title": title, "text": buffer, "basis": basis})
            _, title, basis = heading
            buffer = line
        else:
            buffer += line
    if buffer or not pieces:
        pieces.append({"title": title, "text": buffer, "basis": basis})
    result = []
    for piece in pieces:
        identity = piece["basis"] or "body"
        number = occurrence.get(identity, 0)
        occurrence[identity] = number + 1
        result.append(
            {
                "id": section_id(identity, number),
                "title": piece["title"],
                "text": piece["text"],
                "sha256": section_hash(piece["text"]),
            }
        )
    return result


# ---------------------------------------------------------------------------
# Supersession and efficacy (spec/06-supersession-and-efficacy.md)
# ---------------------------------------------------------------------------


def effect_id(source_id: str, target_revision: int, scopes: Any) -> str:
    """Identity of one supersession effect: 24 hex digits of a canonical JSON hash."""
    canonical = _canonical_json([source_id, target_revision, scopes])
    return section_hash(canonical)[:24]


def _canonical_json(value: Any) -> str:
    import json

    return json.dumps(value, sort_keys=True, separators=(",", ":"))


def anchors(sections: list[dict[str, str]], scopes: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Resolve requested scopes against the target revision's sections; ValueError if invalid."""
    by_id = {s["id"]: s for s in sections}
    result: list[dict[str, Any]] = []
    for scope in scopes:
        section = by_id.get(scope["section_id"])
        if section is None or section["sha256"] != scope["before_sha256"]:
            raise ValueError("scope does not match the target section")
        whole = scope.get("start") is None
        start = 0 if whole else scope["start"]
        end = len(section["text"]) if whole else scope["end"]
        if not 0 <= start < end <= len(section["text"]):
            raise ValueError("scope range outside the section")
        if any(
            a["section_id"] == section["id"] and start < a["end"] and a["start"] < end
            for a in result
        ):
            raise ValueError("overlapping scopes")
        result.append({"section_id": section["id"], "start": start, "end": end, "whole": whole})
    return result


def projected(
    sections: list[dict[str, str]], effects: list[dict[str, Any]], state: str
) -> tuple[list[dict[str, str]], str]:
    """Visible current sections and the effective state of a document."""
    if state != "active":
        return [], state
    if any(e["scopes"] is None and not e.get("unresolved") for e in effects):
        competing = len({e["source_id"] for e in effects}) > 1
        return [], "needs_review" if competing else "superseded"
    if any(e.get("unresolved") and not e.get("review_sections") for e in effects):
        return [], "needs_review"
    masks: dict[str, list[tuple[int, int, str]]] = {}
    review = False
    for effect in effects:
        if effect.get("unresolved"):
            review = True
            for section in sections:
                if section["id"] in effect.get("review_sections", []):
                    masks.setdefault(section["id"], []).append(
                        (0, len(section["text"]), effect["source_id"])
                    )
        else:
            for a in effect["scopes"]:
                masks.setdefault(a["section_id"], []).append(
                    (a["start"], a["end"], effect["source_id"])
                )
    visible = []
    for section in sections:
        ranges = sorted(masks.get(section["id"], []))
        for i, (left, right, source) in enumerate(ranges):
            if any(
                left < other_end and other_start < right and other_source != source
                for other_start, other_end, other_source in ranges[i + 1 :]
            ):
                review = True
        offset, parts = 0, []
        for left, right, _ in ranges:
            if offset < left:
                parts.append(section["text"][offset:left])
            offset = max(offset, right)
        parts.append(section["text"][offset:])
        text = "".join(parts)
        if text:
            visible.append({**section, "text": text, "sha256": section_hash(text)})
    if review:
        status = "needs_review"
    elif effects and visible:
        status = "partial"
    elif effects:
        status = "superseded"
    else:
        status = "active"
    return visible, status


# ---------------------------------------------------------------------------
# Writing conventions (spec/09-writing-conventions.md): warnings, never rejections
# ---------------------------------------------------------------------------

TITLE_MIN, TITLE_MAX = 8, 80
KIND_PREFIX = re.compile(
    r"^\s*(?:\[[^\]]{1,40}\]|(?:결정|트러블슈팅|쟁점|보고|결과 보고|계획|명세|요청|아이디어|"
    r"메모|작업 기록|Policy|정책|Decision|Issue|Report|Plan|Spec|Request|Idea|Note|Work log)"
    r"\s*(?::|—|–|-)\s)",
    re.IGNORECASE,
)
WORK_LOG_PREFIX = re.compile(r"^(?:작업 기록|Work log) — ")
POLICY_PREFIX = re.compile(r"^Policy — ")
DATE = re.compile(r"(?<![0-9])20[0-9]{2}-[01][0-9]-[0-3][0-9](?![0-9])")
FILE_NAME = re.compile(r"^[\w.@-]+\.[A-Za-z0-9]{1,10}$")
UUID = re.compile(
    r"(?<![0-9A-Za-z-])([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}"
    r"-[0-9a-fA-F]{12})(?![0-9A-Za-z-])"
)
# ASCII lookarounds: a particle in another script may follow a key directly.
ISSUE_KEY = re.compile(
    r"(?<![A-Za-z0-9_-])([A-Z][A-Z0-9]{1,9}-[1-9][0-9]{0,5})(?![A-Za-z0-9_-]|\.[0-9])"
)
TAG_KEY = re.compile(r"^([A-Z][A-Z0-9]{1,9})-[1-9][0-9]{0,5}$")
# Standards, units and common abbreviations that look like issue-key prefixes.
NOT_ISSUES = frozenset(
    "UTF SHA ISO RFC AES TLS SSL HTTP HTTPS IPV ECMA ES RS HS PS MD CRC GPT KST UTC GMT "
    "CP WIN PEP CVE CWE GHSA OWASP WCAG MP FR NFR BR AC TC UC US NR PR UI UX OS IOS API".split()
)


def known_prefixes(tags: list[str]) -> set[str]:
    """Issue-key prefixes a set of tags proves to be in use."""
    found = set()
    for tag in tags:
        match = TAG_KEY.match(tag)
        if match and match[1] not in NOT_ISSUES:
            found.add(match[1])
    return found


def issue_keys(text: str, prefixes: set[str]) -> list[str]:
    found: dict[str, None] = {}
    for match in ISSUE_KEY.finditer(UUID.sub(" ", text or "")):
        key = match.group(1)
        if key.split("-", 1)[0] in prefixes:
            found.setdefault(key, None)
    return list(found)


def writing_warnings(
    revision: dict[str, Any], prefixes: set[str] | None = None
) -> list[str]:
    """Warning codes for one revision (title, summary, tags, kind, sections)."""
    codes: list[str] = []
    title = revision["title"].strip()
    tags = revision.get("tags") or []
    kind = revision.get("kind")
    work_log = kind == "action" and "work-log" in tags
    policy = kind == "instruction" and "policy" in tags
    if not (revision.get("summary") or "").strip():
        codes.append("summary_missing")
    if not tags:
        codes.append("tags_missing")
    if not any(s.get("title") for s in revision.get("sections") or []):
        codes.append("sections_missing")
    if not TITLE_MIN <= len(title) <= TITLE_MAX:
        codes.append("title_length")
    allowed = (work_log and WORK_LOG_PREFIX.match(title)) or (policy and POLICY_PREFIX.match(title))
    if KIND_PREFIX.match(title) and not allowed:
        codes.append("title_kind_prefix")
    known = (prefixes or set()) | known_prefixes(tags)
    keys = issue_keys(title, known)
    if keys and not (work_log and len(keys) == 1 and f"({keys[0]})" in title):
        codes.append("title_issue_key")
    if DATE.search(title):
        codes.append("title_date")
    if FILE_NAME.match(title) or UUID.fullmatch(title):
        codes.append("title_file_name")
    return codes


# ---------------------------------------------------------------------------
# Work logs (spec/08-work-logs.md)
# ---------------------------------------------------------------------------

LOG_LINE = re.compile(
    r"^agent-(?P<n>[0-9]+)\((?P<name>[^()\r\n]+)\) "
    r"(?P<time>[0-2][0-9]:[0-5][0-9])"
    r"(?: (?P<branch>[^\s@]+)@(?P<sha>[0-9a-f]{7,40}))?"
    r": (?P<action>[^\r\n]+?) · (?P<status>[^\r\n]+)$"
)
