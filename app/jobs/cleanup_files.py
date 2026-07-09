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

    Parâmetros:
        folder_path: pasta que será analisada.
        expiration_limit: data limite para considerar um arquivo expirado.

    Retorno:
        Quantidade de arquivos removidos.
    """
    removed_files_count = 0

    if not folder_path.exists():
        print(f"limpeza ignorada: pasta não encontrada - {folder_path}")
        return removed_files_count

    for file_path in folder_path.rglob("*"):
        if not file_path.is_file() or is_preserved_file(file_path):
            continue

        if is_expired_file(file_path, expiration_limit):
            delete_file(file_path)
            removed_files_count += 1

    return removed_files_count


def get_compare_storage_folders() -> list[Path]:
    return [
        Config.COMPARE_RECEIVED_FOLDER,
        Config.COMPARE_PROCESSED_FOLDER,
        Config.COMPARE_TEMP_FOLDER,
    ]


def get_extract_text_storage_folders() -> list[Path]:
    return [
        Config.EXTRACT_TEXT_RECEIVED_FOLDER,
        Config.EXTRACT_TEXT_PROCESSED_FOLDER,
        Config.EXTRACT_TEXT_TEMP_FOLDER,
    ]


def get_split_pdf_storage_folders() -> list[Path]:
    return [
        Config.SPLIT_PDF_RECEIVED_FOLDER,
        Config.SPLIT_PDF_PROCESSED_FOLDER,
        Config.SPLIT_PDF_TEMP_FOLDER,
    ]

def get_merge_pdf_storage_folders() -> list[Path]:
    return [
        Config.MERGE_PDF_RECEIVED_FOLDER,
        Config.MERGE_PDF_PROCESSED_FOLDER,
        Config.MERGE_PDF_TEMP_FOLDER,
    ]

def cleanup_folders(storage_folders: list[Path]) -> int:
    expiration_limit = get_file_expiration_limit(
        Config.TIMEZONE_NAME,
        Config.CLEANUP_FILE_MAX_AGE_HOURS,
    )

    removed_files_count = 0

    for folder_path in storage_folders:
        removed_files_count += cleanup_storage_folder(folder_path, expiration_limit)

    return removed_files_count


def cleanup_compare_files() -> int:
    removed_files_count = cleanup_folders(get_compare_storage_folders())

    print(f"limpeza compare concluída: {removed_files_count} arquivo(s) removido(s)")
    return removed_files_count


def cleanup_extract_text_files() -> int:
    removed_files_count = cleanup_folders(get_extract_text_storage_folders())

    print(f"limpeza extract-text concluída: {removed_files_count} arquivo(s) removido(s)")
    return removed_files_count


def cleanup_split_pdf_files() -> int:
    removed_files_count = cleanup_folders(get_split_pdf_storage_folders())

    print(f"limpeza split-pdf concluída: {removed_files_count} arquivo(s) removido(s)")
    return removed_files_count

def cleanup_merge_pdf_files() -> int:
    removed_files_count = cleanup_folders(get_merge_pdf_storage_folders())
    print(f"limpeza merge-pdf concluída: {removed_files_count} arquivo(s) removido(s)")
    return removed_files_count

def cleanup_all_feature_files() -> int:
    removed_files_count = 0
    removed_files_count += cleanup_compare_files()
    removed_files_count += cleanup_extract_text_files()
    removed_files_count += cleanup_split_pdf_files()
    removed_files_count += cleanup_merge_pdf_files()
    print(f"limpeza geral concluída: {removed_files_count} arquivo(s) removido(s)")
    return removed_files_count