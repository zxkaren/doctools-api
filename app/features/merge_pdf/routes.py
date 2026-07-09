from flask import Blueprint, request, send_from_directory

from app.config import Config
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.file_manager import sanitize_filename
from app.core.responses import build_success_response
from app.features.merge_pdf.service import process_merge_pdf_request


merge_pdf_blueprint = Blueprint("merge_pdf", __name__)


@merge_pdf_blueprint.route("/", methods=["POST"])
def merge_pdf():
    """
    Realiza merge de múltiplos arquivos PDF
    ---
    tags:
      - Merge PDF
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Arquivos PDF que serão unidos. Envie o campo file múltiplas vezes.
      - name: order
        in: formData
        type: string
        required: false
        description: Ordem opcional dos arquivos. Aceita valores repetidos no form-data ou CSV. Exemplo 2,1,3.
    responses:
      200:
        description: Merge PDF concluído
      400:
        description: Dados incorretos ou faltando na requisição
      404:
        description: Arquivo processado não encontrado
      500:
        description: Erro interno inesperado no servidor
    """
    uploaded_files = request.files.getlist("file")
    order_items = request.form.getlist("order")

    response_data = process_merge_pdf_request(
        uploaded_files=uploaded_files,
        order_items=order_items,
    )

    return build_success_response("merge pdf concluído", response_data)


@merge_pdf_blueprint.route("/download/<path:processed_filename>", methods=["GET"])
def download_processed_file(processed_filename: str):
    safe_filename = sanitize_filename(processed_filename)

    if safe_filename != processed_filename:
        raise BadRequestError("nome do arquivo inválido")

    processed_path = Config.MERGE_PDF_PROCESSED_FOLDER / safe_filename

    if not processed_path.exists():
        raise NotFoundError("arquivo processado não encontrado")

    return send_from_directory(
        Config.MERGE_PDF_PROCESSED_FOLDER,
        safe_filename,
        as_attachment=True,
    )