"""Testes para modules/upload.py"""

import os
import tempfile
from unittest.mock import patch, Mock
from modules.upload import upload_para_url_publica, _upload_0x0


def test_upload_file_not_found():
    result = upload_para_url_publica("/nonexistent/file.png")
    assert result is None


def test_upload_0x0_success():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake image data")
        tmp = f.name

    try:
        with patch("modules.upload.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "https://0x0.st/abc123"
            mock_post.return_value = mock_response

            url = _upload_0x0(tmp, "test.png")
            assert url == "https://0x0.st/abc123"
    finally:
        os.unlink(tmp)


def test_upload_0x0_failure():
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        f.write(b"fake")
        tmp = f.name

    try:
        with patch("modules.upload.requests.post") as mock_post:
            mock_response = Mock()
            mock_response.status_code = 500
            mock_post.return_value = mock_response

            url = _upload_0x0(tmp, "test.png")
            assert url is None
    finally:
        os.unlink(tmp)
