from unittest.mock import Mock, patch

from drive_gateway import DriveGateway, DriveGatewayConfig


def test_v50_defaults():
    cfg = DriveGatewayConfig.from_values('https://script.google.com/macros/s/abc/exec', 'secret')
    assert cfg.direct_max_upload_mb == 2048
    assert cfg.legacy_max_upload_mb == 30


def test_create_upload_ticket_payload():
    cfg = DriveGatewayConfig.from_values('https://script.google.com/macros/s/abc/exec', 'secret')
    gw = DriveGateway(cfg)
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        'ok': True,
        'upload': {'url': 'https://script.google.com/macros/s/x/exec?mode=upload&ticket=t', 'max_bytes': 2147483648},
    }
    with patch('requests.post', return_value=response) as post:
        out = gw.create_upload_ticket('sess', project_code='P01', kind='drawing', subtype='UPDATED', record_code='MEP-01')
    assert out['max_bytes'] == 2147483648
    body = post.call_args.kwargs['json']
    assert body['action'] == 'create_upload_ticket'
    assert body['max_bytes'] == 2048 * 1024 * 1024
    assert body['project_code'] == 'P01'


def test_list_record_files():
    cfg = DriveGatewayConfig.from_values('https://script.google.com/macros/s/abc/exec', 'secret')
    gw = DriveGateway(cfg)
    response = Mock()
    response.status_code = 200
    response.json.return_value = {
        'ok': True,
        'folder': {'url': 'https://drive.google.com/drive/folders/1'},
        'files': [{'id': 'f1', 'name': 'a.zip', 'size': 100}],
    }
    with patch('requests.post', return_value=response):
        out = gw.list_record_files('sess', project_code='P', kind='document', subtype='NCR', record_code='NCR-1')
    assert out['files'][0]['name'] == 'a.zip'


if __name__ == '__main__':
    test_v50_defaults()
    test_create_upload_ticket_payload()
    test_list_record_files()
    print('OK')
