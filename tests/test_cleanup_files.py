import os
from collections.abc import Callable
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

import pytest

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("TIMEZONE_NAME", "UTC")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("MAX_CONTENT_LENGTH", "52428800")
os.environ.setdefault("STORAGE_ROOT", "storage")

os.environ.setdefault("COMPARE_STORAGE_FOLDER", "compare")
os.environ.setdefault("COMPARE_RECEIVED_FOLDER", "received")
os.environ.setdefault("COMPARE_PROCESSED_FOLDER", "processed")
os.environ.setdefault("COMPARE_TEMP_FOLDER", "temp")

os.environ.setdefault("EXTRACT_TEXT_STORAGE_FOLDER", "extract_text")
os.environ.setdefault("EXTRACT_TEXT_RECEIVED_FOLDER", "received")
os.environ.setdefault("EXTRACT_TEXT_PROCESSED_FOLDER", "processed")
os.environ.setdefault("EXTRACT_TEXT_TEMP_FOLDER", "temp")

os.environ.setdefault("SPLIT_PDF_STORAGE_FOLDER", "split_pdf")
os.environ.setdefault("SPLIT_PDF_RECEIVED_FOLDER", "received")
os.environ.setdefault("SPLIT_PDF_PROCESSED_FOLDER", "processed")
os.environ.setdefault("SPLIT_PDF_TEMP_FOLDER", "temp")

os.environ.setdefault("MERGE_PDF_STORAGE_FOLDER", "merge_pdf")
os.environ.setdefault("MERGE_PDF_RECEIVED_FOLDER", "received")
os.environ.setdefault("MERGE_PDF_PROCESSED_FOLDER", "processed")
os.environ.setdefault("MERGE_PDF_TEMP_FOLDER", "temp")

os.environ.setdefault("OCR_PDF_STORAGE_FOLDER", "ocr_pdf")
os.environ.setdefault("OCR_PDF_RECEIVED_FOLDER", "received")
os.environ.setdefault("OCR_PDF_PROCESSED_FOLDER", "processed")
os.environ.setdefault("OCR_PDF_TEMP_FOLDER", "temp")

os.environ.setdefault("ALLOWED_COMPARE_EXTENSIONS", "pdf,docx,xlsx,pptx")
os.environ.setdefault("IMPLEMENTED_COMPARE_EXTENSIONS", "pdf,docx,xlsx")
os.environ.setdefault("DEFAULT_COMPARE_RESPONSE_MODE", "json_file")
os.environ.setdefault(
    "ALLOWED_COMPARE_RESPONSE_MODES",
    "download_url,json,json_file",
)
os.environ.setdefault("CLEANUP_FILE_MAX_AGE_HOURS", "24")
os.environ.setdefault("CLEANUP_INTERVAL_MINUTES", "60")

from app.config import Config
from app.jobs import cleanup_files as cleanup_files_module


CleanupFunction = Callable[[], int]


def create_file_with_modified_datetime(
    file_path: Path,
    modified_datetime: datetime,
) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("conteúdo de teste", encoding="utf-8")

    modified_timestamp = modified_datetime.timestamp()
    os.utime(file_path, (modified_timestamp, modified_timestamp))


def create_cleanup_stub(
    removed_files_count: int,
) -> CleanupFunction:
    """
    Resumo:
    Cria uma função simulada que retorna uma quantidade fixa de arquivos
    removidos.

    Parâmetros:
    removed_files_count: quantidade que a função simulada deverá retornar.

    Retorno:
    CleanupFunction: função simulada de limpeza.
    """

    def cleanup_stub() -> int:
        return removed_files_count

    return cleanup_stub


@pytest.mark.parametrize(
    (
        "feature_name",
        "received_folder_attribute",
        "processed_folder_attribute",
        "temp_folder_attribute",
        "cleanup_function",
    ),
    [
        (
            "compare",
            "COMPARE_RECEIVED_FOLDER",
            "COMPARE_PROCESSED_FOLDER",
            "COMPARE_TEMP_FOLDER",
            cleanup_files_module.cleanup_compare_files,
        ),
        (
            "extract_text",
            "EXTRACT_TEXT_RECEIVED_FOLDER",
            "EXTRACT_TEXT_PROCESSED_FOLDER",
            "EXTRACT_TEXT_TEMP_FOLDER",
            cleanup_files_module.cleanup_extract_text_files,
        ),
        (
            "split_pdf",
            "SPLIT_PDF_RECEIVED_FOLDER",
            "SPLIT_PDF_PROCESSED_FOLDER",
            "SPLIT_PDF_TEMP_FOLDER",
            cleanup_files_module.cleanup_split_pdf_files,
        ),
        (
            "merge_pdf",
            "MERGE_PDF_RECEIVED_FOLDER",
            "MERGE_PDF_PROCESSED_FOLDER",
            "MERGE_PDF_TEMP_FOLDER",
            cleanup_files_module.cleanup_merge_pdf_files,
        ),
        (
            "ocr_pdf",
            "OCR_PDF_RECEIVED_FOLDER",
            "OCR_PDF_PROCESSED_FOLDER",
            "OCR_PDF_TEMP_FOLDER",
            cleanup_files_module.cleanup_ocr_pdf_files,
        ),
    ],
)
def test_cleanup_feature_files_removes_only_expired_files(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    feature_name: str,
    received_folder_attribute: str,
    processed_folder_attribute: str,
    temp_folder_attribute: str,
    cleanup_function: CleanupFunction,
) -> None:
    feature_storage_folder = tmp_path / "storage" / feature_name
    received_folder = feature_storage_folder / "received"
    processed_folder = feature_storage_folder / "processed"
    temp_folder = feature_storage_folder / "temp"

    monkeypatch.setattr(
        Config,
        received_folder_attribute,
        received_folder,
    )
    monkeypatch.setattr(
        Config,
        processed_folder_attribute,
        processed_folder,
    )
    monkeypatch.setattr(
        Config,
        temp_folder_attribute,
        temp_folder,
    )
    monkeypatch.setattr(
        Config,
        "CLEANUP_FILE_MAX_AGE_HOURS",
        24,
    )

    timezone = ZoneInfo(Config.TIMEZONE_NAME)
    current_datetime = datetime.now(timezone)

    expired_file = received_folder / "expired.pdf"
    current_file = processed_folder / "current.pdf"
    preserved_file = temp_folder / ".gitkeep"

    create_file_with_modified_datetime(
        expired_file,
        current_datetime - timedelta(hours=48),
    )
    create_file_with_modified_datetime(
        current_file,
        current_datetime,
    )
    create_file_with_modified_datetime(
        preserved_file,
        current_datetime - timedelta(hours=48),
    )

    removed_files_count = cleanup_function()

    assert removed_files_count == 1
    assert not expired_file.exists()
    assert current_file.exists()
    assert preserved_file.exists()


def test_cleanup_all_feature_files_returns_total_removed_files(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    cleanup_results = {
        "cleanup_compare_files": 1,
        "cleanup_extract_text_files": 2,
        "cleanup_split_pdf_files": 3,
        "cleanup_merge_pdf_files": 4,
        "cleanup_ocr_pdf_files": 5,
    }

    for cleanup_function_name, removed_files_count in cleanup_results.items():
        monkeypatch.setattr(
            cleanup_files_module,
            cleanup_function_name,
            create_cleanup_stub(removed_files_count),
        )

    total_removed_files = cleanup_files_module.cleanup_all_feature_files()

    assert total_removed_files == 15