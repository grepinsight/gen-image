"""Tests for configuration management."""

import os

from gen_image.config import Config, ConfigManager, config_dir, load_config_env


class TestConfigDefaults:
    def test_default_provider_is_gemini(self):
        config = Config()
        assert config.api.provider == "gemini"

    def test_default_model(self):
        config = Config()
        assert config.api.model == "gemini-3.1-flash-image-preview"

    def test_default_quality(self):
        config = Config()
        assert config.api.quality == "standard"

    def test_default_budget_is_none(self):
        config = Config()
        assert config.costs.budget_limit is None

    def test_default_auto_copy(self):
        config = Config()
        assert config.output.auto_copy_wikilink is True


class TestConfigManager:
    def test_load_returns_defaults_when_no_file(self, tmp_path):
        mgr = ConfigManager(config_path=tmp_path / "nonexistent.toml")
        config = mgr.load()
        assert config.api.provider == "gemini"

    def test_load_from_file(self, tmp_config):
        mgr = ConfigManager(config_path=tmp_config)
        config = mgr.load()
        assert config.api.provider == "gemini"
        assert config.output.auto_copy_wikilink is False

    def test_save_and_reload(self, tmp_path):
        path = tmp_path / "config.toml"
        mgr = ConfigManager(config_path=path)

        config = Config()
        config.api.provider = "openai"
        config.api.model = "gpt-image-2"
        mgr.save(config)

        reloaded = mgr.load()
        assert reloaded.api.provider == "openai"
        assert reloaded.api.model == "gpt-image-2"

    def test_create_default_creates_file(self, tmp_path):
        path = tmp_path / "config.toml"
        mgr = ConfigManager(config_path=path)
        mgr.create_default()
        assert path.exists()
        config = mgr.load()
        assert config.api.provider == "gemini"


class TestLoadConfigEnv:
    def _write_env(self, tmp_path, monkeypatch, contents):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        env_dir = tmp_path / "gen-image"
        env_dir.mkdir(parents=True, exist_ok=True)
        (env_dir / ".env").write_text(contents)
        return env_dir

    def test_loads_key_into_environ(self, tmp_path, monkeypatch):
        self._write_env(tmp_path, monkeypatch, "GEMINI_API_KEY=from-file\n")
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        load_config_env()
        assert os.environ["GEMINI_API_KEY"] == "from-file"

    def test_existing_environ_wins(self, tmp_path, monkeypatch):
        self._write_env(tmp_path, monkeypatch, "GEMINI_API_KEY=from-file\n")
        monkeypatch.setenv("GEMINI_API_KEY", "from-shell")
        load_config_env()
        assert os.environ["GEMINI_API_KEY"] == "from-shell"

    def test_handles_export_prefix_and_quotes(self, tmp_path, monkeypatch):
        self._write_env(tmp_path, monkeypatch, 'export GOOGLE_API_KEY="quoted-val"\n')
        monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
        load_config_env()
        assert os.environ["GOOGLE_API_KEY"] == "quoted-val"

    def test_skips_comments_and_blanks(self, tmp_path, monkeypatch):
        self._write_env(tmp_path, monkeypatch, "# a comment\n\nOPENAI_API_KEY=ok\n")
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)
        load_config_env()
        assert os.environ["OPENAI_API_KEY"] == "ok"

    def test_no_file_is_noop(self, tmp_path, monkeypatch):
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path))
        # No gen-image/.env created.
        load_config_env()  # must not raise
        assert config_dir() == tmp_path / "gen-image"
