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

os.environ.setdefault("CLEANUP_FILE_MAX_AGE_HOURS", "24")
os.environ.setdefault("CLEANUP_INTERVAL_MINUTES", "60")


from app import create_app
from app.config import Config


@pytest.fixture
def client(monkeypatch, tmp_path: Path):
    configure_split_pdf_storage(monkeypatch, tmp_path)

    flask_app = create_app()
    flask_app.config.update(TESTING=True)

    with flask_app.test_client() as test_client:
        yield test_client


def configure_split_pdf_storage(monkeypatch, temporary_path: Path) -> None:
    """
    Resumo:
        Redireciona o storage da feature split_pdf para uma pasta temporária
        durante os testes automatizados.

    Parâmetros:
        monkeypatch: fixture do pytest usada para alterar atributos em tempo de teste.
        temporary_path: pasta temporária criada pelo pytest.

    Retorno:
        None.
    """
    received_folder = temporary_path / "storage" / "split_pdf" / "received"
    processed_folder = temporary_path / "storage" / "split_pdf" / "processed"
    temp_folder = temporary_path / "storage" / "split_pdf" / "temp"

    monkeypatch.setattr(Config, "SPLIT_PDF_RECEIVED_FOLDER", received_folder)
    monkeypatch.setattr(Config, "SPLIT_PDF_PROCESSED_FOLDER", processed_folder)
    monkeypatch.setattr(Config, "SPLIT_PDF_TEMP_FOLDER", temp_folder)


def create_pdf_bytes(page_texts: list[str]) -> BytesIO:
    """
    Resumo:
        Cria um PDF em memória com uma página para cada texto informado.

    Parâmetros:
        page_texts: lista de textos que serão inseridos nas páginas do PDF.

    Retorno:
        BytesIO com o conteúdo binário do PDF gerado.
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
    """
    Resumo:
        Conta a quantidade de páginas de um arquivo PDF salvo em disco.

    Parâmetros:
        pdf_path: caminho do arquivo PDF que será analisado.

    Retorno:
        Quantidade de páginas do PDF.
    """
    with fitz.open(str(pdf_path)) as pdf_document:
        return pdf_document.page_count


def get_download_path(download_url: str) -> str:
    parsed_url = urlparse(download_url)
    return parsed_url.path


def test_split_pdf_one_by_one_generates_one_file_per_page(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "one_by_one",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2", "Página 3"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert response_data["split_type"] == "one_by_one"
    assert response_data["total_files"] == 3

    expected_pages = [[1], [2], [3]]
    generated_pages = [file_result["pages"] for file_result in response_data["files"]]

    assert generated_pages == expected_pages

    for file_result in response_data["files"]:
        output_path = Config.SPLIT_PDF_PROCESSED_FOLDER / file_result["filename"]

        assert output_path.exists()
        assert output_path.suffix == ".pdf"
        assert count_pdf_pages(output_path) == 1


def test_split_pdf_pack_accepts_page_range(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "pack",
            "pack": "1",
            "pages": "1-3",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2", "Página 3", "Página 4"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]
    file_result = response_data["files"][0]
    output_path = Config.SPLIT_PDF_PROCESSED_FOLDER / file_result["filename"]

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert response_data["split_type"] == "pack"
    assert response_data["total_files"] == 1
    assert file_result["pack"] == 1
    assert file_result["pages"] == [1, 2, 3]
    assert output_path.exists()
    assert count_pdf_pages(output_path) == 3


def test_split_pdf_pack_accepts_repeated_form_fields(client) -> None:
    response = client.post(
        "/split/pdf/",
        data=MultiDict(
            [
                ("split_type", "pack"),
                ("pack", "1"),
                ("pages", "1-2"),
                ("pack", "2"),
                ("pages", "3-4"),
                (
                    "file",
                    (
                        create_pdf_bytes(["Página 1", "Página 2", "Página 3", "Página 4"]),
                        "documento.pdf",
                    ),
                ),
            ]
        ),
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert response_data["total_files"] == 2
    assert response_data["files"][0]["pack"] == 1
    assert response_data["files"][0]["pages"] == [1, 2]
    assert response_data["files"][1]["pack"] == 2
    assert response_data["files"][1]["pages"] == [3, 4]


def test_split_pdf_pack_accepts_swagger_style_fields(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "pack",
            "pack": "1,2",
            "pages": "1-2;3-4",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2", "Página 3", "Página 4"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    response_payload = response.get_json()
    response_data = response_payload["data"]

    assert response.status_code == 200
    assert response_payload["success"] is True
    assert response_data["total_files"] == 2
    assert response_data["files"][0]["pages"] == [1, 2]
    assert response_data["files"][1]["pages"] == [3, 4]


def test_split_pdf_download_generated_file(client) -> None:
    split_response = client.post(
        "/split/pdf/",
        data={
            "split_type": "pack",
            "pack": "1",
            "pages": "1-2",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    split_payload = split_response.get_json()
    download_url = split_payload["data"]["files"][0]["download_url"]

    download_response = client.get(get_download_path(download_url))

    assert split_response.status_code == 200
    assert download_response.status_code == 200
    assert download_response.mimetype == "application/pdf"


def test_split_pdf_rejects_more_than_one_pdf(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "one_by_one",
            "file": [
                (create_pdf_bytes(["PDF 1"]), "documento_1.pdf"),
                (create_pdf_bytes(["PDF 2"]), "documento_2.pdf"),
            ],
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_split_pdf_rejects_invalid_extension(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "one_by_one",
            "file": (BytesIO(b"conteudo invalido"), "documento.txt"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_split_pdf_pack_rejects_missing_pages(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "pack",
            "pack": "1",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_split_pdf_pack_rejects_page_outside_pdf_range(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "pack",
            "pack": "1",
            "pages": "1-5",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400


def test_split_pdf_pack_rejects_repeated_page(client) -> None:
    response = client.post(
        "/split/pdf/",
        data={
            "split_type": "pack",
            "pack": "1",
            "pages": "1,1",
            "file": (
                create_pdf_bytes(["Página 1", "Página 2"]),
                "documento.pdf",
            ),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 400