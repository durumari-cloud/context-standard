# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""Writing conventions, work-log lines, property values and invalid fixtures."""

import pytest

import checks
import reference
from conftest import ROOT, read_json


def rev(title, *, tags=("APP-1",), kind="decision", summary="It works.", body="# A\nx\n"):
    return {
        "title": title,
        "tags": list(tags),
        "kind": kind,
        "summary": summary,
        "sections": reference.split_sections(body),
    }


@pytest.mark.parametrize(
    "title, code",
    [
        ("Cache — keep 24 hours of reports", None),
        ("Short", "title_length"),
        ("x" * 81, "title_length"),
        ("Decision: cache reports for a day", "title_kind_prefix"),
        ("[QA] cache reports for a day", "title_kind_prefix"),
        ("결정: 보고서 캐시를 하루 유지", "title_kind_prefix"),
        ("Cache reports for a day (APP-1)", "title_issue_key"),
        ("Cache review 2026-01-05 outcome", "title_date"),
        ("report-cache.md", "title_file_name"),
        ("UTF-8 handling — always decode input", None),
    ],
)
def test_title_rules(title, code):
    codes = reference.writing_warnings(rev(title))
    assert (code in codes) if code else codes == []


def test_unknown_prefixes_are_not_issue_keys():
    assert "title_issue_key" not in reference.writing_warnings(rev("Moving XYZ-9 aside", tags=["x"]))


def test_work_log_and_policy_title_forms_are_allowed():
    log = rev("Work log — Stream exports(APP-1)", tags=["work-log", "APP-1"], kind="action")
    log_ko = rev("작업 기록 — 내보내기 스트리밍(APP-1)", tags=["work-log", "APP-1"], kind="action")
    policy = rev("Policy — review before merge", tags=["policy"], kind="instruction")
    for item in (log, log_ko, policy):
        assert reference.writing_warnings(item) == []
    two_keys = rev("Work log — APP-2 and APP-3(APP-1)", tags=["work-log", "APP-1"], kind="action")
    assert "title_issue_key" in reference.writing_warnings(two_keys)


def test_missing_summary_tags_and_headings_warn():
    codes = reference.writing_warnings(rev("Cache — one day", tags=(), summary=" ", body="plain\n"))
    assert {"summary_missing", "tags_missing", "sections_missing"} <= set(codes)


def test_issue_keys_in_text_with_known_prefixes():
    text = "Fixes APP-12 and APP-13; see SHA-256, UTF-8 and APP-12 again. 키는 APP-14와 연결"
    assert reference.issue_keys(text, {"APP", "SHA"} - reference.NOT_ISSUES) == [
        "APP-12", "APP-13", "APP-14"
    ]


@pytest.mark.parametrize(
    "line, ok",
    [
        ("agent-1(Ada Example) 09:10 feat/x@3f2a9c1: plan written · in progress", True),
        ("agent-2(name unconfirmed) 23:59: notes collected · waiting", True),
        ("agent-1 09:10 feat/x@3f2a9c1: no name · done", False),
        ("agent-1(Ada) 9:10 main@abc1234: short time · done", False),
        ("agent-1(Ada) 09:10 main@abc1234: missing status", False),
    ],
)
def test_log_line(line, ok):
    assert bool(reference.LOG_LINE.match(line)) is ok
    schema_ok = not checks.schema_errors(line, checks.BASE + "work-log#/$defs/logLine")
    assert schema_ok is ok


STATUS = {"id": "s", "kind": "status", "options": {"choices": [{"id": "a", "name": "A", "group": "todo"}]}}


@pytest.mark.parametrize(
    "column, value, ok",
    [
        ({"id": "t", "kind": "text"}, "x" * 2000, True),
        ({"id": "t", "kind": "text"}, "x" * 2001, False),
        ({"id": "d", "kind": "date"}, "2026-02-01/2026-02-14", True),
        ({"id": "d", "kind": "date"}, "2026-02-14/2026-02-01", False),
        ({"id": "d", "kind": "date"}, "2026-02-30", False),
        (STATUS, "a", True),
        (STATUS, "b", False),
        ({"id": "p", "kind": "person"}, ["u1", "u1"], False),
        ({"id": "u", "kind": "url"}, "ftp://example.com/x", False),
        ({"id": "e", "kind": "email"}, "ada@example.com", True),
        ({"id": "ph", "kind": "phone"}, "+1 (555) 010-0000", True),
        ({"id": "c", "kind": "checkbox"}, 1, False),
        ({"id": "n", "kind": "number"}, True, False),
        ({"id": "r", "kind": "relation", "options": {"max": 1}}, ["a", "b"], False),
        ({"id": "k", "kind": "unique_id"}, 7, True),
        ({"id": "f", "kind": "file"}, [{"name": "a.txt", "url": "https://example.com/a.txt"}], True),
        ({"id": "x", "kind": "text"}, None, True),
    ],
)
def test_property_values(column, value, ok):
    assert (checks.value_problem(column, value) is None) is ok


INVALID = sorted((ROOT / "conformance" / "invalid").glob("*.json"))


@pytest.mark.parametrize("path", INVALID, ids=lambda p: p.name)
def test_invalid_fixture_is_rejected(path):
    fixture = read_json(path)
    value = fixture["value"]
    if "schema" in fixture:
        problems = checks.schema_errors(value, fixture["schema"])
    else:
        problems = checks.problems_of(value, {})
    assert problems, fixture["why"]
    assert any(fixture["expect"] in p for p in problems), problems
