from pathlib import Path
from typing import Any

import fitz


def merge_pdf_files(
    ordered_pdf_files: list[dict[str, str]],
    processed_folder: str,
    output_filename: str,
) -> dict[str, Any]:
    """
    Resumo:
    Une múltiplos PDFs em um único arquivo, respeitando a ordem recebida.

    Parâmetros:
    ordered_pdf_files: lista de PDFs já salvos, contendo caminho e nome original.
    processed_folder: pasta onde o PDF final será salvo.
    output_filename: nome do arquivo PDF unificado.

    Retorno:
    Dicionário com metadados do arquivo gerado e dos documentos unificados.
    """
    output_folder = Path(processed_folder)
    output_folder.mkdir(parents=True, exist_ok=True)

    output_path = output_folder / output_filename
    merged_documents: list[dict[str, Any]] = []
    total_pages = 0

    with fitz.open() as merged_pdf_document:
        for document_order, pdf_file in enumerate(ordered_pdf_files, start=1):
            original_filename = pdf_file["original_filename"]
            source_pdf_path = pdf_file["file_path"]

            with fitz.open(source_pdf_path) as source_pdf_document:
                page_count = source_pdf_document.page_count
                merged_pdf_document.insert_pdf(source_pdf_document)

            total_pages += page_count
            merged_documents.append(
                {
                    "order": document_order,
                    "filename": original_filename,
                    "pages": page_count,
                }
            )

        merged_pdf_document.save(output_path)

    return {
        "filename": output_filename,
        "file_path": str(output_path),
        "total_files": len(ordered_pdf_files),
        "total_pages": total_pages,
        "merged_documents": merged_documents,
    }