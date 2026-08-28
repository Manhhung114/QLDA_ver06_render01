from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_gemini_provider_wired():
    service = (ROOT / 'ai_service.py').read_text(encoding='utf-8')
    app = (ROOT / 'streamlit_app.py').read_text(encoding='utf-8')
    req = (ROOT / 'requirements.txt').read_text(encoding='utf-8')
    assert 'class GeminiProjectAssistant' in service
    assert 'class GeminiSettings' in service
    assert 'GEMINI_API_KEY' in service
    assert 'google_search=types.GoogleSearch()' in service
    assert 'GeminiProjectAssistant' in app
    assert 'Nhà cung cấp AI' in app
    assert 'GEMINI_API_KEY' in app
    assert 'google-genai' in req


def test_gemini_render_env_documented():
    render = (ROOT / 'render.yaml').read_text(encoding='utf-8')
    assert 'AI_PROVIDER' in render
    assert 'GEMINI_API_KEY' in render
    assert 'GEMINI_MODEL' in render
