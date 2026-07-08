from pathlib import Path

from decouple import config


def parse_csv_config(variable_name: str) -> set[str]:
    """
    Resumo:
        Converte uma variável de ambiente em formato CSV para um conjunto de strings.

    Parâmetros:
        variable_name (str): nome da variável configurada no arquivo .env.

    Retorno:
        set[str]: conjunto com os valores tratados e sem espaços extras.
    """
    configured_value = config(variable_name)

    return {
        item.strip()
        for item in configured_value.split(",")
        if item.strip()
    }


class Config:
    PROJECT_ROOT = Path(__file__).resolve().parent.parent

    FLASK_ENV = config("FLASK_ENV")
    DEBUG = config("DEBUG", cast=bool)

    HOST = config("HOST")
    PORT = config("PORT", cast=int)

    TIMEZONE_NAME = config("TIMEZONE_NAME")

    SECRET_KEY = config("SECRET_KEY")

    MAX_CONTENT_LENGTH = config("MAX_CONTENT_LENGTH", cast=int)

    STORAGE_ROOT = PROJECT_ROOT / config("STORAGE_ROOT")

    # Compare Configuration
    COMPARE_STORAGE_FOLDER = STORAGE_ROOT / config("COMPARE_STORAGE_FOLDER")
    COMPARE_RECEIVED_FOLDER = COMPARE_STORAGE_FOLDER / config("COMPARE_RECEIVED_FOLDER")
    COMPARE_PROCESSED_FOLDER = COMPARE_STORAGE_FOLDER / config("COMPARE_PROCESSED_FOLDER")
    COMPARE_TEMP_FOLDER = COMPARE_STORAGE_FOLDER / config("COMPARE_TEMP_FOLDER")

    ALLOWED_COMPARE_EXTENSIONS = parse_csv_config("ALLOWED_COMPARE_EXTENSIONS")
    IMPLEMENTED_COMPARE_EXTENSIONS = parse_csv_config("IMPLEMENTED_COMPARE_EXTENSIONS")

    DEFAULT_COMPARE_RESPONSE_MODE = config("DEFAULT_COMPARE_RESPONSE_MODE")
    ALLOWED_COMPARE_RESPONSE_MODES = parse_csv_config("ALLOWED_COMPARE_RESPONSE_MODES")

    # Extract Configuration
    EXTRACT_TEXT_STORAGE_FOLDER = STORAGE_ROOT / config("EXTRACT_TEXT_STORAGE_FOLDER")
    EXTRACT_TEXT_RECEIVED_FOLDER = EXTRACT_TEXT_STORAGE_FOLDER / config("EXTRACT_TEXT_RECEIVED_FOLDER")
    EXTRACT_TEXT_PROCESSED_FOLDER = EXTRACT_TEXT_STORAGE_FOLDER / config("EXTRACT_TEXT_PROCESSED_FOLDER")
    EXTRACT_TEXT_TEMP_FOLDER = EXTRACT_TEXT_STORAGE_FOLDER / config("EXTRACT_TEXT_TEMP_FOLDER")

    ALLOWED_EXTRACT_TEXT_EXTENSIONS = parse_csv_config("ALLOWED_EXTRACT_TEXT_EXTENSIONS")
    DEFAULT_EXTRACT_TEXT_OUTPUT_FORMAT = config("DEFAULT_EXTRACT_TEXT_OUTPUT_FORMAT")
    ALLOWED_EXTRACT_TEXT_OUTPUT_FORMATS = parse_csv_config("ALLOWED_EXTRACT_TEXT_OUTPUT_FORMATS")

    # Split PDF Configuration
    SPLIT_PDF_STORAGE_FOLDER = STORAGE_ROOT / config("SPLIT_PDF_STORAGE_FOLDER")
    SPLIT_PDF_RECEIVED_FOLDER = SPLIT_PDF_STORAGE_FOLDER / config("SPLIT_PDF_RECEIVED_FOLDER")
    SPLIT_PDF_PROCESSED_FOLDER = SPLIT_PDF_STORAGE_FOLDER / config("SPLIT_PDF_PROCESSED_FOLDER")
    SPLIT_PDF_TEMP_FOLDER = SPLIT_PDF_STORAGE_FOLDER / config("SPLIT_PDF_TEMP_FOLDER")

    # Cleanup Configuration
    CLEANUP_FILE_MAX_AGE_HOURS = config("CLEANUP_FILE_MAX_AGE_HOURS", cast=int)
    CLEANUP_INTERVAL_MINUTES = config("CLEANUP_INTERVAL_MINUTES", cast=int)