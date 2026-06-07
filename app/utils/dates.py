from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def get_current_datetime(timezone_name: str) -> datetime:
    return datetime.now(ZoneInfo(timezone_name))


def get_filename_timestamp(timezone_name: str) -> str:
    current_datetime = get_current_datetime(timezone_name)

    return current_datetime.strftime("%d%m%Y-%H%M%S")


def get_file_expiration_limit(timezone_name: str, max_age_hours: int) -> datetime:
    current_datetime = get_current_datetime(timezone_name)

    return current_datetime - timedelta(hours=max_age_hours)