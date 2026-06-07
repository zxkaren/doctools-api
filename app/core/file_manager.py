from pathlib import Path

from werkzeug.datastructures import FileStorage
from werkzeug.utils import secure_filename

from app.core.exceptions import BadRequestError


def ensure_folder_exists(folder_path: Path) -> None:
    folder_path.mkdir(parents=True, exist_ok=True)


def sanitize_filename(filename: str) -> str:
    safe_filename = secure_filename(filename)

    if not safe_filename:
        raise BadRequestError("nome do arquivo inválido")

    return safe_filename


def save_uploaded_file(
    uploaded_file: FileStorage,
    target_folder: Path,
    target_filename: str,
) -> Path:
    ensure_folder_exists(target_folder)

    safe_filename = sanitize_filename(target_filename)
    target_path = target_folder / safe_filename

    uploaded_file.save(target_path)

    return target_path


def delete_file(file_path: Path) -> None:
    if file_path.exists() and file_path.is_file() and file_path.name != ".gitkeep":
        file_path.unlink()