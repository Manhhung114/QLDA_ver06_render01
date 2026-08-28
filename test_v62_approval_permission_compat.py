from drive_gateway import DriveGateway, DriveGatewayConfig


class CaptureGateway(DriveGateway):
    def __init__(self):
        super().__init__(DriveGatewayConfig('https://script.google.com/macros/s/test/exec', 'token'))
        self.calls = []

    def _post(self, action, payload=None, session_token=''):
        self.calls.append((action, dict(payload or {}), session_token))
        return {'ok': True, 'user': dict(payload or {})}


def test_dual_approval_fields_for_legacy_backend():
    gw = CaptureGateway()
    cases = [
        ('', 'none'),
        ('CONTRACTOR', 'contractor'),
        ('SITE_MANAGEMENT', 'site_management'),
        ('CONSULTANT', 'tvgs'),
        ('PROJECT_MANAGEMENT', 'bqlda'),
    ]
    for new_role, legacy_group in cases:
        gw.set_user('session', 'a@example.com', 'A', 'update', '', new_role)
        _, payload, _ = gw.calls[-1]
        assert payload['approval_role'] == new_role
        assert payload['approval_group'] == legacy_group


def test_admin_defaults_to_project_management_bqlda():
    gw = CaptureGateway()
    gw.set_user('session', 'admin@example.com', 'Admin', 'admin', '', '')
    _, payload, _ = gw.calls[-1]
    assert payload['approval_role'] == 'PROJECT_MANAGEMENT'
    assert payload['approval_group'] == 'bqlda'
