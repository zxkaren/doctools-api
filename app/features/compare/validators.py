from werkzeug.datastructures import FileStorage

from app.config import Config
from app.core.exceptions import BadRequestError, FeatureNotImplementedError
from app.core.validators import (
    get_file_extension,
    validate_allowed_extension,
    validate_response_mode,
    validate_same_extension,
    validate_uploaded_file,
)


def validate_route_extension(route_extension: str | None) -> str | None:
    if route_extension is None:
        return None

    normalized_extension = route_extension.lower().strip()
    validate_allowed_extension(normalized_extension, Config.ALLOWED_COMPARE_EXTENSIONS)

    return normalized_extension


def validate_implemented_extension(file_extension: str) -> None:
    if file_extension not in Config.IMPLEMENTED_COMPARE_EXTENSIONS:
        raise FeatureNotImplementedError(
            "o servidor reconhece a requisição, mas não possui a funcionalidade necessária para atendê-la"
        )


def validate_specific_route_extension(file_extension: str, route_extension: str | None) -> None:
    if route_extension is not None and file_extension != route_extension:
        raise BadRequestError("essa rota só aceita a extensão selecionada")


def validate_compare_request(
    original_file: FileStorage | None,
    modified_file: FileStorage | None,
    response_mode: str,
    route_extension: str | None = None,
) -> str:
    """
    Resumo:
        Valida os arquivos enviados para comparação e identifica a extensão processável.

    Parâmetros:
        original_file (FileStorage | None): arquivo original enviado na requisição.
        modified_file (FileStorage | None): arquivo modificado enviado na requisição.
        response_mode (str): modo de resposta solicitado.
        route_extension (str | None): extensão informada na rota específica.

    Retorno:
        str: extensão validada para processamento.
    """
    normalized_route_extension = validate_route_extension(route_extension)

    validate_uploaded_file(original_file, "original")
    validate_uploaded_file(modified_file, "modified")
    validate_response_mode(response_mode, Config.ALLOWED_COMPARE_RESPONSE_MODES)

    original_extension = get_file_extension(original_file.filename)
    modified_extension = get_file_extension(modified_file.filename)

    validate_allowed_extension(original_extension, Config.ALLOWED_COMPARE_EXTENSIONS)
    validate_allowed_extension(modified_extension, Config.ALLOWED_COMPARE_EXTENSIONS)
    validate_same_extension(original_extension, modified_extension)
    validate_specific_route_extension(original_extension, normalized_route_extension)
    validate_implemented_extension(original_extension)

    return original_extension