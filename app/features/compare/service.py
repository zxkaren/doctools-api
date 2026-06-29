from collections.abc import Callable
from pathlib import Path
from typing import Any

from flask import url_for
from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.exceptions import FeatureNotImplementedError
from app.core.file_manager import save_uploaded_file
from app.core.responses import build_compare_payload
from app.features.compare.processors.pdf_processor import compare_files as compare_pdf_files
from app.features.compare.processors.word_processor import compare_files as compare_docx_files
from app.features.compare.processors.excel_processor import compare_files as compare_xlsx_files
from app.features.compare.validators import validate_compare_request
from app.utils.dates import get_filename_timestamp
from app.utils.filenames import build_processed_filename, build_received_filename
from app.utils.logs import log_api_success


CompareProcessor = Callable[[Path, Path, Path], dict[str, Any]]


def build_download_url(processed_filename: str) -> str:
    return url_for(
        "compare.download_processed_file",
        processed_filename=processed_filename,
        _external=True,
    )


def get_compare_processor(file_extension: str) -> CompareProcessor:
    if file_extension == "pdf":
        return compare_pdf_files

    if file_extension == "docx":
        return compare_docx_files

    if file_extension == "xlsx":
        return compare_xlsx_files

    raise FeatureNotImplementedError(
        "o servidor reconhece a requisição, mas não possui a funcionalidade necessária para atendê-la"
    )


def save_compare_files(
    original_file: FileStorage,
    modified_file: FileStorage,
    timestamp: str,
) -> tuple[Path, Path]:
    original_filename = build_received_filename(
        "original",
        original_file.filename,
        timestamp,
    )
    modified_filename = build_received_filename(
        "modified",
        modified_file.filename,
        timestamp,
    )

    original_path = save_uploaded_file(
        original_file,
        Config.COMPARE_RECEIVED_FOLDER,
        original_filename,
    )
    modified_path = save_uploaded_file(
        modified_file,
        Config.COMPARE_RECEIVED_FOLDER,
        modified_filename,
    )

    return original_path, modified_path


def build_response_data(
    response_mode: str,
    download_url: str,
    summary_table: dict[str, Any],
) -> dict[str, Any]:
    if response_mode == "download_url":
        return {
            "download_url": download_url,
        }

    if response_mode == "json":
        return {
            "summary_table": summary_table,
        }

    return build_compare_payload(download_url, summary_table)


def process_compare_request(
    original_file: FileStorage | None,
    modified_file: FileStorage | None,
    response_mode: str,
    route_extension: str | None = None,
) -> dict[str, Any]:
    """
    Resumo:
        Orquestra a comparação de documentos enviados para a API.

    Parâmetros:
        original_file (FileStorage | None): arquivo original enviado pelo usuário.
        modified_file (FileStorage | None): arquivo modificado enviado pelo usuário.
        response_mode (str): modo de retorno desejado.
        route_extension (str | None): extensão informada na rota específica.

    Retorno:
        dict[str, Any]: dados de resposta com download_url, summary_table ou ambos.
    """
    file_extension = validate_compare_request(
        original_file,
        modified_file,
        response_mode,
        route_extension,
    )

    timestamp = get_filename_timestamp(Config.TIMEZONE_NAME)

    original_path, modified_path = save_compare_files(
        original_file,
        modified_file,
        timestamp,
    )

    processed_filename = build_processed_filename(
        modified_file.filename,
        timestamp,
    )
    processed_path = Config.COMPARE_PROCESSED_FOLDER / processed_filename

    compare_processor = get_compare_processor(file_extension)
    processor_result = compare_processor(
        original_path,
        modified_path,
        processed_path,
    )

    download_url = build_download_url(processed_filename)
    summary_table = processor_result["summary_table"]

    log_api_success("comparação concluída")

    return build_response_data(
        response_mode,
        download_url,
        summary_table,
    )