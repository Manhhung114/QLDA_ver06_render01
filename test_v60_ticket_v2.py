from pathlib import Path

ROOT = Path(__file__).resolve().parent
GS = (ROOT / "google_drive_appscript" / "Code.gs").read_text(encoding="utf-8")
GW = (ROOT / "drive_gateway.py").read_text(encoding="utf-8")


def test_ticket_is_stateless_and_signed():
    assert "makeSignedUploadTicket_(meta)" in GS
    assert "computeHmacSha256Signature" in GS
    assert "ticket_version: 2" in GS
    assert "validateUploadTicketMeta_(meta)" in GS


def test_gateway_forwards_exact_exec_url():
    assert '"webapp_url": self.config.webapp_url' in GW
    assert "validWebAppExecUrl_(configuredBase)" in GS


def test_legacy_ticket_compatibility_kept():
    assert "Tương thích ticket V6 cũ" in GS
    assert "PropertiesService.getScriptProperties()" in GS
