import os
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

os.environ.setdefault("FLASK_ENV", "testing")
os.environ.setdefault("DEBUG", "False")
os.environ.setdefault("HOST", "127.0.0.1")
os.environ.setdefault("PORT", "5000")
os.environ.setdefault("TIMEZONE_NAME", "America/Sao_Paulo")
os.environ.setdefault("SECRET_KEY", "test-secret-key")
os.environ.setdefault("MAX_CONTENT_LENGTH", "52428800")
os.environ.setdefault("STORAGE_ROOT", "storage")
os.environ.setdefault("COMPARE_STORAGE_FOLDER", "compare")
os.environ.setdefault("COMPARE_RECEIVED_FOLDER", "received")
os.environ.setdefault("COMPARE_PROCESSED_FOLDER", "processed")
os.environ.setdefault("COMPARE_TEMP_FOLDER", "temp")
os.environ.setdefault("ALLOWED_COMPARE_EXTENSIONS", "pdf,doc,docx,xlsx,ppt,pptx")
os.environ.setdefault("IMPLEMENTED_COMPARE_EXTENSIONS", "pdf")
os.environ.setdefault("DEFAULT_COMPARE_RESPONSE_MODE", "json_file")
os.environ.setdefault("ALLOWED_COMPARE_RESPONSE_MODES", "download_url,json,json_file")
os.environ.setdefault("CLEANUP_FILE_MAX_AGE_HOURS", "24")
os.environ.setdefault("CLEANUP_INTERVAL_MINUTES", "60")

from app.config import Config
from app.jobs.cleanup_files import cleanup_compare_files


def create_file_with_modified_datetime(file_path: Path, modified_datetime: datetime) -> None:
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text("conteúdo de teste", encoding="utf-8")

    modified_timestamp = modified_datetime.timestamp()
    os.utime(file_path, (modified_timestamp, modified_timestamp))


def test_cleanup_compare_files_removes_only_expired_files(tmp_path: Path) -> None:
    Config.COMPARE_RECEIVED_FOLDER = tmp_path / "storage" / "compare" / "received"
    Config.COMPARE_PROCESSED_FOLDER = tmp_path / "storage" / "compare" / "processed"
    Config.COMPARE_TEMP_FOLDER = tmp_path / "storage" / "compare" / "temp"
    Config.CLEANUP_FILE_MAX_AGE_HOURS = 24

    timezone = ZoneInfo(Config.TIMEZONE_NAME)
    current_datetime = datetime.now(timezone)

    expired_file = Config.COMPARE_RECEIVED_FOLDER / "expired.pdf"
    current_file = Config.COMPARE_PROCESSED_FOLDER / "current.pdf"
    preserved_file = Config.COMPARE_TEMP_FOLDER / ".gitkeep"

    create_file_with_modified_datetime(
        expired_file,
        current_datetime - timedelta(hours=48),
    )
    create_file_with_modified_datetime(
        current_file,
        current_datetime,
    )
    create_file_with_modified_datetime(
        preserved_file,
        current_datetime - timedelta(hours=48),
    )

    removed_files_count = cleanup_compare_files()

    assert removed_files_count == 1
    assert not expired_file.exists()
    assert current_file.exists()
    assert preserved_file.exists()