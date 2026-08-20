from pathlib import Path
import tempfile
import settings_store as ss

with tempfile.TemporaryDirectory() as td:
    ss.APP_SETTINGS_FILE = Path(td) / "app_settings.json"
    ss.LEGACY_GOOGLE_FILE = Path(td) / "legacy.json"
    ss.save_app_settings({
        "openai_model": "gpt-5-mini",
        "google_api_key": "abc",
        "google_cx": "cx1",
        "specified_search_domains": ["https://www.thuvienphapluat.vn/a", "vbpl.vn", "vbpl.vn"],
    })
    cfg = ss.load_app_settings()
    assert cfg["google_api_key"] == "abc"
    assert cfg["specified_search_domains"] == ["thuvienphapluat.vn", "vbpl.vn"]
print("SETTINGS_STORE_TEST_OK")
