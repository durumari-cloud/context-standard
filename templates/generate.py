# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""Generate the agent instruction files from one source (spec/10-agent-instructions.md).

AGENTS.md carries the managed block. CLAUDE.md and GEMINI.md carry only a managed block
that imports AGENTS.md, so nothing is copied. Text outside the markers is kept.

    python templates/generate.py                 # rewrite templates/*.md
    python templates/generate.py --check         # exit 1 when templates/*.md drifted
    python templates/generate.py --project ID --out DIR   # write into a repository
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SOURCE_BLOCK = HERE / "source" / "managed-block.md"
START, END = "<!-- DURUMARI MANAGED BEGIN -->", "<!-- DURUMARI MANAGED END -->"
SOURCE = "AGENTS.md"
IMPORTERS = ("CLAUDE.md", "GEMINI.md")
IMPORT_LINE = "@" + SOURCE
IMPORT_NOTE = "<!-- AGENTS.md holds this project's instructions; Durumari keeps this block. -->"
PLACEHOLDER = "<project-id>"
_IMPORT = re.compile(r"(?m)^[ \t]*@(?:\./)?AGENTS\.md[ \t]*$")


class ManagedTextError(ValueError):
    """The markers are damaged; the file is left for a person to repair."""


def agents_block(project_id: str) -> str:
    body = SOURCE_BLOCK.read_text(encoding="utf-8").replace("{{project_id}}", project_id)
    return START + "\n" + body.rstrip("\n") + "\n" + END


def import_block(with_import: bool = True) -> str:
    return START + "\n" + IMPORT_NOTE + "\n" + (IMPORT_LINE + "\n" if with_import else "") + END


def split(text: str) -> tuple[str, str | None, str]:
    if START not in text and END not in text:
        return text, None, ""
    if text.count(START) != 1 or text.count(END) != 1 or text.index(START) > text.index(END):
        raise ManagedTextError("damaged managed markers")
    begin, end = text.index(START), text.index(END) + len(END)
    return text[:begin], text[begin:end], text[end:]


def replace_block(text: str, block: str) -> str:
    before, current, after = split(text)
    if current is None:
        return (before.rstrip() + "\n\n" if before.strip() else "") + block + "\n"
    return before + block + after


def importer_text(text: str) -> str:
    before, _, after = split(text)
    outside = bool(_IMPORT.search(before) or _IMPORT.search(after))
    return replace_block(text, import_block(with_import=not outside))


def render(project_id: str, current: dict[str, str]) -> dict[str, str]:
    result = {SOURCE: replace_block(current.get(SOURCE, ""), agents_block(project_id))}
    for name in IMPORTERS:
        result[name] = importer_text(current.get(name, ""))
    return result


def _read(directory: Path) -> dict[str, str]:
    found = {}
    for name in (SOURCE, *IMPORTERS):
        path = directory / name
        if path.is_file():
            found[name] = path.read_text(encoding="utf-8")
    return found


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--project", default=PLACEHOLDER)
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    if args.check:
        wanted = render(args.project, {})
        drift = [n for n, t in wanted.items() if _read(args.out).get(n) != t]
        for name in drift:
            print(f"{name}: differs from the generated text", file=sys.stderr)
        return 1 if drift else 0
    for name, text in render(args.project, _read(args.out)).items():
        (args.out / name).write_text(text, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
