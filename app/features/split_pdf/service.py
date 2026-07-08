from pathlib import Path
from typing import Any

from flask import url_for
from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.file_manager import ensure_folder_exists, save_uploaded_file
from app.features.split_pdf.processors.pdf_processor import (
    get_pdf_total_pages,
    split_pdf_by_packs,
    split_pdf_one_by_one,
)
from app.features.split_pdf.validators import (
    validate_pack_fields,
    validate_pages_within_pdf_range,
    validate_pdf_file,
    validate_split_type,
)
from app.utils.dates import get_filename_timestamp
from app.utils.filenames import build_received_filename
from app.utils.logs import log_api_success


def build_download_url(processed_filename: str) -> str:
    return url_for(
        "split_pdf.download_processed_file",
        processed_filename=processed_filename,
        _external=True,
    )


def save_split_pdf_file(uploaded_file: FileStorage, timestamp: str) -> Path:
    received_filename = build_received_filename(
        "split-pdf",
        uploaded_file.filename,
        timestamp,
    )

    return save_uploaded_file(
        uploaded_file,
        Config.SPLIT_PDF_RECEIVED_FOLDER,
        received_filename,
    )


def build_file_result(generated_file: dict[str, Any]) -> dict[str, Any]:
    file_result = {
        "filename": generated_file["filename"],
        "download_url": build_download_url(generated_file["filename"]),
        "pages": generated_file["pages"],
    }

    if "pack" in generated_file:
        file_result["pack"] = generated_file["pack"]

    return file_result


def build_file_results(generated_files: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [build_file_result(generated_file) for generated_file in generated_files]


def process_pdf_split(
    source_pdf_path: Path,
    original_filename: str,
    split_type: str,
    packs: dict[int, list[int]],
    timestamp: str,
) -> list[dict[str, Any]]:
    total_pages = get_pdf_total_pages(str(source_pdf_path))

    if split_type == "pack":
        validate_pages_within_pdf_range(packs, total_pages)

        return split_pdf_by_packs(
            source_pdf_path=str(source_pdf_path),
            original_filename=original_filename,
            processed_folder=str(Config.SPLIT_PDF_PROCESSED_FOLDER),
            packs=packs,
            processing_timestamp=timestamp,
        )

    return split_pdf_one_by_one(
        source_pdf_path=str(source_pdf_path),
        original_filename=original_filename,
        processed_folder=str(Config.SPLIT_PDF_PROCESSED_FOLDER),
        processing_timestamp=timestamp,
    )


def build_processing_summary(
    original_filename: str,
    split_type: str,
    generated_files: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "original_filename": original_filename,
        "split_type": split_type,
        "total_files": len(generated_files),
        "files": build_file_results(generated_files),
    }


def process_split_pdf_request(
    uploaded_files: list[FileStorage],
    split_type: str | None,
    pack_numbers: list[str],
    pack_pages_items: list[str],
) -> dict[str, Any]:
    """
    Resumo:
        Orquestra o split de um PDF recebido, permitindo separar página por página
        ou gerar pacotes personalizados com páginas selecionadas.

    Parâmetros:
        uploaded_files: lista de arquivos recebidos na requisição.
        split_type: tipo de split solicitado. Aceita one_by_one ou pack.
        pack_numbers: lista com os números dos packs informados no form-data.
        pack_pages_items: lista com as páginas de cada pack informadas no form-data.

    Retorno:
        Dicionário com resumo do processamento e arquivos gerados.
    """
    pdf_file = validate_pdf_file(uploaded_files)
    normalized_split_type = validate_split_type(split_type)
    packs = validate_pack_fields(
        split_type=normalized_split_type,
        pack_numbers=pack_numbers,
        pack_pages_items=pack_pages_items,
    )

    timestamp = get_filename_timestamp(Config.TIMEZONE_NAME)

    ensure_folder_exists(Config.SPLIT_PDF_RECEIVED_FOLDER)
    ensure_folder_exists(Config.SPLIT_PDF_PROCESSED_FOLDER)

    source_pdf_path = save_split_pdf_file(pdf_file, timestamp)

    generated_files = process_pdf_split(
        source_pdf_path=source_pdf_path,
        original_filename=pdf_file.filename,
        split_type=normalized_split_type,
        packs=packs,
        timestamp=timestamp,
    )

    processing_summary = build_processing_summary(
        original_filename=pdf_file.filename,
        split_type=normalized_split_type,
        generated_files=generated_files,
    )

    log_api_success("split pdf concluído")
    return processing_summary