import pytest

from rag.config import ConfigError, Settings, load_settings


@pytest.fixture(autouse=True)
def _clean_env(monkeypatch):
    for var in ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "TOP_K", "CHROMA_PATH"):
        monkeypatch.delenv(var, raising=False)


def test_lee_key_model_y_top_k_del_entorno(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k-test")
    monkeypatch.setenv("OPENROUTER_MODEL", "algo/modelo:free")
    monkeypatch.setenv("TOP_K", "7")

    s = load_settings(env_file=None)

    assert isinstance(s, Settings)
    assert s.api_key == "k-test"
    assert s.model == "algo/modelo:free"
    assert s.top_k == 7


def test_defaults(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k-test")

    s = load_settings(env_file=None)

    assert s.top_k == 6
    assert s.chroma_path == "./chroma_db"
    assert s.collection == "gestion_talento"
    assert s.history_turns == 3
    assert s.model


def test_falta_api_key_lanza_config_error_en_espanol():
    with pytest.raises(ConfigError) as exc:
        load_settings(env_file=None)
    assert "OPENROUTER_API_KEY" in str(exc.value)
    assert "falta" in str(exc.value).lower()


def test_api_key_en_blanco_lanza_config_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "   ")
    with pytest.raises(ConfigError):
        load_settings(env_file=None)


def test_top_k_invalido_lanza_config_error(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k")
    monkeypatch.setenv("TOP_K", "abc")
    with pytest.raises(ConfigError) as exc:
        load_settings(env_file=None)
    assert "TOP_K" in str(exc.value)


def test_dotenv_no_pisa_el_entorno(monkeypatch, tmp_path):
    envfile = tmp_path / ".env"
    envfile.write_text("OPENROUTER_API_KEY=del-archivo\nTOP_K=9\n")
    monkeypatch.setenv("OPENROUTER_API_KEY", "del-entorno")
    # dotenv escribe en os.environ: registrar TOP_K para que monkeypatch lo limpie al final
    monkeypatch.setenv("TOP_K", "x")
    monkeypatch.delenv("TOP_K")

    s = load_settings(env_file=str(envfile))

    assert s.api_key == "del-entorno"
    assert s.top_k == 9


def test_chroma_path_se_puede_sobrescribir_por_entorno(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "k-test")
    monkeypatch.setenv("CHROMA_PATH", "/tmp/otro_indice")

    assert load_settings(env_file=None).chroma_path == "/tmp/otro_indice"
