from pathlib import Path
text = Path('streamlit_app.py').read_text(encoding='utf-8')
assert '📷 Mở camera' in text
assert '✖ Đóng camera' in text
assert 'camera_state_key' in text
assert 'if camera_is_open:' in text
assert 'camera_photo = None' in text
assert 'st.camera_input(' in text
print('V6 camera button test: OK')
