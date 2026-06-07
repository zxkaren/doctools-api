import os
from io import BytesIO
from pathlib import Path

import fitz
import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("TIMEZONE_NAME", "America/Sao_Paulo")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("MAX_CONTENT_LENGTH", "52428800")
os.environ.setdefault("STORAGE_ROOT", "storage")
os.environ.setdefault("COMPARE_STORAGE_FOLDER", "compare")
os.environ.setdefault("COMPARE_RECEIVED_FOLDER", "received")
os.environ.setdefault("COMPARE_PROCESSED_FOLDER", "processed")
os.environ.setdefault("COMPARE_TEMP_FOLDER", "temp")
os.environ.setdefault("ALLOWED_COMPARE_EXTENSIONS", "pdf,doc,docx,xlsx,ppt,pptx")
os.environ.setdefault("IMPLEMENTED_COMPARE_EXTENSIONS", "pdf")
os.environ.setdefault("DEFAULT_COMPARE_RESPONSE_MODE", "json_file")
os.environ.setdefault("ALLOWED_COMPARE_RESPONSE_MODES", "download_url,json,json_file")
os.environ.setdefault("CLEANUP_FILE_MAX_AGE_HOURS", "24")
os.environ.setdefault("CLEANUP_INTERVAL_MINUTES", "60")

from app import create_app
from app.config import Config


@pytest.fixture
def client(tmp_path: Path):
    Config.COMPARE_RECEIVED_FOLDER = tmp_path / "storage" / "compare" / "received"
    Config.COMPARE_PROCESSED_FOLDER = tmp_path / "storage" / "compare" / "processed"
    Config.COMPARE_TEMP_FOLDER = tmp_path / "storage" / "compare" / "temp"

    flask_app = create_app()
    flask_app.config["TESTING"] = True

    return flask_app.test_client()


def build_pdf_bytes(text: str) -> bytes:
    """
    Resumo:
        Cria um PDF em memória para uso nos testes da API.

    Parâmetros:
        text (str): texto que será inserido no PDF.

    Retorno:
        bytes: conteúdo binário do PDF gerado.
    """
    document = fitz.open()
    page = document.new_page()
    page.insert_text(fitz.Point(72, 72), text, fontsize=12)

    pdf_bytes = document.tobytes()
    document.close()

    return pdf_bytes


def test_compare_pdf_returns_download_url_and_summary_table(client) -> None:
    original_pdf = build_pdf_bytes("hello world")
    modified_pdf = build_pdf_bytes("hello brave world")

    response = client.post(
        "/compare/",
        data={
            "original": (BytesIO(original_pdf), "original.pdf"),
            "modified": (BytesIO(modified_pdf), "modified.pdf"),
            "response_mode": "json_file",
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert "download_url" in response_payload["data"]
    assert "summary_table" in response_payload["data"]
    assert response_payload["data"]["summary_table"]["add"] >= 1
    assert response_payload["data"]["summary_table"]["total_changes"] >= 1


def test_compare_pdf_without_modified_file_returns_bad_request(client) -> None:
    original_pdf = build_pdf_bytes("hello world")

    response = client.post(
        "/compare/",
        data={
            "original": (BytesIO(original_pdf), "original.pdf"),
            "response_mode": "json_file",
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()

    assert response.status_code == 400
    assert response_payload["success"] is False
    assert response_payload["error"]["message"] == "informe o arquivo modified"


def test_compare_with_different_extensions_returns_bad_request(client) -> None:
    original_pdf = build_pdf_bytes("hello world")

    response = client.post(
        "/compare/",
        data={
            "original": (BytesIO(original_pdf), "original.pdf"),
            "modified": (BytesIO(b"fake content"), "modified.docx"),
            "response_mode": "json_file",
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()

    assert response.status_code == 400
    assert response_payload["success"] is False
    assert response_payload["error"]["message"] == "os arquivos devem ter a mesma extensão"


def test_compare_specific_route_with_wrong_extension_returns_bad_request(client) -> None:
    original_pdf = build_pdf_bytes("hello world")
    modified_pdf = build_pdf_bytes("hello brave world")

    response = client.post(
        "/compare/docx",
        data={
            "original": (BytesIO(original_pdf), "original.pdf"),
            "modified": (BytesIO(modified_pdf), "modified.pdf"),
            "response_mode": "json_file",
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()

    assert response.status_code == 400
    assert response_payload["success"] is False
    assert response_payload["error"]["message"] == "essa rota só aceita a extensão selecionada"