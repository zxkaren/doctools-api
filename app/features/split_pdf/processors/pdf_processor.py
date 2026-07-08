from pathlib import Path
from typing import Any

import fitz
from werkzeug.utils import secure_filename


def get_pdf_total_pages(pdf_path: str) -> int:
    with fitz.open(pdf_path) as pdf_document:
        return pdf_document.page_count


def split_pdf_one_by_one(
    source_pdf_path: str,
    original_filename: str,
    processed_folder: str,
    processing_timestamp: str,
) -> list[dict[str, Any]]:
    """
    Resumo:
        Separa todas as páginas do PDF original em arquivos PDF individuais.

    Parâmetros:
        source_pdf_path: caminho do PDF original salvo no storage.
        original_filename: nome original do arquivo enviado pelo usuário.
        processed_folder: pasta onde os PDFs finais serão salvos.
        processing_timestamp: data/hora usada para evitar sobrescrita de arquivos.

    Retorno:
        Lista com os metadados dos PDFs gerados.
    """
    output_folder = Path(processed_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    generated_files: list[dict[str, Any]] = []
    filename_base = build_filename_base(original_filename)

    with fitz.open(source_pdf_path) as source_pdf_document:
        for page_index in range(source_pdf_document.page_count):
            page_number = page_index + 1
            output_filename = (
                f"{filename_base}_one-by-one-{page_number}-{processing_timestamp}.pdf"
            )
            output_path = output_folder / output_filename

            create_pdf_from_pages(
                source_pdf_document=source_pdf_document,
                page_numbers=[page_number],
                output_path=str(output_path),
            )

            generated_files.append(
                {
                    "filename": output_filename,
                    "file_path": str(output_path),
                    "pages": [page_number],
                }
            )

    return generated_files


def split_pdf_by_packs(
    source_pdf_path: str,
    original_filename: str,
    processed_folder: str,
    packs: dict[int, list[int]],
    processing_timestamp: str,
) -> list[dict[str, Any]]:
    """
    Resumo:
        Separa o PDF original em pacotes personalizados de páginas.

    Parâmetros:
        source_pdf_path: caminho do PDF original salvo no storage.
        original_filename: nome original do arquivo enviado pelo usuário.
        processed_folder: pasta onde os PDFs finais serão salvos.
        packs: dicionário no formato {numero_do_pack: [paginas]}.
        processing_timestamp: data/hora usada para evitar sobrescrita de arquivos.

    Retorno:
        Lista com os metadados dos PDFs gerados.
    """
    output_folder = Path(processed_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    generated_files: list[dict[str, Any]] = []
    filename_base = build_filename_base(original_filename)

    with fitz.open(source_pdf_path) as source_pdf_document:
        for pack_number, pack_pages in packs.items():
            output_filename = (
                f"{filename_base}_pack{pack_number:02d}-{processing_timestamp}.pdf"
            )
            output_path = output_folder / output_filename

            create_pdf_from_pages(
                source_pdf_document=source_pdf_document,
                page_numbers=pack_pages,
                output_path=str(output_path),
            )

            generated_files.append(
                {
                    "filename": output_filename,
                    "file_path": str(output_path),
                    "pack": pack_number,
                    "pages": pack_pages,
                }
            )

    return generated_files


def create_pdf_from_pages(
    source_pdf_document: fitz.Document,
    page_numbers: list[int],
    output_path: str,
) -> None:
    """
    Resumo:
        Cria um novo PDF com base nas páginas selecionadas do documento original.

    Parâmetros:
        source_pdf_document: documento PDF original aberto pelo fitz.
        page_numbers: lista de páginas em formato humano, iniciando em 1.
        output_path: caminho completo onde o novo PDF será salvo.

    Retorno:
        None.
    """
    with fitz.open() as output_pdf_document:
        for page_number in page_numbers:
            page_index = page_number - 1
            output_pdf_document.insert_pdf(
                source_pdf_document,
                from_page=page_index,
                to_page=page_index,
            )

        output_pdf_document.save(output_path)


def build_filename_base(original_filename: str) -> str:
    safe_filename = secure_filename(original_filename)
    filename_base = Path(safe_filename).stem

    return filename_base or "documento"