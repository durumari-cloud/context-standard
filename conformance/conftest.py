# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
import json
import sys
from pathlib import Path

import pytest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


@pytest.fixture(scope="session")
def manifest():
    return read_json(ROOT / "examples" / "manifest.json")


@pytest.fixture(scope="session")
def examples(manifest):
    return {item["file"]: read_json(ROOT / "examples" / item["file"]) for item in manifest["examples"]}


@pytest.fixture(scope="session")
def by_id(examples):
    return {value["id"]: value for value in examples.values() if "id" in value}
