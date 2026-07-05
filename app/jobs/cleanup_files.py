import logging
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from app.config import Config
from app.core.file_manager import delete_file
from app.utils.dates import get_file_expiration_limit


def is_preserved_file(file_path: Path) -> bool:
    return file_path.name == ".gitkeep"


def is_expired_file(file_path: Path, expiration_limit: datetime) -> bool:
    file_timezone = ZoneInfo(Config.TIMEZONE_NAME)
    file_modified_datetime = datetime.fromtimestamp(
        file_path.stat().st_mtime,
        tz=file_timezone,
    )

    return file_modified_datetime < expiration_limit


def cleanup_storage_folder(folder_path: Path, expiration_limit: datetime) -> int:
    """
    Resumo:
        Remove arquivos expirados de uma pasta de armazenamento sem apagar .gitkeep.
    """
    removed_files_count = 0

    if not folder_path.exists():
        logging.info("limpeza ignorada. pasta não encontrada")
        return removed_files_count

    for file_path in folder_path.rglob("*"):
        if not file_path.is_file() or is_preserved_file(file_path):
            continue

        if is_expired_file(file_path, expiration_limit):
            delete_file(file_path)
            removed_files_count += 1

    return removed_files_count

def get_cleanup_storage_folders() -> list[Path]:
    return [
        Config.COMPARE_RECEIVED_FOLDER,
        Config.COMPARE_PROCESSED_FOLDER,
        Config.COMPARE_TEMP_FOLDER,
        Config.EXTRACT_TEXT_RECEIVED_FOLDER,
        Config.EXTRACT_TEXT_PROCESSED_FOLDER,
        Config.EXTRACT_TEXT_TEMP_FOLDER,
    ]

def cleanup_compare_files() -> int:
    expiration_limit = get_file_expiration_limit(
        Config.TIMEZONE_NAME,
        Config.CLEANUP_FILE_MAX_AGE_HOURS,
    )

    removed_files_count = 0

    for folder_path in get_cleanup_storage_folders():
        removed_files_count += cleanup_storage_folder(folder_path, expiration_limit)

    logging.info(f"limpeza concluída. arquivos removidos: {removed_files_count}")

    return removed_files_count