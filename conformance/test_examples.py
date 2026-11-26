# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""Every example validates against its schema and follows the normative rules."""

import re

import pytest

import checks
import reference
from conftest import ROOT, read_json

MANIFEST = read_json(ROOT / "examples" / "manifest.json")["examples"]


def test_manifest_lists_every_example():
    listed = {item["file"] for item in MANIFEST}
    present = {
        p.relative_to(ROOT / "examples").as_posix()
        for p in (ROOT / "examples").rglob("*.json")
        if p.name != "manifest.json"
    }
    assert listed == present


@pytest.mark.parametrize("item", MANIFEST, ids=lambda i: i["file"])
def test_example_validates_against_its_schema(item, examples):
    assert checks.schema_errors(examples[item["file"]], item["schema"]) == []


@pytest.mark.parametrize("item", MANIFEST, ids=lambda i: i["file"])
def test_example_follows_the_rules(item, examples, by_id):
    value = examples[item["file"]]
    if item["schema"].endswith("#/$defs/event"):
        pytest.skip("property events have no rules beyond the schema")
    assert checks.problems_of(value, by_id) == []


def documents(examples):
    return [v for v in examples.values() if "revisions" in v]


def test_examples_have_no_writing_warnings(examples):
    for doc in documents(examples):
        for rev in doc["revisions"]:
            assert reference.writing_warnings(rev) == [], (doc["id"], rev["revision"])


def test_examples_cover_the_model(examples):
    docs = documents(examples)
    states = {d["effective_state"] for d in docs}
    assert {"active", "partial", "withdrawn"} <= states
    assert any(len(d["revisions"]) > 1 for d in docs)
    assert any(r["supersedes"] for d in docs for r in d["revisions"])
    assert {e["kind"] for d in docs for r in d["revisions"] for e in r["provenance"]} == {
        "user", "agent", "document"
    }
    assert any("key" in d and d.get("aliases") for d in docs)


FOREIGN_HOST = re.compile(r"https?://(?!example\.com\b)[A-Za-z0-9.-]+")
ISSUE_KEY = re.compile(r"\b([A-Z][A-Z0-9]{1,9})-[1-9][0-9]*\b")
SYNTHETIC_PREFIXES = {"APP", "EXP"}


def test_examples_are_synthetic():
    """Only example.com hosts and the synthetic APP/EXP issue keys appear in examples."""
    for path in (ROOT / "examples").rglob("*.json"):
        text = path.read_text(encoding="utf-8")
        assert not FOREIGN_HOST.search(text), path.name
        prefixes = {m.group(1) for m in ISSUE_KEY.finditer(text)} - reference.NOT_ISSUES
        assert prefixes <= SYNTHETIC_PREFIXES, (path.name, prefixes)
