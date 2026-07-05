from flask import Blueprint, request, send_from_directory

from app.config import Config
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.file_manager import sanitize_filename
from app.core.responses import build_success_response
from app.features.extract_text.service import process_extract_text_request


extract_text_blueprint = Blueprint("extract_text", __name__)


@extract_text_blueprint.route("/", methods=["POST"])
def extract_text_by_detected_extension():
    """
    Extrai textos de documentos pela extensão enviada
    ---
    tags:
      - Extração de Texto
    consumes:
      - multipart/form-data
    parameters:
      - name: files
        in: formData
        type: file
        required: true
        description: Um ou mais arquivos para extração de texto. Aceita PDF, DOCX e PPTX.
      - name: output_format
        in: formData
        type: string
        required: false
        enum:
          - docx
          - txt
          - json
        description: Formato de saída. Se não informado, usa DOCX.
    responses:
      200:
        description: Extração de texto concluída
      400:
        description: Dados incorretos ou faltando na requisição
      404:
        description: Arquivo processado não encontrado
      500:
        description: Erro interno inesperado no servidor
    """
    uploaded_files = request.files.getlist("files")
    output_format = request.form.get(
        "output_format",
        Config.DEFAULT_EXTRACT_TEXT_OUTPUT_FORMAT,
    )

    response_data = process_extract_text_request(
        uploaded_files,
        output_format,
    )

    return build_success_response("extração de texto concluída", response_data)


@extract_text_blueprint.route("/download/<processed_filename>", methods=["GET"])
def download_processed_file(processed_filename: str):
    safe_filename = sanitize_filename(processed_filename)

    if safe_filename != processed_filename:
        raise BadRequestError("nome do arquivo inválido")

    processed_path = Config.EXTRACT_TEXT_PROCESSED_FOLDER / safe_filename

    if not processed_path.exists():
        raise NotFoundError("arquivo processado não encontrado")

    return send_from_directory(
        Config.EXTRACT_TEXT_PROCESSED_FOLDER,
        safe_filename,
        as_attachment=True,
    )