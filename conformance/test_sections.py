# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""Section splitting reproduces the normative vectors and keeps its invariants."""

import hashlib
import random

import pytest

import reference
from conftest import ROOT, read_json

VECTORS = read_json(ROOT / "conformance" / "vectors" / "sections.json")["vectors"]


@pytest.mark.parametrize("vector", VECTORS, ids=lambda v: v["name"])
def test_vector(vector):
    assert reference.split_sections(vector["input"]) == vector["sections"]


def test_section_id_formula():
    assert reference.section_id("", 0) == hashlib.sha256(b"body:0").hexdigest()[:16]
    assert reference.section_id("Purpose", 1) == hashlib.sha256(b"Purpose:1").hexdigest()[:16]


def test_section_hash_is_sha256_of_utf8():
    assert reference.section_hash("# 목적\n") == hashlib.sha256("# 목적\n".encode()).hexdigest()


def test_ids_survive_edits_under_a_heading():
    before = reference.split_sections("# Goal\nold text\n# Plan\nsteps\n")
    after = reference.split_sections("# Goal\nnew, longer text\n# Plan\nsteps\n")
    assert [s["id"] for s in before] == [s["id"] for s in after]
    assert before[0]["sha256"] != after[0]["sha256"]
    assert before[1]["sha256"] == after[1]["sha256"]


ATOMS = ["# A\n", "## B ##\n", "text\n", "```\n", "~~~~\n", "---\n", "k: v\n", "\r\n",
         "  # C\n", "#D\n", "# 가\n", "...\n", "```py\n", " - x\n", "\r", "####### x\n"]


def test_invariants_on_generated_bodies():
    rng = random.Random(2026)
    for _ in range(2000):
        raw = "".join(rng.choice(ATOMS) for _ in range(rng.randint(0, 16)))
        sections = reference.split_sections(raw)
        assert sections
        assert "".join(s["text"] for s in sections) == raw
        assert len({s["id"] for s in sections}) == len(sections)
        assert all(s["sha256"] == reference.section_hash(s["text"]) for s in sections)
        assert all(s["text"] for s in sections) or raw == ""
