from pathlib import Path

TEXT = Path('streamlit_app.py').read_text(encoding='utf-8')

assert 'def _render_selected_drawing_downloads' in TEXT
assert '⬇️ Tải bản vẽ đã chọn' in TEXT
assert 'drawing_select_grid_' in TEXT
assert 'Tick bản vẽ cần tải xuống' in TEXT
assert 'kind="drawing"' in TEXT
assert 'include_history=False' in TEXT
assert 'https://drive.google.com/uc?export=download&id=' in TEXT
assert '🗑 Xóa bản vẽ đã chọn' in TEXT
print('V6 selected drawing download UI: OK')
