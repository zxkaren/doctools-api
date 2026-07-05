from pathlib import Path

import fitz


def extract_text_from_pdf(file_path: Path) -> str:
    """
    Resumo:
        Extrai apenas o texto pesquisável de um arquivo PDF.

    Parâmetros:
        file_path (Path): caminho do arquivo PDF salvo em storage.

    Retorno:
        str: texto bruto extraído do PDF.
    """
    extracted_text_pages = []

    try:
        with fitz.open(file_path) as pdf_document:
            for page in pdf_document:
                page_text = page.get_text("text").strip()

                if page_text:
                    extracted_text_pages.append(page_text)

        return "\n\n".join(extracted_text_pages)

    except Exception as error:
        print(f"Erro ao extrair texto do PDF {file_path.name}: {error}")
        raise