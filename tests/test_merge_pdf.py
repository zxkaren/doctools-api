import os
from io import BytesIO
from pathlib import Path
from urllib.parse import urlparse

import fitz
import pytest
from werkzeug.datastructures import MultiDict


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
os.environ.setdefault("ALLOWED_COMPARE_EXTENSIONS", "pdf,docx,xlsx,pptx")
os.environ.setdefault("IMPLEMENTED_COMPARE_EXTENSIONS", "pdf,docx,xlsx,pptx")
os.environ.setdefault("DEFAULT_COMPARE_RESPONSE_MODE", "json_file")
os.environ.setdefault("ALLOWED_COMPARE_RESPONSE_MODES", "download_url,json,json_file")

os.environ.setdefault("EXTRACT_TEXT_STORAGE_FOLDER", "extract_text")
os.environ.setdefault("EXTRACT_TEXT_RECEIVED_FOLDER", "received")
os.environ.setdefault("EXTRACT_TEXT_PROCESSED_FOLDER", "processed")
os.environ.setdefault("EXTRACT_TEXT_TEMP_FOLDER", "temp")
os.environ.setdefault("ALLOWED_EXTRACT_TEXT_EXTENSIONS", "pdf,docx,pptx")
os.environ.setdefault("DEFAULT_EXTRACT_TEXT_OUTPUT_FORMAT", "docx")
os.environ.setdefault("ALLOWED_EXTRACT_TEXT_OUTPUT_FORMATS", "docx,txt,json")

os.environ.setdefault("SPLIT_PDF_STORAGE_FOLDER", "split_pdf")
os.environ.setdefault("SPLIT_PDF_RECEIVED_FOLDER", "received")
os.environ.setdefault("SPLIT_PDF_PROCESSED_FOLDER", "processed")
os.environ.setdefault("SPLIT_PDF_TEMP_FOLDER", "temp")

os.environ.setdefault("MERGE_PDF_STORAGE_FOLDER", "merge_pdf")
os.environ.setdefault("MERGE_PDF_RECEIVED_FOLDER", "received")
os.environ.setdefault("MERGE_PDF_PROCESSED_FOLDER", "processed")
os.environ.setdefault("MERGE_PDF_TEMP_FOLDER", "temp")

os.environ.setdefault("CLEANUP_FILE_MAX_AGE_HOURS", "24")
os.environ.setdefault("CLEANUP_INTERVAL_MINUTES", "60")


from app import create_app
from app.config import Config


@pytest.fixture
def client(monkeypatch, tmp_path: Path):
    configure_merge_pdf_storage(monkeypatch, tmp_path)

    flask_app = create_app()
    flask_app.config.update(TESTING=True)

    with flask_app.test_client() as test_client:
        yield test_client


def configure_merge_pdf_storage(monkeypatch, temporary_path: Path) -> None:
    """
    Resumo:
    Redireciona o storage da feature merge_pdf para uma pasta temporária nos testes.

    Parâmetros:
    monkeypatch: fixture do pytest usada para alterar atributos em tempo de teste.
    temporary_path: pasta temporária criada pelo pytest.

    Retorno:
    None.
    """
    received_folder = temporary_path / "storage" / "merge_pdf" / "received"
    processed_folder = temporary_path / "storage" / "merge_pdf" / "processed"
    temp_folder = temporary_path / "storage" / "merge_pdf" / "temp"

    monkeypatch.setattr(Config, "MERGE_PDF_RECEIVED_FOLDER", received_folder)
    monkeypatch.setattr(Config, "MERGE_PDF_PROCESSED_FOLDER", processed_folder)
    monkeypatch.setattr(Config, "MERGE_PDF_TEMP_FOLDER", temp_folder)


def create_pdf_bytes(page_texts: list[str]) -> BytesIO:
    """
    Resumo:
    Cria um PDF em memória com uma página para cada texto informado.

    Parâmetros:
    page_texts: textos que serão inseridos nas páginas do PDF.

    Retorno:
    BytesIO com o PDF gerado.
    """
    pdf_document = fitz.open()

    for page_text in page_texts:
        pdf_page = pdf_document.new_page()
        pdf_page.insert_text((72, 72), page_text)

    pdf_bytes = BytesIO(pdf_document.tobytes())
    pdf_document.close()
    pdf_bytes.seek(0)

    return pdf_bytes


def count_pdf_pages(pdf_path: Path) -> int:
    with fitz.open(str(pdf_path)) as pdf_document:
        return pdf_document.page_count


