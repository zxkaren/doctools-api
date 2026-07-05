from flask import Blueprint, request, send_from_directory

from app.config import Config
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.file_manager import sanitize_filename
from app.core.responses import build_success_response
from app.features.compare.service import process_compare_request


compare_blueprint = Blueprint("compare", __name__)


def get_response_mode() -> str:
    return request.form.get("response_mode", Config.DEFAULT_COMPARE_RESPONSE_MODE)


def get_uploaded_files():
    return request.files.get("original"), request.files.get("modified")


@compare_blueprint.route("/", methods=["POST"])
def compare_by_detected_extension():
    """
    Compara documentos pela extensão enviada
    ---
    tags:
      - Compare
    consumes:
      - multipart/form-data
    parameters:
      - name: original
        in: formData
        type: file
        required: true
        description: Arquivo original
      - name: modified
        in: formData
        type: file
        required: true
        description: Arquivo modificado
      - name: response_mode
        in: formData
        type: string
        required: false
        enum:
          - download_url
          - json
          - json_file
        description: Modo de resposta
    responses:
      200:
        description: Comparação concluída
      400:
        description: Dados incorretos ou faltando na requisição
      500:
        description: Erro interno inesperado no servidor
      501:
        description: Funcionalidade ainda não implementada
    """
    original_file, modified_file = get_uploaded_files()
    response_mode = get_response_mode()

    response_data = process_compare_request(
        original_file,
        modified_file,
        response_mode,
    )

    return build_success_response("comparação concluída", response_data)


@compare_blueprint.route("/<route_extension>", methods=["POST"])
def compare_by_selected_extension(route_extension: str):
    """
    Compara documentos pela extensão selecionada
    ---
    tags:
      - Compare
    consumes:
      - multipart/form-data
    parameters:
      - name: route_extension
        in: path
        type: string
        required: true
        enum:
          - pdf
          - docx
          - xlsx
          - pptx
        description: Extensão escolhida
      - name: original
        in: formData
        type: file
        required: true
        description: Arquivo original
      - name: modified
        in: formData
        type: file
        required: true
        description: Arquivo modificado
      - name: response_mode
        in: formData
        type: string
        required: false
        enum:
          - download_url
          - json
          - json_file
        description: Modo de resposta
    responses:
      200:
        description: Comparação concluída
      400:
        description: Dados incorretos ou faltando na requisição
      500:
        description: Erro interno inesperado no servidor
      501:
        description: Funcionalidade ainda não implementada
    """
    original_file, modified_file = get_uploaded_files()
    response_mode = get_response_mode()

    response_data = process_compare_request(
        original_file,
        modified_file,
        response_mode,
        route_extension,
    )

    return build_success_response("comparação concluída", response_data)


@compare_blueprint.route("/download/<processed_filename>", methods=["GET"])
def download_processed_file(processed_filename: str):
    safe_filename = sanitize_filename(processed_filename)

    if safe_filename != processed_filename:
        raise BadRequestError("nome do arquivo inválido")

    processed_path = Config.COMPARE_PROCESSED_FOLDER / safe_filename

    if not processed_path.exists():
        raise NotFoundError("arquivo processado não encontrado")

    return send_from_directory(
        Config.COMPARE_PROCESSED_FOLDER,
        safe_filename,
        as_attachment=True,
    )