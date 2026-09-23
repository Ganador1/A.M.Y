import os
from pathlib import Path
from app.config.config_loader import get_config, load_config_section, reload_section, _CACHE  # type: ignore

def setup_module(module):
    cfg_dir = Path("config")
    cfg_dir.mkdir(exist_ok=True)
    (cfg_dir / "sample.yaml").write_text("""
value: 42
nested:
  key: abc
""", encoding="utf-8")
    (cfg_dir / "sample.test.yaml").write_text("""
value: 100
nested:
  extra: yes
""", encoding="utf-8")
    os.environ["ATLAS_ENV"] = "test"
    # Limpia cache entre tests
    _CACHE.clear()  # type: ignore

def teardown_module(module):
    # Limpieza mínima
    pass

def test_basic_load_and_env_override():
    section = load_config_section("sample")
    assert section["value"] == 100  # override por sample.test.yaml
    assert section["nested"]["key"] == "abc"
    assert section["nested"]["extra"] == "yes"

def test_get_config_path():
    assert get_config("sample.nested.key") == "abc"
    assert get_config("sample.nested.missing", default=123) == 123

def test_reload_section():
    before = load_config_section("sample")
    assert before["value"] == 100
    # Modificar archivo override y recargar
    Path("config/sample.test.yaml").write_text("value: 200\n", encoding="utf-8")
    reloaded = reload_section("sample")
    assert reloaded["value"] == 200
