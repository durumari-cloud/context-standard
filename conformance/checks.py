# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""Schema validation plus the rule checks a JSON Schema cannot express.

    python conformance/checks.py FILE [FILE ...]     # documents, work logs, types

Exit status 0 when every file conforms; problems are printed one per line.
"""

from __future__ import annotations

import json
import re
import sys
from datetime import date
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

BASE = "urn:durumari-context-standard:0.1:schema:"


def load_registry() -> Registry:
    resources = []
    for path in sorted((ROOT / "schemas").glob("*.schema.json")):
        schema = json.loads(path.read_text(encoding="utf-8"))
        resources.append((schema["$id"], Resource.from_contents(schema)))
    return Registry().with_resources(resources)


REGISTRY = load_registry()


def schema_errors(instance: Any, uri: str) -> list[str]:
    schema = {"$ref": uri}
    validator = Draft202012Validator(schema, registry=REGISTRY, format_checker=FormatChecker())
    return [
        f"schema: {'/'.join(map(str, e.absolute_path)) or '<root>'}: {e.message}"
        for e in sorted(validator.iter_errors(instance), key=lambda e: list(e.absolute_path))
    ]


def standard_types() -> dict[str, dict[str, Any]]:
    data = json.loads((ROOT / "registry" / "standard-types.json").read_text(encoding="utf-8"))
    return {item["id"]: item for item in data["types"]}


# ---------------------------------------------------------------------------
# Documents
# ---------------------------------------------------------------------------


def revision_problems(rev: dict[str, Any]) -> list[str]:
    where = f"revision {rev['revision']}"
    problems = []
    expected = reference.split_sections(rev["body"])
    if "".join(s["text"] for s in rev["sections"]) != rev["body"]:
        problems.append(f"{where}: section texts do not concatenate to the body")
    for section in rev["sections"]:
        if reference.section_hash(section["text"]) != section["sha256"]:
            problems.append(f"{where}: section {section['id']} sha256 is wrong")
    stripped = [{k: s[k] for k in ("id", "title", "text", "sha256")} for s in rev["sections"]]
    if stripped != expected:
        problems.append(f"{where}: sections differ from the normative split of the body")
    if len({t.strip() for t in rev["tags"]}) != len(rev["tags"]):
        problems.append(f"{where}: duplicate tags")
    if rev["kind"] not in reference.KINDS:
        problems.append(f"{where}: unknown kind {rev['kind']!r}")
    for entry in rev["provenance"]:
        if entry["kind"] == "document" and "source_id" not in entry:
            problems.append(f"{where}: document provenance without source_id (SHOULD)")
    return problems


def work_log_document_problems(rev: dict[str, Any]) -> list[str]:
    problems = []
    if not reference.WORK_LOG_PREFIX.match(rev["title"]):
        problems.append("work log: title must start with 'Work log — ' or '작업 기록 — '")
    if len(rev["summary"]) > 300:
        problems.append("work log: summary longer than 300 characters")
    log = [s for s in rev["sections"] if s["title"].lower() in {"progress log", "진행 기록", "작업 로그"}]
    for section in log:
        for line in section["text"].splitlines()[1:]:
            if line.strip() and not reference.LOG_LINE.match(line):
                problems.append(f"work log: line does not follow the log format: {line!r}")
    if any(reference.DATE.search(s["title"]) for s in rev["sections"]):
        problems.append("work log: section headings must not carry dates")
    return problems


def document_problems(doc: dict[str, Any], others: dict[str, dict[str, Any]] | None = None) -> list[str]:
    problems = schema_errors(doc, BASE + "document")
    if problems:
        return problems
    revisions = doc["revisions"]
    numbers = [r["revision"] for r in revisions]
    if numbers != list(range(1, len(numbers) + 1)):
        problems.append("revisions are not consecutive from 1")
    current = revisions[-1]
    if doc["revision"] != current["revision"]:
        problems.append("revision does not name the last revision")
    if doc["state"] != current["state"]:
        problems.append("state differs from the current revision's state")
    for rev in revisions:
        if rev["context_id"] != doc["id"]:
            problems.append(f"revision {rev['revision']}: context_id differs from the document id")
        problems += revision_problems(rev)
    _, status = reference.projected(current["sections"], doc["lifecycle"], current["state"])
    if doc["effective_state"] != status or doc["efficacy"]["status"] != status:
        problems.append(f"effective state should be {status!r}")
    eff = doc["efficacy"]
    if eff["current_revision"] != doc["revision"] or eff["current_state"] != doc["state"]:
        problems.append("efficacy does not describe the current revision")
    if eff["decision_count"] != len(doc["lifecycle"]):
        problems.append("efficacy decision_count differs from the number of effects")
    for effect in doc["lifecycle"]:
        problems += effect_problems(doc, effect, others or {})
    if current["kind"] == "action" and "work-log" in current["tags"]:
        problems += work_log_document_problems(current)
    if "properties" in doc:
        problems += property_problems(doc, doc["properties"], others or {})
    return problems


def effect_problems(target: dict[str, Any], effect: dict[str, Any], others: dict[str, Any]) -> list[str]:
    problems = []
    by_number = {r["revision"]: r for r in target["revisions"]}
    original = by_number.get(effect["target_revision"])
    if original is None:
        return [f"effect {effect['id']}: target revision is missing"]
    source = others.get(effect["source_id"])
    if source is None:
        return problems
    source_rev = {r["revision"]: r for r in source["revisions"]}.get(effect["source_revision"])
    refs = [
        r for r in (source_rev or {}).get("supersedes", [])
        if r["context_id"] == target["id"] and r["revision"] == effect["target_revision"]
    ]
    if not refs:
        return [f"effect {effect['id']}: the source revision does not supersede this target"]
    scopes = refs[0].get("scopes")
    if reference.effect_id(effect["source_id"], effect["target_revision"], scopes) != effect["id"]:
        problems.append(f"effect {effect['id']}: id does not match its source reference")
    if scopes is not None and not effect.get("unresolved"):
        try:
            anchors = reference.anchors(original["sections"], scopes)
        except ValueError as error:
            return problems + [f"effect {effect['id']}: {error}"]
        if effect["target_revision"] == target["revision"] and anchors != effect["scopes"]:
            problems.append(f"effect {effect['id']}: anchors differ from the resolved scopes")
    return problems


# ---------------------------------------------------------------------------
# Properties
# ---------------------------------------------------------------------------

_DATE = re.compile(r"^(\d{4}-\d{2}-\d{2})(?:/(\d{4}-\d{2}-\d{2}))?$")
_EMAIL = re.compile(r"^[^@\s]{1,64}@[^@\s]{1,190}\.[^@\s]{2,63}$")
_PHONE = re.compile(r"^\+?[0-9 ()\-]{4,30}$")
_URL = re.compile(r"^https?://[^\s]{1,1990}$")


def _strings(value: Any, limit: int) -> bool:
    return (
        isinstance(value, list)
        and len(value) <= limit
        and all(isinstance(v, str) and v for v in value)
        and len(set(value)) == len(value)
    )


def value_problem(column: dict[str, Any], value: Any) -> str | None:
    """None when ``value`` is a valid value of ``column`` (spec chapter 4.3)."""
    if value is None:
        return None
    kind, options = column["kind"], column.get("options") or {}
    choices = {c["id"] for c in options.get("choices", [])}
    ok = True
    if kind == "text":
        ok = isinstance(value, str) and len(value) <= 2000
    elif kind == "number":
        ok = isinstance(value, (int, float)) and not isinstance(value, bool) and value == value
        ok = ok and value not in (float("inf"), float("-inf"))
    elif kind == "date":
        match = _DATE.match(value) if isinstance(value, str) else None
        try:
            days = [date.fromisoformat(d) for d in match.groups() if d] if match else []
        except ValueError:
            days = []
        ok = bool(days) and (len(days) == 1 or days[0] <= days[1])
    elif kind in {"select", "status"}:
        ok = isinstance(value, str) and value in choices
    elif kind == "multi_select":
        ok = _strings(value, 50) and set(value) <= choices
    elif kind == "checkbox":
        ok = isinstance(value, bool)
    elif kind == "person":
        ok = _strings(value, 20)
    elif kind == "url":
        ok = isinstance(value, str) and len(value) <= 2000 and bool(_URL.match(value))
    elif kind == "email":
        ok = isinstance(value, str) and bool(_EMAIL.match(value))
    elif kind == "phone":
        ok = isinstance(value, str) and bool(_PHONE.match(value))
    elif kind == "file":
        ok = isinstance(value, list) and len(value) <= 20 and all(
            isinstance(f, dict) and set(f) == {"name", "url"} and isinstance(f["name"], str)
            and isinstance(f["url"], str) and bool(_URL.match(f["url"]))
            for f in value
        )
    elif kind == "relation":
        ok = _strings(value, min(50, options.get("max", 50)))
    elif kind == "unique_id":
        ok = isinstance(value, int) and not isinstance(value, bool) and value >= 1
    else:
        return f"column {column['id']}: kind {kind} is never stored"
    return None if ok else f"column {column['id']}: invalid {kind} value {value!r}"


def property_problems(doc: dict[str, Any], props: dict[str, Any], others: dict[str, Any]) -> list[str]:
    types = standard_types()
    type_id = props["type_id"]
    definition = types.get(type_id) or others.get(type_id)
    if definition is None:
        return [f"properties: unknown type {type_id!r}"]
    kind = doc["revisions"][-1]["kind"]
    if definition.get("standard") and not definition.get("explicit") and kind not in definition["kinds"]:
        return [f"properties: kind {kind!r} does not map to type {type_id!r}"]
    columns = {c["id"]: c for c in definition["columns"]}
    problems = []
    for column_id, value in props["values"].items():
        column = columns.get(column_id)
        if column is None:
            problems.append(f"properties: unknown column {column_id!r}")
            continue
        problem = value_problem(column, value)
        if problem:
            problems.append("properties: " + problem)
    return problems


# ---------------------------------------------------------------------------
# Work logs and types
# ---------------------------------------------------------------------------


def work_log_problems(record: dict[str, Any]) -> list[str]:
    problems = schema_errors(record, BASE + "work-log")
    if problems:
        return problems
    numbers = [e["revision"] for e in record["events"]]
    if numbers != sorted(numbers) or len(set(numbers)) != len(numbers):
        problems.append("events must be in increasing revision order, one per revision")
    if numbers[-1] != record["revision"]:
        problems.append("the last event must belong to the current revision")
    return problems


def type_problems(definition: dict[str, Any]) -> list[str]:
    problems = schema_errors(definition, BASE + "document-type")
    if problems:
        return problems
    ids = [c["id"] for c in definition["columns"]]
    if len(set(ids)) != len(ids):
        problems.append("duplicate column ids")
    for column in definition["columns"]:
        options = column.get("options") or {}
        choices = [c["id"] for c in options.get("choices", [])]
        if len(set(choices)) != len(choices):
            problems.append(f"column {column['id']}: duplicate choice ids")
        if column["kind"] == "status" and any("group" not in c for c in options.get("choices", [])):
            problems.append(f"column {column['id']}: every status choice needs a group")
        if "default" in options and options["default"] not in choices:
            problems.append(f"column {column['id']}: default is not a choice")
        for source, targets in (options.get("transitions") or {}).items():
            if source not in choices or not set(targets) <= set(choices):
                problems.append(f"column {column['id']}: transition names an unknown choice")
    return problems


def problems_of(value: dict[str, Any], others: dict[str, Any] | None = None) -> list[str]:
    if "revisions" in value:
        return document_problems(value, others)
    if "events" in value:
        return work_log_problems(value)
    if "columns" in value:
        return type_problems(value)
    return ["unrecognized file: expected a document, work log or document type"]


def main(argv: list[str]) -> int:
    values = {}
    for name in argv:
        values[name] = json.loads(Path(name).read_text(encoding="utf-8"))
    by_id = {v["id"]: v for v in values.values() if isinstance(v, dict) and "id" in v}
    failed = False
    for name, value in values.items():
        found = problems_of(value, by_id)
        for problem in found:
            print(f"{name}: {problem}")
        failed = failed or bool(found)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
