"""Tests for utility functions."""

from gen_image.utils import extract_topic_from_prompt, get_unique_filename


class TestExtractTopicFromPrompt:
    def test_simple_prompt(self):
        result = extract_topic_from_prompt("A red fox in a forest")
        assert result == "red-fox-forest"

    def test_strips_style_markers(self):
        result = extract_topic_from_prompt("[Style: cartoon] A dancing cat")
        assert "style" not in result.lower()

    def test_strips_generate_prefix(self):
        result = extract_topic_from_prompt("Create a beautiful sunset")
        assert "create" not in result.lower()

    def test_limits_to_max_words(self):
        result = extract_topic_from_prompt("one two three four five", max_words=2)
        assert result == "one-two"

    def test_empty_prompt_returns_image(self):
        result = extract_topic_from_prompt("")
        assert result == "image"

    def test_truncates_long_slug(self):
        long_prompt = " ".join([f"word{i}" for i in range(100)])
        result = extract_topic_from_prompt(long_prompt)
        assert len(result) <= 50


class TestGetUniqueFilename:
    def test_returns_original_if_no_conflict(self, tmp_path):
        path = tmp_path / "test.png"
        assert get_unique_filename(path) == path

    def test_increments_on_conflict(self, tmp_path):
        path = tmp_path / "test.png"
        path.touch()
        result = get_unique_filename(path)
        assert result == tmp_path / "test-1.png"

    def test_increments_multiple(self, tmp_path):
        for name in ["test.png", "test-1.png", "test-2.png"]:
            (tmp_path / name).touch()
        result = get_unique_filename(tmp_path / "test.png")
        assert result == tmp_path / "test-3.png"
