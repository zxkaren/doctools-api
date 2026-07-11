import subprocess
from pathlib import Path


MAX_IMAGE_MPIXELS = "1000"

OCR_QUALITY_ARGUMENTS = {
    "standard": [],
    "enhanced": [
        "--rotate-pages",
        "--deskew",
        "--clean",
        "--oversample",
        "300",
    ],
    "aggressive": [
        "--deskew",
        "--clean",
        "--clean-final",
        "--oversample",
        "400",
    ],
    "ebook": [
        "--deskew",
        "--oversample",
        "400",
        "--tesseract-pagesegmode",
        "6",
        "--pdf-renderer",
        "hocr",
    ],
}


def apply_ocr_to_pdf(
    source_pdf_path: Path,
    target_pdf_path: Path,
    ocr_mode: str,
    tesseract_language: str,
    ocr_quality: str,
) -> Path:
    """
    Resumo:
        Aplica OCR em um arquivo PDF usando o OCRmyPDF instalado no Docker.

    Parâmetros:
        source_pdf_path: caminho do arquivo PDF original.
        target_pdf_path: caminho onde o PDF com OCR será salvo.
        ocr_mode: modo de OCR. Aceita apply ou force.
        tesseract_language: idioma usado pelo Tesseract, como por, eng ou spa.
        ocr_quality: perfil de qualidade. Aceita standard, enhanced, aggressive ou ebook.

    Retorno:
        Caminho do PDF processado com OCR.
    """
    target_pdf_path.parent.mkdir(parents=True, exist_ok=True)

    ocr_command = [
        "ocrmypdf",
        "--language",
        tesseract_language,
        "--output-type",
        "pdf",
        "--max-image-mpixels",
        MAX_IMAGE_MPIXELS,
    ]

    ocr_command.extend(OCR_QUALITY_ARGUMENTS[ocr_quality])

    if ocr_mode == "force":
        ocr_command.append("--force-ocr")
    else:
        ocr_command.append("--skip-text")

    ocr_command.extend(
        [
            str(source_pdf_path),
            str(target_pdf_path),
        ]
    )

    try:
        subprocess.run(
            ocr_command,
            check=True,
            capture_output=True,
            text=True,
        )

        print(f"OCR aplicado com sucesso: {target_pdf_path.name}")
        return target_pdf_path

    except subprocess.CalledProcessError as command_error:
        error_message = command_error.stderr or command_error.stdout
        print(f"Falha ao aplicar OCR em {source_pdf_path.name}: {error_message}")
        raise RuntimeError(
            f"falha ao aplicar OCR no arquivo {source_pdf_path.name}"
        ) from command_error