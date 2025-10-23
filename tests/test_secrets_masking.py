import logging

from utils.secrets import mask_secret


def test_mask_secret_default_behavior():
    # Default behavior should show only last 4 chars
    assert mask_secret("sk-12345678") == "*****5678"


def test_mask_secret_short_secret():
    # When secret length <= show, it should be fully masked
    assert mask_secret("abcd", show=4) == "****"


def test_logging_uses_masked_value_only(caplog):
    caplog.set_level(logging.INFO)
    logger = logging.getLogger("secrets-test")

    key = "sk-LEAKME1234"
    logger.info("Using key %s", mask_secret(key))

    # Assert masked appears
    assert any("LEAKME1234"[-4:] in rec.message for rec in caplog.records)
    assert any("*****" in rec.message for rec in caplog.records)

    # Assert raw value does NOT appear
    for rec in caplog.records:
        assert "sk-LEAKME1234" not in rec.message
