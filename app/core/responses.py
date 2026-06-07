from http import HTTPStatus
from typing import Any

from flask import Response, jsonify


def build_success_payload(message: str, data: dict[str, Any] | None = None) -> dict[str, Any]:
    payload = {
        "success": True,
        "message": message,
    }

    if data is not None:
        payload["data"] = data

    return payload


def build_compare_payload(download_url: str, summary_table: dict[str, Any]) -> dict[str, Any]:
    return {
        "download_url": download_url,
        "summary_table": summary_table,
    }


def build_success_response(
    message: str,
    data: dict[str, Any] | None = None,
    status_code: int = HTTPStatus.OK,
) -> tuple[Response, int]:
    payload = build_success_payload(message, data)

    return jsonify(payload), status_code