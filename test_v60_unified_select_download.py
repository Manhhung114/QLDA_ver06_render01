from pathlib import Path
s = Path("streamlit_app.py").read_text(encoding="utf-8")
assert 'def _render_selected_record_downloads(' in s
assert 'def _render_selected_document_downloads(' in s
assert 'def _render_selected_drawing_downloads(' in s
assert 'doc_download_selected_state_' in s
assert 'drawing_download_selected_state_' in s
assert 'Tải hồ sơ đã chọn' in s
assert 'Tải bản vẽ đã chọn' in s
assert 'disabled_cols = [c for c in df.columns if c != "Chọn"]' in s
print('V6_UNIFIED_SELECT_DOWNLOAD_TEST_OK')
