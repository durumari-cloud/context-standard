# SPDX-FileCopyrightText: 2026 Durumari Context Standard contributors
# SPDX-License-Identifier: Apache-2.0
"""The schemas themselves are valid draft 2020-12 and agree with the registries."""

import json

import pytest
from jsonschema import Draft202012Validator

import checks
import reference
from conftest import ROOT, read_json

SCHEMAS = sorted((ROOT / "schemas").glob("*.schema.json"))


@pytest.mark.parametrize("path", SCHEMAS, ids=lambda p: p.name)
def test_schema_is_valid_draft_2020_12(path):
    schema = read_json(path)
    assert schema["$schema"] == "https://json-schema.org/draft/2020-12/schema"
    Draft202012Validator.check_schema(schema)
    assert schema["$id"] == checks.BASE + path.name.removesuffix(".schema.json")


def test_every_reference_resolves():
    for path in SCHEMAS:
        text = path.read_text(encoding="utf-8")
        for uri in {part.split('"')[0] for part in text.split('"$ref": "')[1:]}:
            if uri.startswith("#"):
                continue
            resource, _, pointer = uri.partition("#")
            resolved = checks.REGISTRY.resolver().lookup(uri)
            assert resolved.contents is not None, (path.name, uri, resource, pointer)


def test_kind_enum_matches_reference_and_registry():
    enum = read_json(ROOT / "schemas" / "common.schema.json")["$defs"]["kind"]["enum"]
    registry = [k["kind"] for k in read_json(ROOT / "registry" / "kinds.json")["kinds"]]
    assert enum == list(reference.KINDS) == registry


def test_registries_validate():
    kinds = read_json(ROOT / "registry" / "kinds.json")
    types = read_json(ROOT / "registry" / "standard-types.json")
    assert not checks.schema_errors(kinds, "urn:durumari-context-standard:0.1:schema:registry#/$defs/kinds")
    assert not checks.schema_errors(
        types, "urn:durumari-context-standard:0.1:schema:registry#/$defs/standardTypes"
    )
    for definition in types["types"]:
        assert not checks.type_problems(definition), definition["id"]


def test_every_kind_maps_to_exactly_one_type():
    types = read_json(ROOT / "registry" / "standard-types.json")["types"]
    mapped = [kind for t in types for kind in t["kinds"]]
    assert sorted(mapped) == sorted(reference.KINDS)


def test_column_kinds_match_schema():
    types = read_json(ROOT / "registry" / "standard-types.json")
    enum = read_json(ROOT / "schemas" / "document-type.schema.json")["$defs"]["columnKind"]["enum"]
    assert types["column_kinds"] == enum


def test_schemas_are_plain_ascii_json():
    for path in SCHEMAS:
        raw = path.read_bytes()
        raw.decode("ascii")
        json.loads(raw)
