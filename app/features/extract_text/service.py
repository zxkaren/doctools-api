import json
from collections.abc import Callable
from pathlib import Path
from typing import Any

from docx import Document
from flask import url_for
from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.file_manager import ensure_folder_exists, save_uploaded_file
from app.core.validators import get_file_extension
from app.features.extract_text.processors.pdf_processor import extract_text_from_pdf
from app.features.extract_text.processors.slides_processor import extract_text_from_slides
from app.features.extract_text.processors.text_cleaner import clean_extracted_text
from app.features.extract_text.processors.word_processor import extract_text_from_word
from app.features.extract_text.validators import validate_extract_text_request
from app.utils.dates import get_filename_timestamp
from app.utils.filenames import build_received_filename, get_filename_stem
from app.utils.logs import log_api_success


ExtractTextProcessor = Callable[[Path], str]


def build_download_url(processed_filename: str) -> str:
    return url_for(
        "extract_text.download_processed_file",
        processed_filename=processed_filename,
        _external=True,
    )


def get_extract_text_processor(file_extension: str) -> ExtractTextProcessor:
    if file_extension == "pdf":
        return extract_text_from_pdf

    if file_extension == "docx":
        return extract_text_from_word

    if file_extension == "pptx":
        return extract_text_from_slides

    raise ValueError("extensão sem processador de extração configurado")


def build_output_filename(
    original_filename: str,
    output_format: str,
    timestamp: str,
    file_position: int,
) -> str:
    filename_stem = get_filename_stem(original_filename, "extracted-text")

    return (
        f"{filename_stem}-extracted-text-"
        f"{file_position:03d}-{timestamp}.{output_format}"
    )


def save_extract_text_file(
    uploaded_file: FileStorage,
    timestamp: str,
    file_position: int,
) -> Path:
    received_filename = build_received_filename(
        f"extract-{file_position:03d}",
        uploaded_file.filename,
        timestamp,
    )

    return save_uploaded_file(
        uploaded_file,
        Config.EXTRACT_TEXT_RECEIVED_FOLDER,
        received_filename,
    )


def write_docx_output(text_content: str, output_path: Path) -> None:
    word_document = Document()

    for paragraph_text in text_content.splitlines():
        if paragraph_text.strip():
            word_document.add_paragraph(paragraph_text.strip())

    word_document.save(output_path)


def write_txt_output(text_content: str, output_path: Path) -> None:
    output_path.write_text(text_content, encoding="utf-8")


def write_json_output(
    text_content: str,
    original_filename: str,
    output_path: Path,
) -> None:
    json_content = {
        "original_filename": original_filename,
        "text": text_content,
        "characters": len(text_content),
        "words": len(text_content.split()),
    }

    output_path.write_text(
        json.dumps(json_content, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def create_output_file(
    text_content: str,
    original_filename: str,
    output_format: str,
    timestamp: str,
    file_position: int,
) -> str:
    ensure_folder_exists(Config.EXTRACT_TEXT_PROCESSED_FOLDER)

    output_filename = build_output_filename(
        original_filename,
        output_format,
        timestamp,
        file_position,
    )
    output_path = Config.EXTRACT_TEXT_PROCESSED_FOLDER / output_filename

    if output_format == "docx":
        write_docx_output(text_content, output_path)
        return output_filename

    if output_format == "txt":
        write_txt_output(text_content, output_path)
        return output_filename

    write_json_output(text_content, original_filename, output_path)

    return output_filename


def build_file_error_result(
    original_filename: str,
    error_message: str,
) -> dict[str, Any]:
    return {
        "original_filename": original_filename,
        "status": "error",
        "error": error_message,
    }


def process_single_file(
    uploaded_file: FileStorage,
    output_format: str,
    timestamp: str,
    file_position: int,
) -> dict[str, Any]:
    """
    Resumo:
        Processa um arquivo enviado, extrai o texto, limpa o conteúdo e gera
        um arquivo de saída no formato solicitado.

    Parâmetros:
        uploaded_file (FileStorage): arquivo enviado na requisição.
        output_format (str): formato de saída solicitado.
        timestamp (str): data e hora usada para nomear arquivos.
        file_position (int): posição do arquivo na requisição.

    Retorno:
        dict[str, Any]: resultado individual do arquivo processado.
    """
    original_filename = uploaded_file.filename
    file_extension = get_file_extension(original_filename)

    received_path = save_extract_text_file(
        uploaded_file,
        timestamp,
        file_position,
    )

    extract_text_processor = get_extract_text_processor(file_extension)
    raw_text_content = extract_text_processor(received_path)
    cleaned_text_content = clean_extracted_text(raw_text_content)

    if not cleaned_text_content:
        return build_file_error_result(
            original_filename,
            "nenhum texto legível foi encontrado no arquivo",
        )

    output_filename = create_output_file(
        cleaned_text_content,
        original_filename,
        output_format,
        timestamp,
        file_position,
    )

    return {
        "original_filename": original_filename,
        "status": "success",
        "output_filename": output_filename,
        "download_url": build_download_url(output_filename),
    }


def process_uploaded_files_recursively(
    uploaded_files: list[FileStorage],
    output_format: str,
    timestamp: str,
    file_position: int = 1,
) -> list[dict[str, Any]]:
    if file_position > len(uploaded_files):
        return []

    current_file = uploaded_files[file_position - 1]

    try:
        current_result = process_single_file(
            current_file,
            output_format,
            timestamp,
            file_position,
        )
    except Exception as error:
        print(f"falha. extração não concluída para {current_file.filename}: {error}")

        current_result = build_file_error_result(
            current_file.filename,
            "não foi possível extrair o texto deste arquivo",
        )

    remaining_results = process_uploaded_files_recursively(
        uploaded_files,
        output_format,
        timestamp,
        file_position + 1,
    )

    return [current_result, *remaining_results]


def build_processing_summary(
    output_format: str,
    file_results: list[dict[str, Any]],
) -> dict[str, Any]:
    processed_files = sum(
        1
        for file_result in file_results
        if file_result["status"] == "success"
    )
    failed_files = len(file_results) - processed_files

    return {
        "output_format": output_format,
        "total_files": len(file_results),
        "processed_files": processed_files,
        "failed_files": failed_files,
        "files": file_results,
    }


def process_extract_text_request(
    uploaded_files: list[FileStorage],
    output_format: str,
) -> dict[str, Any]:
    """
    Resumo:
        Orquestra a extração de texto dos arquivos enviados, garantindo a regra
        de um arquivo de entrada para um arquivo de saída.

    Parâmetros:
        uploaded_files (list[FileStorage]): arquivos enviados na requisição.
        output_format (str): formato de saída solicitado. Aceita docx, txt ou json.

    Retorno:
        dict[str, Any]: resumo do processamento e lista de arquivos gerados.
    """
    valid_uploaded_files, normalized_output_format = validate_extract_text_request(
        uploaded_files,
        output_format,
    )

    timestamp = get_filename_timestamp(Config.TIMEZONE_NAME)

    file_results = process_uploaded_files_recursively(
        valid_uploaded_files,
        normalized_output_format,
        timestamp,
    )

    processing_summary = build_processing_summary(
        normalized_output_format,
        file_results,
    )

    log_api_success("extração de texto concluída")

    return processing_summary