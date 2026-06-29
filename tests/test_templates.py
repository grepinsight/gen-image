"""Tests for the built-in prompt templates."""

import pytest

from gen_image.templates import TemplateManager

# Built-in templates that ship with the package, mapped to the variables each must expose.
BUILTIN_TEMPLATE_VARIABLES = {
    "spectrum-triad": {
        "title",
        "low_label",
        "low_behavior",
        "low_scene",
        "low_caption",
        "mid_label",
        "mid_behavior",
        "mid_scene",
        "mid_caption",
        "high_label",
        "high_behavior",
        "high_scene",
        "high_caption",
        "axis_label",
    },
    "metaphor-mapping": {
        "metaphor",
        "concept",
        "scene",
        "map_1",
        "map_2",
        "map_3",
    },
    "thought-experiment": {
        "title",
        "setup",
        "left_label",
        "left_scene",
        "left_outcome",
        "right_label",
        "right_scene",
        "right_outcome",
    },
}


@pytest.fixture
def manager(tmp_path):
    """A TemplateManager whose custom dir is isolated to a temp path."""
    return TemplateManager(custom_templates_dir=tmp_path / "custom")


def test_builtin_templates_are_listed(manager):
    """Every expected built-in template is discoverable via list_templates()."""
    builtin_names = {name for name, _ in manager.list_templates()["builtin"]}
    for name in BUILTIN_TEMPLATE_VARIABLES:
        assert name in builtin_names, f"{name} missing from built-in templates"


def test_builtin_templates_have_descriptions(manager):
    """Each built-in template's first comment line is a non-empty description."""
    descriptions = dict(manager.list_templates()["builtin"])
    for name in BUILTIN_TEMPLATE_VARIABLES:
        desc = descriptions[name]
        assert desc and desc not in {"No description", "Error reading template"}


@pytest.mark.parametrize("name,expected_vars", BUILTIN_TEMPLATE_VARIABLES.items())
def test_builtin_template_variables(manager, name, expected_vars):
    """Each built-in template exposes exactly its documented variable slots."""
    content = manager.load_template(name)
    assert set(manager.get_required_variables(content)) == expected_vars


@pytest.mark.parametrize("name,expected_vars", BUILTIN_TEMPLATE_VARIABLES.items())
def test_builtin_template_expands_without_leftover_slots(manager, name, expected_vars):
    """Filling every variable leaves no unsubstituted {{slot}} behind."""
    variables = {var: f"<{var}>" for var in expected_vars}
    expanded = manager.expand_template(name, variables)
    assert "{{" not in expanded and "}}" not in expanded
    for var in expected_vars:
        assert f"<{var}>" in expanded


def test_expand_missing_variable_raises(manager):
    """A missing required variable is reported, not silently left in place."""
    with pytest.raises(ValueError, match="Missing required variables"):
        manager.expand_template("spectrum-triad", {"title": "only one"})
