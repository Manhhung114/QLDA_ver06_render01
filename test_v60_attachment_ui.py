from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_v60_streamlit_inline_attachment_ui():
    text = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")
    assert "QLDA Xây dựng V6.0" in text
    assert 'st.form_submit_button("📎 Đính kèm file"' in text
    assert '"💾 Cập nhật" if selected else "💾 Lưu mới"' in text
    assert "components.iframe" in text
    assert "🗑 Xóa file đã chọn" in text
    assert "⬇️ Tải xuống" in text
    for doc in ["NCR", "RFA", "RFI", "VO", "NTCV", "NTVL", "KDVT"]:
        assert f'"{doc}"' in text
    for drawing in ["SHOPDRAWING", "ISSUED_DESIGN", "UPDATED", "AS_BUILT"]:
        assert f'"{drawing}"' in text


def test_v60_apps_script_embed_and_rbac():
    text = (ROOT / "google_drive_appscript" / "Code.gs").read_text(encoding="utf-8")
    assert "version: '6.0'" in text
    assert "HtmlService.XFrameOptionsMode.ALLOWALL" in text
    assert "input.addEventListener('change'" in text
    assert "requireRole_(body, ['admin'])" in text
    assert "MAX_DIRECT_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024" in text
