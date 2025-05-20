from document_generator.config.settings import Settings


def test_settings_defaults(monkeypatch):
    # Should pick up environment override
    monkeypatch.setenv("MODEL_NAME", "test-model")
    s = Settings()
    assert s.model_name == "test-model"
