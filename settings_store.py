from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

CONFIG_DIR = Path.home() / ".qlda_xaydung"
APP_SETTINGS_FILE = CONFIG_DIR / "app_settings.json"
LEGACY_GOOGLE_FILE = CONFIG_DIR / "google_search.json"

DEFAULT_SPECIFIED_SEARCH_DOMAINS = [
    "vanban.chinhphu.vn",
    "congbao.chinhphu.vn",
    "vbpl.vn",
    "moc.gov.vn",
    "tieuchuan.vsqi.gov.vn",
    "tieuchuanxaydung.vsqi.gov.vn",
    "thuvienphapluat.vn",
]

DEFAULT_SETTINGS: dict[str, Any] = {
    "google_api_key": "",
    "google_cx": "",
    "ai_provider": "openai",
    "openai_api_key": "",
    "openai_model": "gpt-5-mini",
    "gemini_api_key": "",
    "gemini_model": "gemini-2.5-flash",
    "openai_web_search": False,
    "specified_search_domains": DEFAULT_SPECIFIED_SEARCH_DOMAINS,
    "drive_enabled": False,
    "drive_auto_upload": False,
    "drive_client_credentials_path": "",
    "drive_root_folder_id": "",
    "drive_root_folder_url": "",
    "drive_root_folder_name": "QLDA Xây dựng",
}


def _clean_domains(values) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        d = str(value or "").strip().lower()
        d = d.removeprefix("https://").removeprefix("http://").split("/", 1)[0].strip()
        if d.startswith("www."):
            d = d[4:]
        if d and "." in d and d not in seen:
            seen.add(d); out.append(d)
    return out


def load_app_settings() -> dict[str, Any]:
    data = dict(DEFAULT_SETTINGS)
    data["specified_search_domains"] = list(DEFAULT_SPECIFIED_SEARCH_DOMAINS)
    if APP_SETTINGS_FILE.exists():
        try:
            saved = json.loads(APP_SETTINGS_FILE.read_text(encoding="utf-8"))
            if isinstance(saved, dict):
                data.update(saved)
        except Exception:
            pass

    # Migrate Google settings from V4.0.5/V4.0.6 without deleting the legacy file.
    if (not data.get("google_api_key") or not data.get("google_cx")) and LEGACY_GOOGLE_FILE.exists():
        try:
            legacy = json.loads(LEGACY_GOOGLE_FILE.read_text(encoding="utf-8"))
            data["google_api_key"] = data.get("google_api_key") or str(legacy.get("api_key", "")).strip()
            data["google_cx"] = data.get("google_cx") or str(legacy.get("cx", "")).strip()
        except Exception:
            pass

    data["specified_search_domains"] = _clean_domains(data.get("specified_search_domains")) or list(DEFAULT_SPECIFIED_SEARCH_DOMAINS)
    data["ai_provider"] = "gemini" if str(data.get("ai_provider") or "openai").strip().lower() == "gemini" else "openai"
    data["openai_model"] = str(data.get("openai_model") or "gpt-5-mini").strip() or "gpt-5-mini"
    data["gemini_model"] = str(data.get("gemini_model") or "gemini-2.5-flash").strip() or "gemini-2.5-flash"
    data["openai_web_search"] = bool(data.get("openai_web_search", False))
    data["drive_enabled"] = bool(data.get("drive_enabled", False))
    data["drive_auto_upload"] = bool(data.get("drive_auto_upload", False))
    data["drive_root_folder_name"] = str(data.get("drive_root_folder_name") or "QLDA Xây dựng").strip() or "QLDA Xây dựng"
    return data


def save_app_settings(settings: dict[str, Any]) -> Path:
    current = load_app_settings()
    current.update(settings or {})
    current["specified_search_domains"] = _clean_domains(current.get("specified_search_domains")) or list(DEFAULT_SPECIFIED_SEARCH_DOMAINS)
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    APP_SETTINGS_FILE.write_text(json.dumps(current, ensure_ascii=False, indent=2), encoding="utf-8")
    return APP_SETTINGS_FILE


def get_specified_search_domains() -> tuple[str, ...]:
    return tuple(load_app_settings().get("specified_search_domains") or DEFAULT_SPECIFIED_SEARCH_DOMAINS)


def get_openai_runtime_settings() -> dict[str, Any]:
    cfg = load_app_settings()
    env_web = os.environ.get("OPENAI_WEB_SEARCH")
    if env_web is None:
        use_web = bool(cfg.get("openai_web_search", False))
    else:
        use_web = env_web.strip().lower() in {"1", "true", "yes", "on"}
    return {
        "api_key": (os.environ.get("OPENAI_API_KEY") or str(cfg.get("openai_api_key", ""))).strip(),
        "model": (os.environ.get("OPENAI_MODEL") or str(cfg.get("openai_model", "gpt-5-mini"))).strip() or "gpt-5-mini",
        "use_web": use_web,
    }

def get_ai_runtime_settings() -> dict[str, Any]:
    cfg = load_app_settings()
    provider = (os.environ.get("AI_PROVIDER") or str(cfg.get("ai_provider", "openai"))).strip().lower()
    provider = "gemini" if provider == "gemini" else "openai"
    env_web = os.environ.get("AI_WEB_SEARCH")
    if env_web is None:
        env_web = os.environ.get("GEMINI_WEB_SEARCH" if provider == "gemini" else "OPENAI_WEB_SEARCH")
    use_web = bool(cfg.get("openai_web_search", False)) if env_web is None else env_web.strip().lower() in {"1", "true", "yes", "on"}
    if provider == "gemini":
        return {
            "provider": "gemini",
            "api_key": (os.environ.get("GEMINI_API_KEY") or str(cfg.get("gemini_api_key", ""))).strip(),
            "model": (os.environ.get("GEMINI_MODEL") or str(cfg.get("gemini_model", "gemini-2.5-flash"))).strip() or "gemini-2.5-flash",
            "use_web": use_web,
        }
    return {
        "provider": "openai",
        "api_key": (os.environ.get("OPENAI_API_KEY") or str(cfg.get("openai_api_key", ""))).strip(),
        "model": (os.environ.get("OPENAI_MODEL") or str(cfg.get("openai_model", "gpt-5-mini"))).strip() or "gpt-5-mini",
        "use_web": use_web,
    }

