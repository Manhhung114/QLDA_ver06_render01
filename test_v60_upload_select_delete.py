from pathlib import Path
s = Path("streamlit_app.py").read_text(encoding="utf-8")
g = Path("drive_gateway.py").read_text(encoding="utf-8")
js = Path("google_drive_appscript/Code.gs").read_text(encoding="utf-8")
assert s.count('st.form_submit_button("⬆️ Tải lên"') >= 2
assert 'CheckboxColumn(' in s and '"☑ Chọn"' in s
assert 'Tải bản vẽ đã chọn' in s
assert 'Tải hồ sơ đã chọn' in s
assert 'Xóa bản vẽ đã chọn' in s
assert 'Xóa hồ sơ đã chọn' in s
assert s.count('CheckboxColumn(') >= 2
assert '✅ Có file (' in s
assert 'Hoàn tất & cập nhật File DB' in s
assert 'def record_file_counts(' in g
assert "case 'record_file_counts'" in js
assert 'function recordFileCounts_' in js
assert '<button id="start">⬆ Tải lên</button>' in js
assert "input.addEventListener('change'" in js
assert 'startSelectedFiles();}});' not in js
print('V6_UPLOAD_SELECT_DELETE_TEST_OK')
