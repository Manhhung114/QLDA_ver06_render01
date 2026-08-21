from pathlib import Path

text = Path('streamlit_app.py').read_text(encoding='utf-8')
assert 'def render_site_diary' in text
assert 'st.camera_input(' in text
assert 'Tiến độ thực tế (%)' in text
assert 'Tình trạng vật tư' in text
assert 'Sự cố / Trở ngại' in text
assert '📷 Nhật ký công trường' in text
assert '🔎 Lọc file cần xem' in text
assert 'def _drive_preview_url' in text
assert 'c2.link_button("👁 Xem"' in text
assert 'st.caption(' not in text
assert '.caption(' not in text
print('V6_FIELD_DIARY_MOBILE_TEST_OK')
