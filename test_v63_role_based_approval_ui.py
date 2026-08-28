from pathlib import Path

APP = Path(__file__).with_name('streamlit_app.py').read_text(encoding='utf-8')


def test_rfa_rfi_use_role_based_ui():
    assert 'if doc_type in APPROVAL_ELIGIBLE_DOCS:' in APP
    assert 'return _render_approval_document_type(pid, doc_type)' in APP


def test_contractor_fields_are_limited():
    start = APP.index('def _render_approval_document_type')
    end = APP.index('def render_document_type', start)
    block = APP[start:end]
    for label in [
        'Bộ môn / Hệ', 'Nhà thầu / Đơn vị', 'Mức độ', 'Mô tả',
        '💾 Lưu hồ sơ', '📤 Tải file lên lưu', '📝 Mở / xử lý hồ sơ'
    ]:
        assert label in block
    # Những trường cũ không còn là input trực tiếp trong form RFA/RFI.
    assert 'st.text_input(cfg.get("assignee_label"' not in block
    assert 'st.checkbox("Đã có ngày đóng"' not in block
    assert 'st.text_input("WBS / Task liên quan"' not in block
    assert 'st.text_area(cfg.get("response_label"' not in block
    assert 'st.text_area("Ghi chú"' not in block


def test_reviewer_has_approval_result_table_and_strict_roles():
    assert '#### 📝 Ý kiến / Kết quả phê duyệt' in APP
    assert '"Ý kiến / Kết quả phê duyệt"' in APP
    assert 'contractor_ok = approval_role == "CONTRACTOR"' in APP
    assert 'current_stage == "CONTRACTOR" and approval_role == "CONTRACTOR"' in APP
