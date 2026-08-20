from __future__ import annotations

import base64
from unittest.mock import patch

from drive_gateway import DriveGateway, DriveGatewayConfig, DriveGatewayError


class Resp:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.text = str(data)
    def json(self):
        return self._data


def test_health_and_login():
    cfg = DriveGatewayConfig.from_values('https://script.google.com/macros/s/abc/exec', 'secret')
    gw = DriveGateway(cfg)
    with patch('drive_gateway.requests.post', return_value=Resp({'ok': True, 'initialized': True})) as p:
        assert gw.health()['initialized'] is True
        sent = p.call_args.kwargs['json']
        assert sent['action'] == 'health' and sent['api_token'] == 'secret'
    with patch('drive_gateway.requests.post', return_value=Resp({'ok': True, 'session_token': 'x.y', 'user': {'role': 'admin'}})):
        assert gw.login('a@b.com', 'password')['user']['role'] == 'admin'


def test_upload_base64():
    cfg = DriveGatewayConfig.from_values('https://script.google.com/macros/s/abc/exec', 'secret', max_upload_mb=1)
    gw = DriveGateway(cfg)
    with patch('drive_gateway.requests.post', return_value=Resp({'ok': True, 'file': {'id': '1', 'webViewLink': 'https://drive.google.com/x'}})) as p:
        out = gw.upload_bytes('tok', project_code='P01', kind='document', subtype='NCR', record_code='NCR-1', name='a.txt', content=b'abc', mime_type='text/plain')
        assert out['id'] == '1'
        sent = p.call_args.kwargs['json']
        assert base64.b64decode(sent['file_base64']) == b'abc'
        assert sent['session_token'] == 'tok'


def test_size_limit():
    cfg = DriveGatewayConfig.from_values('https://script.google.com/macros/s/abc/exec', 'secret', max_upload_mb=1)
    gw = DriveGateway(cfg)
    try:
        gw.upload_bytes('tok', project_code='P', kind='document', subtype='NCR', record_code='N', name='big.bin', content=b'x' * (1024 * 1024 + 1))
    except DriveGatewayError as exc:
        assert 'vượt giới hạn' in str(exc)
    else:
        raise AssertionError('expected DriveGatewayError')


if __name__ == '__main__':
    test_health_and_login(); test_upload_base64(); test_size_limit(); print('OK')
