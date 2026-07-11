from io import BytesIO
from pathlib import Path
from unittest.mock import Mock

import pytest
from werkzeug.datastructures import FileStorage

from app.core.exceptions import BadRequestError
from app.features.ocr_pdf.processors import pdf_processor
from app.features.ocr_pdf.processors.pdf_processor import apply_ocr_to_pdf
from app.features.ocr_pdf.validators import (
    validate_ocr_language,
    validate_ocr_mode,
    validate_ocr_quality,
    validate_pdf_files,
)


def create_uploaded_file(filename: str) -> FileStorage:
    return FileStorage(
        stream=BytesIO(b"conteudo fake para teste"),
        filename=filename,
        content_type="application/pdf",
    )


def test_validate_pdf_files_accepts_pdf_files():
    uploaded_files = [
        create_uploaded_file("arquivo_1.pdf"),
        create_uploaded_file("arquivo_2.PDF"),
    ]

    valid_files = validate_pdf_files(uploaded_files)

    assert len(valid_files) == 2
    assert valid_files[0].filename == "arquivo_1.pdf"
    assert valid_files[1].filename == "arquivo_2.PDF"


def test_validate_pdf_files_rejects_empty_file_list():
    with pytest.raises(BadRequestError):
        validate_pdf_files([])


def test_validate_pdf_files_rejects_non_pdf_file():
    uploaded_files = [create_uploaded_file("arquivo.docx")]

    with pytest.raises(BadRequestError):
        validate_pdf_files(uploaded_files)


def test_validate_ocr_mode_accepts_valid_modes():
    assert validate_ocr_mode("apply") == "apply"
    assert validate_ocr_mode("force") == "force"


def test_validate_ocr_mode_applies_default_mode():
    assert validate_ocr_mode(None) == "apply"


def test_validate_ocr_mode_rejects_invalid_mode():
    with pytest.raises(BadRequestError):
        validate_ocr_mode("invalid")


def test_validate_ocr_language_maps_supported_languages():
    assert validate_ocr_language("pt_br") == ("pt_br", "por")
    assert validate_ocr_language("pt_pt") == ("pt_pt", "por")
    assert validate_ocr_language("en_us") == ("en_us", "eng")
    assert validate_ocr_language("es_es") == ("es_es", "spa")


def test_validate_ocr_language_applies_default_language():
    assert validate_ocr_language(None) == ("pt_br", "por")


def test_validate_ocr_language_rejects_invalid_language():
    with pytest.raises(BadRequestError):
        validate_ocr_language("fr_fr")


def test_validate_ocr_quality_accepts_valid_qualities():
    assert validate_ocr_quality("standard") == "standard"
    assert validate_ocr_quality("enhanced") == "enhanced"
    assert validate_ocr_quality("aggressive") == "aggressive"
    assert validate_ocr_quality("ebook") == "ebook"


def test_validate_ocr_quality_applies_default_quality():
    assert validate_ocr_quality(None) == "standard"


def test_validate_ocr_quality_rejects_invalid_quality():
    with pytest.raises(BadRequestError):
        validate_ocr_quality("colored")


def test_apply_ocr_to_pdf_builds_standard_command(monkeypatch, tmp_path):
    subprocess_run_mock = Mock()
    monkeypatch.setattr(pdf_processor.subprocess, "run", subprocess_run_mock)

    source_pdf_path = tmp_path / "entrada.pdf"
    target_pdf_path = tmp_path / "saida.pdf"
    source_pdf_path.write_bytes(b"%PDF-1.4 fake")

    processed_path = apply_ocr_to_pdf(
        source_pdf_path=source_pdf_path,
        target_pdf_path=target_pdf_path,
        ocr_mode="apply",
        tesseract_language="por",
        ocr_quality="standard",
    )

    executed_command = subprocess_run_mock.call_args.args[0]

    assert processed_path == target_pdf_path
    assert "--skip-text" in executed_command
    assert "--force-ocr" not in executed_command
    assert "--language" in executed_command
    assert "por" in executed_command
    assert str(source_pdf_path) in executed_command
    assert str(target_pdf_path) in executed_command


def test_apply_ocr_to_pdf_builds_force_ebook_command(monkeypatch, tmp_path):
    subprocess_run_mock = Mock()
    monkeypatch.setattr(pdf_processor.subprocess, "run", subprocess_run_mock)

    source_pdf_path = tmp_path / "entrada.pdf"
    target_pdf_path = tmp_path / "saida.pdf"
    source_pdf_path.write_bytes(b"%PDF-1.4 fake")

    apply_ocr_to_pdf(
        source_pdf_path=source_pdf_path,
        target_pdf_path=target_pdf_path,
        ocr_mode="force",
        tesseract_language="por",
        ocr_quality="ebook",
    )

    executed_command = subprocess_run_mock.call_args.args[0]

    assert "--force-ocr" in executed_command
    assert "--skip-text" not in executed_command
    assert "--deskew" in executed_command
    assert "--oversample" in executed_command
    assert "400" in executed_command
    assert "--tesseract-pagesegmode" in executed_command
    assert "6" in executed_command
    assert "--pdf-renderer" in executed_command
    assert "hocr" in executed_command


def test_apply_ocr_to_pdf_builds_aggressive_command_without_rotate_pages(monkeypatch, tmp_path):
    subprocess_run_mock = Mock()
    monkeypatch.setattr(pdf_processor.subprocess, "run", subprocess_run_mock)

    source_pdf_path = tmp_path / "entrada.pdf"
    target_pdf_path = tmp_path / "saida.pdf"
    source_pdf_path.write_bytes(b"%PDF-1.4 fake")

    apply_ocr_to_pdf(
        source_pdf_path=source_pdf_path,
        target_pdf_path=target_pdf_path,
        ocr_mode="force",
        tesseract_language="por",
        ocr_quality="aggressive",
    )

    executed_command = subprocess_run_mock.call_args.args[0]

    assert "--force-ocr" in executed_command
    assert "--deskew" in executed_command
    assert "--clean" in executed_command
    assert "--clean-final" in executed_command
    assert "--rotate-pages" not in executed_command
    assert "--remove-background" not in executed_command