from pathlib import Path

code = (Path(__file__).parent / 'google_drive_appscript' / 'Code.gs').read_text(encoding='utf-8')
assert "MAX_DIRECT_UPLOAD_BYTES = 2 * 1024 * 1024 * 1024" in code
assert "RECOMMENDED_CHUNK_BYTES = 2 * 1024 * 1024" in code
assert "function startResumableUpload" in code
assert "function uploadChunk" in code
assert "function queryResumableUpload" in code
assert "Authorization: 'Bearer ' + ScriptApp.getOAuthToken()" in code
assert "PropertiesService.getScriptProperties()" in code
assert "create_upload_ticket" in code
assert "list_record_files" in code
print('V5.0 Apps Script static: OK')
