from pathlib import Path

from werkzeug.utils import secure_filename

from app.core.validators import get_file_extension


def get_filename_stem(filename: str, fallback_name: str) -> str:
    filename_stem = Path(filename).stem.strip()
    safe_filename_stem = secure_filename(filename_stem)

    if safe_filename_stem:
        return safe_filename_stem

    return fallback_name


def build_received_filename(file_label: str, filename: str, timestamp: str) -> str:
    file_extension = get_file_extension(filename)
    filename_stem = get_filename_stem(filename, file_label)

    return f"{file_label}-{filename_stem}-{timestamp}.{file_extension}"


def build_processed_filename(filename: str, timestamp: str) -> str:
    file_extension = get_file_extension(filename)
    filename_stem = get_filename_stem(filename, "compared")

    return f"{filename_stem}-compared-{timestamp}.{file_extension}"