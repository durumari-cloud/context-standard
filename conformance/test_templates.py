# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""The instruction templates are generated from one source and keep user text."""

import importlib.util

import pytest

from conftest import ROOT

spec = importlib.util.spec_from_file_location("generate", ROOT / "templates" / "generate.py")
generate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(generate)


def test_committed_templates_match_the_source():
    assert generate.main(["--check"]) == 0


def test_importers_hold_only_the_import_block():
    for name in generate.IMPORTERS:
        text = (ROOT / "templates" / name).read_text(encoding="utf-8")
        assert text == generate.import_block() + "\n"


def test_agents_block_fills_the_project():
    block = generate.agents_block("project-123")
    assert block.startswith(generate.START + "\n## Durumari Cloud Context\n\nProject: project-123\n")
    assert block.endswith(generate.END)
    assert "{{" not in block


def test_user_text_outside_the_block_is_kept():
    text = "# My project\n\nOwn rules.\n"
    first = generate.replace_block(text, generate.agents_block("p"))
    assert first.startswith(text.rstrip() + "\n\n")
    again = generate.replace_block(first + "\nTrailing note.\n", generate.agents_block("q"))
    assert again.startswith(text.rstrip()) and again.endswith("Trailing note.\n")
    assert "Project: q" in again and "Project: p" not in again


def test_existing_import_outside_the_block_is_not_repeated():
    text = "@AGENTS.md\n\nMore.\n"
    result = generate.importer_text(text)
    assert result.count("@AGENTS.md") == 1


@pytest.mark.parametrize(
    "text",
    [
        generate.START + "\n" + generate.START + "\n" + generate.END,
        generate.END + "\n" + generate.START,
        generate.START + "\nno end\n",
    ],
)
def test_damaged_markers_are_refused(text):
    with pytest.raises(generate.ManagedTextError):
        generate.replace_block(text, generate.agents_block("p"))
