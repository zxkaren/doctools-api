from pathlib import Path
from typing import Any

from flask import url_for
from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.file_manager import ensure_folder_exists, save_uploaded_file
from app.features.merge_pdf.processors.pdf_processor import merge_pdf_files
from app.features.merge_pdf.validators import validate_merge_order, validate_pdf_files
from app.utils.dates import get_filename_timestamp
from app.utils.filenames import build_received_filename
from app.utils.logs import log_api_success


def build_download_url(processed_filename: str) -> str:
    return url_for(
        "merge_pdf.download_processed_file",
        processed_filename=processed_filename,
        _external=True,
    )


def build_merged_pdf_filename(timestamp: str) -> str:
    return f"merged-pdf-{timestamp}.pdf"


def save_merge_pdf_file(
    uploaded_file: FileStorage,
    timestamp: str,
    file_order: int,
) -> Path:
    received_filename = build_received_filename(
        f"merge-pdf-{file_order}",
        uploaded_file.filename,
        timestamp,
    )

    return save_uploaded_file(
        uploaded_file,
        Config.MERGE_PDF_RECEIVED_FOLDER,
        received_filename,
    )


def save_ordered_pdf_files(
    ordered_uploaded_files: list[FileStorage],
    timestamp: str,
) -> list[dict[str, str]]:
    saved_pdf_files: list[dict[str, str]] = []

    for file_order, uploaded_file in enumerate(ordered_uploaded_files, start=1):
        saved_file_path = save_merge_pdf_file(
            uploaded_file=uploaded_file,
            timestamp=timestamp,
            file_order=file_order,
        )

        saved_pdf_files.append(
            {
                "original_filename": uploaded_file.filename,
                "file_path": str(saved_file_path),
            }
        )

    return saved_pdf_files


def build_processing_summary(merged_file: dict[str, Any]) -> dict[str, Any]:
    return {
        "filename": merged_file["filename"],
        "download_url": build_download_url(merged_file["filename"]),
        "total_files": merged_file["total_files"],
        "total_pages": merged_file["total_pages"],
        "merged_documents": merged_file["merged_documents"],
    }


def process_merge_pdf_request(
    uploaded_files: list[FileStorage],
    order_items: list[str],
) -> dict[str, Any]:
    """
    Resumo:
    Orquestra o merge de múltiplos PDFs, respeitando a ordem opcional enviada.

    Parâmetros:
    uploaded_files: lista de arquivos PDF recebidos na requisição.
    order_items: lista opcional com a ordem dos arquivos para o merge.

    Retorno:
    Dicionário com resumo do processamento e URL para download do PDF unificado.
    """
    valid_uploaded_files = validate_pdf_files(uploaded_files)
    ordered_uploaded_files = validate_merge_order(valid_uploaded_files, order_items)

    timestamp = get_filename_timestamp(Config.TIMEZONE_NAME)

    ensure_folder_exists(Config.MERGE_PDF_RECEIVED_FOLDER)
    ensure_folder_exists(Config.MERGE_PDF_PROCESSED_FOLDER)

    saved_pdf_files = save_ordered_pdf_files(
        ordered_uploaded_files=ordered_uploaded_files,
        timestamp=timestamp,
    )

    merged_file = merge_pdf_files(
        ordered_pdf_files=saved_pdf_files,
        processed_folder=str(Config.MERGE_PDF_PROCESSED_FOLDER),
        output_filename=build_merged_pdf_filename(timestamp),
    )

    processing_summary = build_processing_summary(merged_file)

    log_api_success("merge pdf concluído")

    return processing_summary