def extract_pdf_page_texts(pdf_path: Path) -> list[str]:
    with fitz.open(str(pdf_path)) as pdf_document:
        return [
            " ".join(pdf_page.get_text().split())
            for pdf_page in pdf_document
        ]


def get_download_path(download_url: str) -> str:
    parsed_url = urlparse(download_url)
    return parsed_url.path


def test_merge_pdf_uses_uploaded_file_order(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data={
            "file": [
                (
                    create_pdf_bytes(["Primeiro PDF - Página 1", "Primeiro PDF - Página 2"]),
                    "primeiro.pdf",
                ),
                (
                    create_pdf_bytes(["Segundo PDF - Página 1"]),
                    "segundo.pdf",
                ),
            ],
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]
    output_path = Config.MERGE_PDF_PROCESSED_FOLDER / response_data["filename"]

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert response_data["total_files"] == 2
    assert response_data["total_pages"] == 3
    assert output_path.exists()
    assert output_path.suffix == ".pdf"
    assert count_pdf_pages(output_path) == 3

    assert response_data["merged_documents"][0]["filename"] == "primeiro.pdf"
    assert response_data["merged_documents"][1]["filename"] == "segundo.pdf"

    assert extract_pdf_page_texts(output_path) == [
        "Primeiro PDF - Página 1",
        "Primeiro PDF - Página 2",
        "Segundo PDF - Página 1",
    ]


def test_merge_pdf_respects_csv_order(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data={
            "order": "3,1,2",
            "file": [
                (create_pdf_bytes(["Arquivo 1"]), "primeiro.pdf"),
                (create_pdf_bytes(["Arquivo 2"]), "segundo.pdf"),
                (create_pdf_bytes(["Arquivo 3"]), "terceiro.pdf"),
            ],
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]
    output_path = Config.MERGE_PDF_PROCESSED_FOLDER / response_data["filename"]

    assert response.status_code == 200
    assert response_payload["success"] is True

    assert [
        document_result["filename"]
        for document_result in response_data["merged_documents"]
    ] == [
        "terceiro.pdf",
        "primeiro.pdf",
        "segundo.pdf",
    ]

    assert extract_pdf_page_texts(output_path) == [
        "Arquivo 3",
        "Arquivo 1",
        "Arquivo 2",
    ]


def test_merge_pdf_respects_repeated_order_fields(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data=MultiDict(
            [
                ("order", "2"),
                ("order", "1"),
                ("file", (create_pdf_bytes(["Arquivo 1"]), "primeiro.pdf")),
                ("file", (create_pdf_bytes(["Arquivo 2"]), "segundo.pdf")),
            ]
        ),
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]
    output_path = Config.MERGE_PDF_PROCESSED_FOLDER / response_data["filename"]

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert extract_pdf_page_texts(output_path) == ["Arquivo 2", "Arquivo 1"]


def test_merge_pdf_download_generated_file(client) -> None:
    merge_response = client.post(
        "/merge/pdf/",
        data={
            "file": [
                (create_pdf_bytes(["Arquivo 1"]), "primeiro.pdf"),
                (create_pdf_bytes(["Arquivo 2"]), "segundo.pdf"),
            ],
        },
        content_type="multipart/form-data",
    )

    merge_payload = merge_response.get_json()
    download_url = merge_payload["data"]["download_url"]

    download_response = client.get(get_download_path(download_url))

    assert merge_response.status_code == 200
    assert download_response.status_code == 200
    assert download_response.mimetype == "application/pdf"


def test_merge_pdf_rejects_less_than_two_files(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data={
            "file": (create_pdf_bytes(["Arquivo único"]), "unico.pdf"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_merge_pdf_rejects_invalid_extension(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data={
            "file": [
                (create_pdf_bytes(["Arquivo 1"]), "primeiro.pdf"),
                (BytesIO(b"conteudo invalido"), "segundo.txt"),
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_merge_pdf_rejects_incomplete_order(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data={
            "order": "2,1",
            "file": [
                (create_pdf_bytes(["Arquivo 1"]), "primeiro.pdf"),
                (create_pdf_bytes(["Arquivo 2"]), "segundo.pdf"),
                (create_pdf_bytes(["Arquivo 3"]), "terceiro.pdf"),
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_merge_pdf_rejects_repeated_order_position(client) -> None:
    response = client.post(
        "/merge/pdf/",
        data={
            "order": "1,1",
            "file": [
                (create_pdf_bytes(["Arquivo 1"]), "primeiro.pdf"),
                (create_pdf_bytes(["Arquivo 2"]), "segundo.pdf"),
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400