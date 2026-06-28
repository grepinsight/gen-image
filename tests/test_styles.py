"""Tests for style presets, including the first-person POV style."""

from gen_image.styles import (
    STYLE_DEFINITIONS,
    StylePreset,
    get_style_prompt_prefix,
    list_styles,
)


class TestStyleRegistry:
    def test_every_preset_has_a_definition(self):
        for style in StylePreset:
            assert style in STYLE_DEFINITIONS, f"{style} missing from STYLE_DEFINITIONS"

    def test_every_definition_has_required_keys(self):
        required = {"name", "purpose", "characteristics", "best_for", "prompt_prefix"}
        for style, definition in STYLE_DEFINITIONS.items():
            assert required <= set(definition), f"{style} missing keys"

    def test_non_custom_styles_have_nonempty_prefix(self):
        for style in StylePreset:
            if style is StylePreset.CUSTOM:
                continue
            assert get_style_prompt_prefix(style).strip(), f"{style} has empty prefix"

    def test_custom_has_empty_prefix(self):
        assert get_style_prompt_prefix(StylePreset.CUSTOM) == ""


class TestFirstPersonStyle:
    def test_enum_value(self):
        assert StylePreset.FIRST_PERSON.value == "first-person"

    def test_constructed_from_string(self):
        assert StylePreset("first-person") is StylePreset.FIRST_PERSON

    def test_prefix_encodes_pov_composition(self):
        prefix = get_style_prompt_prefix(StylePreset.FIRST_PERSON).lower()
        # Load-bearing compositional cues of the POV scenario style.
        assert "first-person" in prefix
        assert "hands" in prefix
        assert "legible" in prefix

    def test_listed_in_styles_output(self):
        assert "first-person" in list_styles()
