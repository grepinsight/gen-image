"""Shared test fixtures."""

import pytest


@pytest.fixture
def tmp_config(tmp_path):
    """Create a temporary config file."""
    config_path = tmp_path / "config.toml"
    config_path.write_text("""
[general]
vault_path = "/tmp/test-vault"

[api]
provider = "gemini"
model = "gemini-3.1-flash-image-preview"
quality = "standard"
size = "1024x1024"

[costs]
warn_at_percent = 80

[output]
auto_copy_wikilink = false
""")
    return config_path


@pytest.fixture
def tmp_history(tmp_path):
    """Create a temporary history file."""
    return tmp_path / "history.jsonl"


@pytest.fixture
def sample_png(tmp_path):
    """Create a minimal valid PNG file for testing."""
    from PIL import Image

    img = Image.new("RGB", (10, 10), color="red")
    path = tmp_path / "ref.png"
    img.save(path)
    return path
