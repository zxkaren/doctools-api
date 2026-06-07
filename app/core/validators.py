from pathlib import Path

from werkzeug.datastructures import FileStorage

from app.core.exceptions import BadRequestError


def get_file_extension(filename: str) -> str:
    return Path(filename).suffix.lower().replace(".", "", 1)


def validate_uploaded_file(uploaded_file: FileStorage | None, field_name: str) -> None:
    if uploaded_file is None or not uploaded_file.filename:
        raise BadRequestError(f"informe o arquivo {field_name}")


def validate_allowed_extension(file_extension: str, allowed_extensions: set[str]) -> None:
    if file_extension not in allowed_extensions:
        raise BadRequestError(
            "selecione uma extensão permitida (pdf, doc, docx, xlsx, ppt e pptx.)"
        )


def validate_same_extension(original_extension: str, modified_extension: str) -> None:
    if original_extension != modified_extension:
        raise BadRequestError("os arquivos devem ter a mesma extensão")


def validate_response_mode(response_mode: str, allowed_response_modes: set[str]) -> None:
    if response_mode not in allowed_response_modes:
        raise BadRequestError(
            "selecione um modo de resposta permitido: download_url, json ou json_file"
        )