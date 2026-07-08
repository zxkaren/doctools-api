from flask import Blueprint, request, send_from_directory

from app.config import Config
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.file_manager import sanitize_filename
from app.core.responses import build_success_response
from app.features.split_pdf.service import process_split_pdf_request


split_pdf_blueprint = Blueprint("split_pdf", __name__)


@split_pdf_blueprint.route("/", methods=["POST"])
def split_pdf():
    """
    Realiza split de PDF por página individual ou por packs personalizados
    ---
    tags:
      - Split PDF
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Arquivo PDF que será separado.
      - name: split_type
        in: formData
        type: string
        required: true
        enum:
          - one_by_one
          - pack
        description: Tipo de split. Use one_by_one para páginas individuais ou pack para pacotes.
      - name: pack
        in: formData
        type: string
        required: false
        description: Número do pack. Para vários packs no Swagger use 1,2,3.
      - name: pages
        in: formData
        type: string
        required: false
        description: Páginas do pack. Aceita páginas soltas e intervalos. Exemplo 1-3 ou 1,2,5-8.
    responses:
      200:
        description: Split PDF concluído
      400:
        description: Dados incorretos ou faltando na requisição
      404:
        description: Arquivo processado não encontrado
      500:
        description: Erro interno inesperado no servidor
    """
    uploaded_files = request.files.getlist("file")
    split_type = request.form.get("split_type")
    pack_numbers = request.form.getlist("pack")
    pack_pages_items = request.form.getlist("pages")

    response_data = process_split_pdf_request(
        uploaded_files=uploaded_files,
        split_type=split_type,
        pack_numbers=pack_numbers,
        pack_pages_items=pack_pages_items,
    )

    return build_success_response("split pdf concluído", response_data)


@split_pdf_blueprint.route("/download/<path:processed_filename>", methods=["GET"])
def download_processed_file(processed_filename: str):
    safe_filename = sanitize_filename(processed_filename)

    if safe_filename != processed_filename:
        raise BadRequestError("nome do arquivo inválido")

    processed_path = Config.SPLIT_PDF_PROCESSED_FOLDER / safe_filename

    if not processed_path.exists():
        raise NotFoundError("arquivo processado não encontrado")

    return send_from_directory(
        Config.SPLIT_PDF_PROCESSED_FOLDER,
        safe_filename,
        as_attachment=True,
    )