from pathlib import Path
from tempfile import TemporaryDirectory
from datetime import date

from cloud_db import CloudDatabase
from legal_documents import LegalRepository
from ai_service import AISettings, AIServiceError, OpenAIProjectAssistant, ProjectContextBuilder

with TemporaryDirectory() as td:
    db_path = Path(td) / "test.db"
    db = CloudDatabase(db_path)
    pid = db.add_project("AI-01", "Dự án test AI", "2026-01-01", "2026-12-31", "PM", "")
    tid = db.add_task(pid, dict(
        wbs="1.1", name="Thi công hệ thống điện", responsible="NT",
        start_date="2026-07-01", end_date="2026-08-01", duration=32,
        planned_progress=100, actual_progress=60, predecessor="", note=""
    ))
    with db.connect() as c:
        c.execute("UPDATE tasks SET critical=1,total_slack=0 WHERE id=?", (tid,))
    did = db.save_document(pid, "RFI", dict(
        code="RFI-001", subject="Làm rõ tủ điện", discipline="MEP", contractor="NT",
        issuer="NT", assignee="TVGS", issue_date="2026-07-01", due_date="2026-07-10",
        closed_date="", status="Chờ phản hồi", priority="Cao", related_wbs="1.1",
        description="", response="", cost_impact=0, time_impact_days=3,
    ))
    db.add_document_attachments(did, [("rfi.txt", "text/plain", b"noi dung rfi")])
    db.save_drawing(pid, "SHOPDRAWING", dict(
        drawing_no="SD-01", title="Tủ điện", discipline="Điện", revision="01", issuer="NT",
        receiver="BQL", received_date="2026-07-02", issue_date="2026-07-01", status="Cần sửa",
        related_wbs="1.1", reference_no="", note=""
    ))
    legal = LegalRepository(db_path)
    legal.upsert_many([dict(
        category="Nghị định", number="TEST-01", title="Văn bản test quản lý chất lượng",
        issuer="CP", issue_date="2026-01-01", effective_date="2026-02-01", expiry_date="",
        status="Còn hiệu lực", field="Xây dựng", source_name="test",
        source_url="https://example.invalid/test-legal", is_draft=0, note="", online_updated_at="2026-08-16"
    )])

    ctx = ProjectContextBuilder(db_path)
    snap = ctx.build(pid, "quản lý chất lượng", date(2026, 8, 16))
    for marker in ("[TASK:", "[DOC:", "[DRAWING:", "[LEGAL:"):
        assert marker in snap, marker
    files = ctx.attachment_catalog(pid)
    assert files
    assert ctx.load_attachment(files[0]["id"])[2] == b"noi dung rfi"

    ai = OpenAIProjectAssistant(db_path, AISettings(api_key="", model="gpt-5-mini"))
    try:
        ai.test_connection()
        raise AssertionError("Expected missing API key")
    except AIServiceError as exc:
        assert "OPENAI_API_KEY" in str(exc)

print("AI_CONTEXT_TEST_OK")
