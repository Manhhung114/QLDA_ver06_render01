from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_streamlit_update_cannot_delete_files():
    s = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")
    assert 'disabled=not _is_admin()' in s
    assert '🗑 Xóa file đã chọn' in s
    assert 'Quyền Cập nhật/Chỉ đọc không được xóa file' in s
    assert 'legacy_doc_tick_' in s
    assert 'legacy_drawing_tick_' in s


def test_appsscript_server_blocks_update_delete():
    s = (ROOT / "google_drive_appscript" / "Code.gs").read_text(encoding="utf-8")
    trash = s[s.index('function trashFile_'):s.index('// -----------------------------------------------------------------------------\n// HTML DIRECT UPLOADER')]
    assert "requireRole_(body, ['admin'])" in trash
    apply = s[s.index('function applyDriveRole_'):s.index('function revokeDriveRole_')]
    assert "if (role === 'admin') root.addEditor(email);" in apply
    assert "else root.addViewer(email);" in apply


def test_update_still_can_upload():
    s = (ROOT / "google_drive_appscript" / "Code.gs").read_text(encoding="utf-8")
    create = s[s.index('function createUploadTicket_'):s.index('function readUploadTicket_')]
    assert "requireRole_(body, ['update', 'admin'])" in create
