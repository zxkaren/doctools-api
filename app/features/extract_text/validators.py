from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.exceptions import BadRequestError
from app.core.validators import get_file_extension


def validate_output_format(output_format: str) -> str:
    normalized_output_format = output_format.lower().strip()

    if normalized_output_format not in Config.ALLOWED_EXTRACT_TEXT_OUTPUT_FORMATS:
        raise BadRequestError(
            "selecione um formato de saída permitido: docx, txt ou json"
        )

    return normalized_output_format


def validate_uploaded_files(uploaded_files: list[FileStorage]) -> list[FileStorage]:
    if not uploaded_files:
        raise BadRequestError("informe ao menos um arquivo para extração de texto")

    valid_uploaded_files = [
        uploaded_file
        for uploaded_file in uploaded_files
        if uploaded_file and uploaded_file.filename
    ]

    if not valid_uploaded_files:
        raise BadRequestError("nenhum arquivo válido foi enviado para extração de texto")

    return valid_uploaded_files


def validate_extract_text_extension(uploaded_file: FileStorage) -> str:
    file_extension = get_file_extension(uploaded_file.filename)

    if file_extension not in Config.ALLOWED_EXTRACT_TEXT_EXTENSIONS:
        raise BadRequestError(
            "selecione uma extensão permitida para extração de texto: pdf, docx ou pptx"
        )

    return file_extension


def validate_extract_text_request(
    uploaded_files: list[FileStorage],
    output_format: str,
) -> tuple[list[FileStorage], str]:
    """
    Resumo:
        Valida os arquivos enviados para extração de texto e o formato de saída
        solicitado pelo usuário.

    Parâmetros:
        uploaded_files (list[FileStorage]): arquivos enviados na requisição.
        output_format (str): formato de saída solicitado. Aceita docx, txt ou json.

    Retorno:
        tuple[list[FileStorage], str]: arquivos válidos e formato de saída normalizado.
    """
    valid_uploaded_files = validate_uploaded_files(uploaded_files)
    normalized_output_format = validate_output_format(output_format)

    for uploaded_file in valid_uploaded_files:
        validate_extract_text_extension(uploaded_file)

    return valid_uploaded_files, normalized_output_format