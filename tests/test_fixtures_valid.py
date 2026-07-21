"""Fast, deterministic guard tests (no LLM).

These protect the fixtures the headless tests depend on and the shipped config
artifacts: every fixture config and the example config must conform to the schema.
"""

import json

import pytest

import fixtures_data as fx
from _util import REPO_ROOT, SCHEMA_PATH

jsonschema = pytest.importorskip("jsonschema")


def _validator():
    schema = json.loads(SCHEMA_PATH.read_text())
    return jsonschema.Draft7Validator(schema)


@pytest.mark.parametrize(
    "config",
    [fx.CONFIG_GHERKIN, fx.CONFIG_LINEAR],
    ids=["gherkin", "linear"],
)
def test_fixture_configs_conform_to_schema(config):
    errors = sorted(_validator().iter_errors(config), key=lambda e: list(e.path))
    assert not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_example_config_conforms_to_schema():
    example = json.loads((REPO_ROOT / ".refine-story.example.json").read_text())
    errors = sorted(_validator().iter_errors(example), key=lambda e: list(e.path))
    assert not errors, "; ".join(f"{list(e.path)}: {e.message}" for e in errors)


def test_schema_has_no_template_block():
    # The output style comes from the Golden Story, not a template; the schema must not
    # (re)introduce a `template` key.
    schema = json.loads(SCHEMA_PATH.read_text())
    assert "template" not in schema.get("properties", {})
