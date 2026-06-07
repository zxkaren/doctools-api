from http import HTTPStatus

from flask import Flask, jsonify
from werkzeug.exceptions import HTTPException


class ApiError(Exception):
    def __init__(self, message: str, status_code: int) -> None:
        self.message = message
        self.status_code = status_code
        super().__init__(message)


class BadRequestError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(message, HTTPStatus.BAD_REQUEST)


class NotFoundError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(message, HTTPStatus.NOT_FOUND)


class FeatureNotImplementedError(ApiError):
    def __init__(self, message: str) -> None:
        super().__init__(message, HTTPStatus.NOT_IMPLEMENTED)


def build_error_payload(message: str, status_code: int) -> dict:
    return {
        "success": False,
        "error": {
            "status_code": status_code,
            "message": message,
        },
    }


def register_error_handlers(flask_app: Flask) -> None:
    """
    Resumo:
        Registra os tratamentos globais de erro da API.

    Parâmetros:
        flask_app (Flask): aplicação Flask onde os handlers serão registrados.

    Retorno:
        None.
    """

    @flask_app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        print(f"requisição falhou. {error.message}")
        return jsonify(build_error_payload(error.message, error.status_code)), error.status_code

    @flask_app.errorhandler(HTTPException)
    def handle_http_error(error: HTTPException):
        status_code = error.code or HTTPStatus.INTERNAL_SERVER_ERROR
        message = error.description or "erro http inesperado"

        print(f"requisição falhou. {message}")
        return jsonify(build_error_payload(message, status_code)), status_code

    @flask_app.errorhandler(Exception)
    def handle_unexpected_error(error: Exception):
        print(f"requisição falhou. {error}")

        return (
            jsonify(
                build_error_payload(
                    "ocorreu um erro interno e inesperado no servidor",
                    HTTPStatus.INTERNAL_SERVER_ERROR,
                )
            ),
            HTTPStatus.INTERNAL_SERVER_ERROR,
        )