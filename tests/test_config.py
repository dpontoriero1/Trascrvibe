import pytest

from app.config import Settings


def test_defaults():
    s = Settings.from_env(env={})
    assert s.default_provider == "faster-whisper"
    assert s.default_model == "base"
    assert s.default_language == "auto"
    assert s.upload_dir == s.data_dir / "uploads"
    assert s.db_path.name == "trascrvibe.sqlite"
    assert s.max_upload_mb == 5120


def test_env_overrides():
    env = {
        "TRSV_DEFAULT_MODEL": "small",
        "TRSV_LANGUAGE": "en",
        "TRSV_MAX_UPLOAD_MB": "10",
        "TRSV_DEFAULT_PROVIDER": "demo",
        "TRSV_DATA_DIR": "altre_data",
    }
    s = Settings.from_env(env)
    assert s.default_model == "small"
    assert s.default_language == "en"
    assert s.max_upload_mb == 10
    assert s.default_provider == "demo"
    assert s.data_dir.name == "altre_data"


def test_invalid_model_rejected():
    with pytest.raises(ValueError):
        Settings.from_env(env={"TRSV_DEFAULT_MODEL": "gigante"})


def test_invalid_provider_rejected():
    with pytest.raises(ValueError):
        Settings.from_env(env={"TRSV_DEFAULT_PROVIDER": "cloud"})
