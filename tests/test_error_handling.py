"""Tests for error handling in generators."""

from unittest.mock import patch

from gen_image.gemini_generator import GeminiGenerator
from gen_image.generator import ImageGenerator


class TestOpenAIErrorHandling:
    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handle_error_rate_limit(self):
        gen = ImageGenerator(api_key="test-key")
        err = gen._handle_error(Exception("rate_limit exceeded"))
        assert isinstance(err, RuntimeError)
        assert "rate limit" in str(err).lower()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handle_error_content_policy(self):
        gen = ImageGenerator(api_key="test-key")
        err = gen._handle_error(Exception("content_policy violation"))
        assert isinstance(err, RuntimeError)
        assert "content policy" in str(err).lower()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handle_error_empty_message(self):
        gen = ImageGenerator(api_key="test-key")
        err = gen._handle_error(Exception(""))
        assert isinstance(err, RuntimeError)
        msg = str(err)
        assert msg  # must be non-empty
        assert "no details" in msg.lower()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handle_error_invalid_key(self):
        gen = ImageGenerator(api_key="test-key")
        err = gen._handle_error(Exception("Invalid API key provided"))
        assert "invalid" in str(err).lower()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handle_error_safety_filter(self):
        gen = ImageGenerator(api_key="test-key")
        err = gen._handle_error(Exception("safety system triggered"))
        assert "content policy" in str(err).lower()

    @patch.dict("os.environ", {"OPENAI_API_KEY": "test-key"})
    def test_handle_error_generic(self):
        gen = ImageGenerator(api_key="test-key")
        err = gen._handle_error(Exception("something unexpected"))
        assert "something unexpected" in str(err)


class TestGeminiErrorHandling:
    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_handle_error_quota(self):
        gen = GeminiGenerator(api_key="test-key")
        err = gen._handle_error(Exception("quota exceeded"))
        assert isinstance(err, RuntimeError)
        assert "quota" in str(err).lower()

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_handle_error_safety_blocked(self):
        gen = GeminiGenerator(api_key="test-key")
        err = gen._handle_error(Exception("response blocked by safety"))
        assert "safety" in str(err).lower()

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_handle_error_empty_message(self):
        gen = GeminiGenerator(api_key="test-key")
        err = gen._handle_error(Exception(""))
        msg = str(err)
        assert msg  # non-empty
        assert "no details" in msg.lower()

    @patch.dict("os.environ", {"GEMINI_API_KEY": "test-key"})
    def test_handle_error_generic(self):
        gen = GeminiGenerator(api_key="test-key")
        err = gen._handle_error(Exception("network timeout"))
        assert "network timeout" in str(err)
