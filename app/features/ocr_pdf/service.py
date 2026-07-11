from pathlib import Path

from flask import url_for
from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.file_manager import ensure_folder_exists, save_uploaded_file
from app.features.ocr_pdf.processors.pdf_processor import apply_ocr_to_pdf
from app.features.ocr_pdf.validators import (
    validate_ocr_language,
    validate_ocr_mode,
    validate_ocr_quality,
    validate_pdf_files,
)
from app.utils.dates import get_filename_timestamp
from app.utils.filenames import build_received_filename, get_filename_stem
from app.utils.logs import log_api_success


def build_download_url(processed_filename: str) -> str:
    return url_for(
        "ocr_pdf.download_processed_file",
        processed_filename=processed_filename,
        _external=True,
    )


def process_ocr_pdf_request(
    uploaded_files: list[FileStorage],
    ocr_mode: str | None,
    ocr_language: str | None,
    ocr_quality: str | None = None,
) -> dict[str, object]:
    """
    Resumo:
        Orquestra a aplicação de OCR em um ou mais arquivos PDF.

    Parâmetros:
        uploaded_files: lista de arquivos PDF recebidos na requisição.
        ocr_mode: modo de OCR solicitado. Aceita apply ou force.
        ocr_language: idioma amigável solicitado pela API.
        ocr_quality: perfil de qualidade solicitado. Aceita standard, enhanced ou aggressive.

    Retorno:
        Dicionário com resumo do processamento e URLs para download.
    """
    valid_uploaded_files = validate_pdf_files(uploaded_files)
    validated_ocr_mode = validate_ocr_mode(ocr_mode)
    validated_ocr_language, tesseract_language = validate_ocr_language(ocr_language)
    validated_ocr_quality = validate_ocr_quality(ocr_quality)

    timestamp = get_filename_timestamp(Config.TIMEZONE_NAME)

    ensure_folder_exists(Config.OCR_PDF_RECEIVED_FOLDER)
    ensure_folder_exists(Config.OCR_PDF_PROCESSED_FOLDER)

    processed_files: list[dict[str, str]] = []

    for file_order, uploaded_file in enumerate(valid_uploaded_files, start=1):
        file_label = f"ocr-pdf-{file_order}"
        original_filename = uploaded_file.filename
        filename_stem = get_filename_stem(original_filename, file_label)

        received_filename = build_received_filename(
            file_label,
            original_filename,
            timestamp,
        )

        processed_filename = f"{file_label}-{filename_stem}-{timestamp}.pdf"

        source_pdf_path = save_uploaded_file(
            uploaded_file,
            Config.OCR_PDF_RECEIVED_FOLDER,
            received_filename,
        )

        processed_pdf_path = apply_ocr_to_pdf(
            source_pdf_path=source_pdf_path,
            target_pdf_path=Path(Config.OCR_PDF_PROCESSED_FOLDER) / processed_filename,
            ocr_mode=validated_ocr_mode,
            tesseract_language=tesseract_language,
            ocr_quality=validated_ocr_quality,
        )

        processed_files.append(
            {
                "original_filename": original_filename,
                "filename": processed_pdf_path.name,
                "download_url": build_download_url(processed_pdf_path.name),
            }
        )

    log_api_success("ocr pdf concluído")

    return {
        "message": "OCR aplicado com sucesso",
        "mode": validated_ocr_mode,
        "language": validated_ocr_language,
        "tesseract_language": tesseract_language,
        "quality": validated_ocr_quality,
        "total_files": len(processed_files),
        "files": processed_files,
    }