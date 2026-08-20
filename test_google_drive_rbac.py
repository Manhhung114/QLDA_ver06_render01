from google_drive_service import extract_drive_id, app_role_from_drive_role

assert extract_drive_id('https://drive.google.com/drive/folders/ABC_def-123') == 'ABC_def-123'
assert extract_drive_id('https://drive.google.com/open?id=XYZ_123456789') == 'XYZ_123456789'
assert app_role_from_drive_role('reader') == 'read'
assert app_role_from_drive_role('writer') == 'update'
assert app_role_from_drive_role('fileOrganizer') == 'update'
assert app_role_from_drive_role('organizer') == 'admin'
assert app_role_from_drive_role('owner') == 'admin'
print('Google Drive RBAC helpers: OK')
