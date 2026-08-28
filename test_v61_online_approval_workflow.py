from pathlib import Path
from tempfile import TemporaryDirectory

from cloud_db import CloudDatabase


def test_online_approval_return_to_reviewer_and_history():
    with TemporaryDirectory() as td:
        db = CloudDatabase(Path(td) / "qlda_test.db")
        pid = db.add_project("P01", "Dự án mẫu")
        doc_id = db.save_document(pid, "RFA", {
            "code": "RFA-001",
            "subject": "Trình duyệt vật liệu",
            "status": "Soạn thảo",
        })
        approvers = {
            "CONTRACTOR": {"email": "contractor@example.com", "name": "Nhà thầu A"},
            "SITE_MANAGEMENT": {"email": "site@example.com", "name": "Ban điều hành"},
            "CONSULTANT": {"email": "tvgs@example.com", "name": "TVGS"},
            "PROJECT_MANAGEMENT": {"email": "pm@example.com", "name": "Ban QLDA"},
        }
        wid = db.start_approval_workflow(
            pid, "document", "RFA", doc_id, "RFA-001", "contractor@example.com", approvers,
            submitted_name="Nhà thầu A",
        )

        wf = db.approval_workflow(pid, "document", "RFA", doc_id)
        assert wf["current_stage"] == "SITE_MANAGEMENT"
        assert wf["revision_no"] == 0

        db.approval_action(wid, "SITE_MANAGEMENT", "site@example.com", "APPROVE", "Đồng ý", "Ban điều hành")
        wf = db.approval_workflow(pid, "document", "RFA", doc_id)
        assert wf["current_stage"] == "CONSULTANT"

        db.approval_action(
            wid, "CONSULTANT", "tvgs@example.com", "REQUEST_REVISION", "Bổ sung catalogue", "TVGS"
        )
        wf = db.approval_workflow(pid, "document", "RFA", doc_id)
        assert wf["current_stage"] == "CONTRACTOR"
        assert wf["return_stage"] == "CONSULTANT"

        result = db.resubmit_approval_workflow(wid, "contractor@example.com", "Nhà thầu A")
        assert result["current_stage"] == "CONSULTANT"
        assert result["revision_no"] == 1
        assert result["next_email"] == "tvgs@example.com"

        steps = {r["stage_code"]: r for r in db.approval_steps(wid)}
        assert steps["SITE_MANAGEMENT"]["status"] == "Đã duyệt"
        assert steps["CONSULTANT"]["status"] == "Đang chờ duyệt"
        assert steps["PROJECT_MANAGEMENT"]["status"] == "Chờ"

        db.approval_action(wid, "CONSULTANT", "tvgs@example.com", "APPROVE", "Đạt", "TVGS")
        db.approval_action(wid, "PROJECT_MANAGEMENT", "pm@example.com", "APPROVE", "Phê duyệt", "Ban QLDA")
        wf = db.approval_workflow(pid, "document", "RFA", doc_id)
        assert wf["current_stage"] == "DONE"
        assert wf["overall_status"] == "Đã phê duyệt"

        history = db.approval_history(wid)
        actions = [h["action"] for h in history]
        assert "SUBMIT" in actions
        assert "REQUEST_REVISION" in actions
        assert "RESUBMIT" in actions
        assert "COMPLETE" in actions


if __name__ == "__main__":
    test_online_approval_return_to_reviewer_and_history()
    print("OK - online approval workflow v2")
