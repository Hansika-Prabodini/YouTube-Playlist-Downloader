import os
import io
import logging
from contextlib import redirect_stderr

import pytest

from utils.secrets import get_openai_api_key


@pytest.fixture(autouse=True)
def _isolate_env_and_cwd(monkeypatch, tmp_path):
    # Ensure tests don't accidentally read a real .env in repo root by running in tmp cwd
    monkeypatch.chdir(tmp_path)
    # Clear any OPENAI_API_KEY from the environment by default; individual tests may set it
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)


def write_dotenv(tmp_path, value: str):
    (tmp_path / ".env").write_text(f"OPENAI_API_KEY={value}\n", encoding="utf-8")


def test_env_var_takes_precedence_over_dotenv(monkeypatch, tmp_path):
    # Arrange: .env has a different value, but env var should win
    write_dotenv(tmp_path, "sk-dotenv-XXXXXXXX")
    monkeypatch.setenv("OPENAI_API_KEY", "sk-env-ABCDEFGH")

    # Act
    key = get_openai_api_key()

    # Assert
    assert key == "sk-env-ABCDEFGH"


def test_loads_from_dotenv_when_env_missing(tmp_path):
    # Arrange: ensure no env var and create .env in temp cwd
    write_dotenv(tmp_path, "sk-dotenv-ABCDEFGH")

    # Act
    key = get_openai_api_key()

    # Assert
    assert key == "sk-dotenv-ABCDEFGH"


def test_raises_when_missing_and_required(tmp_path):
    # Arrange: ensure neither env var nor .env exists in CWD
    # No .env written and env var unset via autouse fixture

    # Act / Assert
    with pytest.raises(EnvironmentError) as excinfo:
        get_openai_api_key(required=True)

    # The message should be non-sensitive and should not leak any key
    msg = str(excinfo.value)
    assert "OPENAI_API_KEY" in msg
    assert "sk-" not in msg
