import os
import platform

from fastapi.testclient import TestClient
from unittest.mock import MagicMock, mock_open, patch

from app.mermaid_controller import app

test_script_path = "./tests/scripts/test_mmdc.sh"


def test_version():
    os.environ["MERMAID_SERVICE_VERSION"] = "test1"
    os.environ["MERMAID_SERVICE_BUILD_TIMESTAMP"] = "test2"
    with TestClient(app) as test_client:
        version = test_client.get("/version").json()

        assert version["python"] == platform.python_version()
        assert version["mermaidCli"] is not None
        assert version["mermaidService"] == "test1"
        assert version["timestamp"] == "test2"


def test_convert():
    os.environ["MMDC"] = test_script_path
    os.environ["MERMAID_SERVICE_VERSION"] = "test1"
    with (
        patch("subprocess.run") as mock_subprocess,
        patch("pathlib.Path.open", create=True) as mock_path_open,
        TestClient(app) as test_client
    ):
        mock_file = MagicMock()
        mock_file.read.return_value = b"circle cx=\"50\" cy=\"50\" r=\"40\""
        mock_path_open.return_value.__enter__.return_value = mock_file
        mock_subprocess.return_value = MagicMock()

        result = test_client.post(
            "/convert"
        )
        assert result.status_code == 400
        assert b"Empty request body" in result.content

        result = test_client.post(
            "/convert",
            content=b'flowchart TD; A-->B;',
        )
        assert result.status_code == 200
        assert b"circle cx=\"50\" cy=\"50\" r=\"40\"" in result.content


def test_convert_with_styling():
    os.environ["MMDC"] = test_script_path
    os.environ["MERMAID_SERVICE_VERSION"] = "test1"
    with (
        patch("subprocess.run") as mock_subprocess,
        patch("pathlib.Path.open", create=True) as mock_path_open,
        TestClient(app) as test_client
    ):
        mock_file = MagicMock()
        mock_file.read.return_value = b"circle cx=\"50\" cy=\"50\" r=\"40\""
        mock_path_open.return_value.__enter__.return_value = mock_file
        mock_subprocess.return_value = MagicMock()

        result = test_client.post(
            "/convert-with-styling",
            data={},
        )
        assert result.status_code == 400
        assert b"'mmd' and 'css' multipart form data should be strings" in result.content

        result = test_client.post(
            "/convert-with-styling",
            data={
                "mmd": b"sequenceDiagram; participant Participant 3; actor Aktor 4; Participant 3->>Aktor 4: message"
            }
        )
        assert result.status_code == 200
        assert b"circle cx=\"50\" cy=\"50\" r=\"40\"" in result.content
