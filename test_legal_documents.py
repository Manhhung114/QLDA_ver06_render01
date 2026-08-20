from pathlib import Path
import tempfile
from legal_documents import LegalRepository

p = Path(tempfile.gettempdir()) / "qlda_v37_legal_test.db"
p.unlink(missing_ok=True)
repo = LegalRepository(p)
stats = repo.upsert_many([
    {
        "category": "Nghị định", "number": "TEST/2026/NĐ-CP", "title": "Quản lý dự án đầu tư xây dựng",
        "issuer": "Chính phủ", "issue_date": "2026-01-01", "effective_date": "2026-02-01",
        "expiry_date": "", "status": "Còn hiệu lực", "field": "QLDA xây dựng",
        "source_name": "TEST", "source_url": "https://example.invalid/test-nd", "is_draft": 0, "note": ""
    },
    {
        "category": "TCVN", "number": "TCVN TEST:2026", "title": "Kết cấu xây dựng - thử nghiệm",
        "issuer": "Bộ Khoa học và Công nghệ", "issue_date": "2026-01-01", "effective_date": "",
        "expiry_date": "", "status": "A - Còn hiệu lực (Active)", "field": "Tiêu chuẩn xây dựng",
        "source_name": "TEST", "source_url": "https://example.invalid/test-tcvn", "is_draft": 0, "note": ""
    }
])
assert stats["added"] == 2
assert len(repo.list_documents()) == 2
assert len(repo.list_documents(category="TCVN")) == 1
print("LEGAL_REPOSITORY_TEST_OK")
