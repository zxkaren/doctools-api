from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.exceptions import BadRequestError


OCR_LANGUAGE_MAP = {
    "pt_br": "por",
    "pt_pt": "por",
    "en_us": "eng",
    "es_es": "spa",
}


def validate_pdf_files(uploaded_files: list[FileStorage]) -> list[FileStorage]:
    valid_uploaded_files = [
        uploaded_file
        for uploaded_file in uploaded_files
        if uploaded_file and uploaded_file.filename
    ]

    if not valid_uploaded_files:
        raise BadRequestError("envie ao menos 1 arquivo PDF para aplicar OCR")

    for uploaded_file in valid_uploaded_files:
        if not uploaded_file.filename.lower().endswith(".pdf"):
            raise BadRequestError("a funcionalidade OCR aceita somente arquivos PDF")

    return valid_uploaded_files


def validate_ocr_mode(ocr_mode: str | None) -> str:
    normalized_ocr_mode = (ocr_mode or Config.DEFAULT_OCR_MODE).strip().lower()

    if normalized_ocr_mode not in Config.ALLOWED_OCR_MODES:
        allowed_modes_text = ", ".join(Config.ALLOWED_OCR_MODES)
        raise BadRequestError(
            f"modo OCR inválido. modos aceitos: {allowed_modes_text}"
        )

    return normalized_ocr_mode


def validate_ocr_language(ocr_language: str | None) -> tuple[str, str]:
    normalized_ocr_language = (ocr_language or Config.DEFAULT_OCR_LANGUAGE).strip().lower()

    if normalized_ocr_language not in Config.ALLOWED_OCR_LANGUAGES:
        allowed_languages_text = ", ".join(Config.ALLOWED_OCR_LANGUAGES)
        raise BadRequestError(
            f"idioma OCR inválido. idiomas aceitos: {allowed_languages_text}"
        )

    return normalized_ocr_language, OCR_LANGUAGE_MAP[normalized_ocr_language]


def validate_ocr_quality(ocr_quality: str | None) -> str:
    normalized_ocr_quality = (ocr_quality or Config.DEFAULT_OCR_QUALITY).strip().lower()

    if normalized_ocr_quality not in Config.ALLOWED_OCR_QUALITIES:
        allowed_qualities_text = ", ".join(Config.ALLOWED_OCR_QUALITIES)
        raise BadRequestError(
            f"qualidade OCR inválida. qualidades aceitas: {allowed_qualities_text}"
        )

    return normalized_ocr_quality