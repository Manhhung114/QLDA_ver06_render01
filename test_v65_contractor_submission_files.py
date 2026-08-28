from pathlib import Path

APP = Path(__file__).with_name('streamlit_app.py').read_text(encoding='utf-8')


def test_rfa_rfi_contractor_has_submission_upload():
    assert '📎 Lưu & tải tệp trình duyệt' in APP
    assert '📎 Tải tệp trình duyệt lên' in APP
    assert 'submission_upload_after_save_document_' in APP


def test_shopdrawing_contractor_has_submission_upload():
    assert '📎 Tải tệp Shopdrawing trình duyệt lên' in APP
    assert 'submission_upload_after_save_drawing_' in APP


def test_reviewer_sees_files_before_approval_and_approval_requires_file():
    assert 'attachment_count=attachment_count' in APP
    assert 'Cần tải ít nhất 01 tệp trình duyệt trước khi gửi vào luồng phê duyệt.' in APP
    assert 'Không thể phê duyệt cho đến khi Nhà thầu tải tệp lên' in APP
    assert 'disabled=not has_submission_file' in APP


def test_attachment_panel_returns_file_count():
    assert 'def _render_inline_drive_attachments' in APP
    assert '-> int:' in APP
    assert 'return current_file_count' in APP
