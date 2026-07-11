from flask import Blueprint, request, send_from_directory

from app.config import Config
from app.core.exceptions import BadRequestError, NotFoundError
from app.core.file_manager import sanitize_filename
from app.core.responses import build_success_response
from app.features.ocr_pdf.service import process_ocr_pdf_request


ocr_pdf_blueprint = Blueprint("ocr_pdf", __name__)


@ocr_pdf_blueprint.route("/", methods=["POST"])
def ocr_pdf():
    """
    Aplica OCR em um ou mais arquivos PDF
    ---
    tags:
      - OCR PDF
    consumes:
      - multipart/form-data
    parameters:
      - name: file
        in: formData
        type: file
        required: true
        description: Arquivos PDF que receberão OCR. Envie o campo file múltiplas vezes.
      - name: ocr_mode
        in: formData
        type: string
        required: false
        enum:
          - apply
          - force
        description: Use apply para aplicar OCR apenas onde necessário ou force para forçar OCR em todo o PDF.
      - name: ocr_language
        in: formData
        type: string
        required: false
        enum:
          - pt_br
          - pt_pt
          - en_us
          - es_es
        description: Idioma usado na aplicação do OCR.
      - name: ocr_quality
        in: formData
        type: string
        required: false
        enum:
          - standard
          - enhanced
          - aggressive
          - ebook
        description: Perfil de qualidade do OCR. Use standard para seguro, enhanced para melhoria moderada, aggressive para PDFs de baixa qualidade e ebook para apostilas, e-books e materiais de estudo com layout visual.
    responses:
      200:
        description: OCR PDF concluído
      400:
        description: Dados incorretos ou faltando na requisição
      404:
        description: Arquivo processado não encontrado
      500:
        description: Erro interno inesperado no servidor
    """
    uploaded_files = request.files.getlist("file")
    ocr_mode = request.form.get("ocr_mode")
    ocr_language = request.form.get("ocr_language")
    ocr_quality = request.form.get("ocr_quality")

    response_data = process_ocr_pdf_request(
        uploaded_files=uploaded_files,
        ocr_mode=ocr_mode,
        ocr_language=ocr_language,
        ocr_quality=ocr_quality,
    )

    return build_success_response("ocr pdf concluído", response_data)


@ocr_pdf_blueprint.route("/download/<processed_filename>", methods=["GET"])
def download_processed_file(processed_filename: str):
    safe_filename = sanitize_filename(processed_filename)

    if safe_filename != processed_filename:
        raise BadRequestError("nome do arquivo inválido")

    processed_path = Config.OCR_PDF_PROCESSED_FOLDER / safe_filename

    if not processed_path.exists():
        raise NotFoundError("arquivo processado não encontrado")

    return send_from_directory(
        Config.OCR_PDF_PROCESSED_FOLDER,
        safe_filename,
        as_attachment=True,
    )