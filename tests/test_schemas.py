import pytest

from app.schemas import VersionSchema


def test_version_schema_valid():
    data = {"python": "3.11.7", "mermaidCli": "11.6.0", "mermaidService": "1.0.0", "timestamp": "2025-03-25T14:00:00Z"}

    result = VersionSchema(**data)

    assert result.python == data["python"]
    assert result.mermaidCli == data["mermaidCli"]
    assert result.mermaidService == data["mermaidService"]
    assert result.timestamp == data["timestamp"]


def test_version_schema_missing_required():
    data = {"mermaidCli": "11.6.0"}

    with pytest.raises(Exception) as excinfo:
        VersionSchema(**data)

    assert "python" in str(excinfo.value)
