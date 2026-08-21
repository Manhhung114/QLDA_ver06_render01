from pathlib import Path

ROOT = Path(__file__).resolve().parent


def test_streamlit_tower_code_and_filters():
    s = (ROOT / "streamlit_app.py").read_text(encoding="utf-8")
    assert '"BBHT"' in s
    assert 'doc_types = ["NCR", "RFA", "RFI", "BBHT", "NTCV", "NTVL", "KDVT"]' in s
    assert 'doc_types = ["NCR", "RFA", "RFI", "VO"' not in s
    assert 'placeholder="S2-MEP-001"' in s
    assert 'Mã phải theo định dạng THÁP-BỘMÔN-STT' in s
    assert 'filter_tower' in s and 'filter_discipline' in s and 'filter_file' in s
    assert '"Tháp": tower' in s
    assert '"Ghi chú": r["note"]' not in s


def test_apps_script_tower_folder_and_legacy_compatibility():
    s = (ROOT / "google_drive_appscript" / "Code.gs").read_text(encoding="utf-8")
    assert "return 'Tháp ' + first;" in s
    assert 'usesTowerFolder_' in s
    assert 'findLegacyRecordFolderFromBody_' in s
    assert 'tower_name: towerFolderNameFromRecordCode_' in s
    assert "meta.tower_name" in s
