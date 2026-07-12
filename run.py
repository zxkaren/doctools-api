from apscheduler.schedulers.background import BackgroundScheduler

from app import create_app
from app.config import Config
from app.core.file_manager import ensure_folder_exists
from app.jobs.cleanup_files import cleanup_all_feature_files


def create_storage_folders() -> None:
    storage_folders = [
        Config.COMPARE_RECEIVED_FOLDER,
        Config.COMPARE_PROCESSED_FOLDER,
        Config.COMPARE_TEMP_FOLDER,
        Config.EXTRACT_TEXT_RECEIVED_FOLDER,
        Config.EXTRACT_TEXT_PROCESSED_FOLDER,
        Config.EXTRACT_TEXT_TEMP_FOLDER,
        Config.SPLIT_PDF_RECEIVED_FOLDER,
        Config.SPLIT_PDF_PROCESSED_FOLDER,
        Config.SPLIT_PDF_TEMP_FOLDER,
        Config.MERGE_PDF_RECEIVED_FOLDER,
        Config.MERGE_PDF_PROCESSED_FOLDER,
        Config.MERGE_PDF_TEMP_FOLDER,
        Config.OCR_PDF_RECEIVED_FOLDER,
        Config.OCR_PDF_PROCESSED_FOLDER,
        Config.OCR_PDF_TEMP_FOLDER,
    ]

    try:
        for folder_path in storage_folders:
            ensure_folder_exists(folder_path)

        print("sucesso. pastas de storage criadas")

    except Exception as error:
        print(f"falha. pastas de storage não criadas: {error}")
        raise


def start_cleanup_scheduler() -> None:
    try:
        scheduler = BackgroundScheduler(timezone=Config.TIMEZONE_NAME)

        scheduler.add_job(
            cleanup_all_feature_files,
            "interval",
            minutes=Config.CLEANUP_INTERVAL_MINUTES,
            id="cleanup_all_feature_files",
            replace_existing=True,
        )

        scheduler.start()
        print("sucesso. scheduler iniciado")

    except Exception as error:
        print(f"falha. scheduler não iniciado: {error}")
        raise


def start_api() -> None:
    try:
        flask_app = create_app()

        create_storage_folders()
        start_cleanup_scheduler()

        print("sucesso. api iniciada")

        flask_app.run(
            host=Config.HOST,
            port=Config.PORT,
            debug=Config.DEBUG,
            use_reloader=False,
        )

    except Exception as error:
        print(f"falha. api não iniciada: {error}")
        raise


if __name__ == "__main__":
    start_api()