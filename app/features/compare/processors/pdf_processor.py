from dataclasses import dataclass
from difflib import SequenceMatcher
from pathlib import Path

import fitz


ADD_HIGHLIGHT_COLOR = (0, 0.45, 1)
DELETE_MARK_COLOR = (1, 0, 0)

COMMENT_MARGIN_RIGHT = 18
COMMENT_MARGIN_TOP = 24
COMMENT_MARGIN_BOTTOM = 24
COMMENT_VERTICAL_GAP = 20

DELETE_INSERTION_MARKER_WIDTH = 14

SUMMARY_PAGE_WIDTH = 595
SUMMARY_PAGE_HEIGHT = 842


@dataclass
class PdfWord:
    page_index: int
    text: str
    normalized_text: str
    rect: fitz.Rect


@dataclass
class DeletionChange:
    anchor_index: int
    deleted_text: str
    deleted_count: int
    marker_words: list[PdfWord]


@dataclass
class PdfComparison:
    added_words: list[PdfWord]
    deleted_changes: list[DeletionChange]


def normalize_word_text(word_text: str) -> str:
    return word_text.strip().casefold()


def build_pdf_words(file_path: Path) -> list[PdfWord]:
    """
    Resumo:
        Extrai as palavras de um PDF preservando página, texto e posição.

    Parâmetros:
        file_path (Path): caminho do arquivo PDF que será lido.

    Retorno:
        list[PdfWord]: lista de palavras extraídas com suas posições no documento.
    """
    pdf_words = []
    document = fitz.open(file_path)

    try:
        for page_index in range(document.page_count):
            page = document[page_index]
            extracted_words = page.get_text("words")

            for extracted_word in extracted_words:
                word_text = extracted_word[4].strip()

                if not word_text:
                    continue

                word_rect = fitz.Rect(
                    extracted_word[0],
                    extracted_word[1],
                    extracted_word[2],
                    extracted_word[3],
                )

                pdf_words.append(
                    PdfWord(
                        page_index=page_index,
                        text=word_text,
                        normalized_text=normalize_word_text(word_text),
                        rect=word_rect,
                    )
                )

        return pdf_words

    finally:
        document.close()


def build_deleted_text(deleted_words: list[PdfWord]) -> str:
    return " ".join(deleted_word.text for deleted_word in deleted_words)


def build_pdf_comparison(
    original_words: list[PdfWord],
    modified_words: list[PdfWord],
) -> PdfComparison:
    """
    Resumo:
        Compara as palavras do PDF original com as palavras do PDF modificado.

    Parâmetros:
        original_words (list[PdfWord]): palavras extraídas do PDF original.
        modified_words (list[PdfWord]): palavras extraídas do PDF modificado.

    Retorno:
        PdfComparison: palavras adicionadas e exclusões identificadas.
    """
    original_tokens = [word.normalized_text for word in original_words]
    modified_tokens = [word.normalized_text for word in modified_words]

    sequence_matcher = SequenceMatcher(
        None,
        original_tokens,
        modified_tokens,
        autojunk=False,
    )

    added_words = []
    deleted_changes = []

    for operation, original_start, original_end, modified_start, modified_end in sequence_matcher.get_opcodes():
        if operation == "equal":
            continue

        modified_change_words = modified_words[modified_start:modified_end]

        if operation in {"insert", "replace"}:
            added_words.extend(modified_change_words)

        if operation in {"delete", "replace"}:
            deleted_words = original_words[original_start:original_end]

            if deleted_words:
                deleted_changes.append(
                    DeletionChange(
                        anchor_index=modified_start,
                        deleted_text=build_deleted_text(deleted_words),
                        deleted_count=len(deleted_words),
                        marker_words=modified_change_words,
                    )
                )

    return PdfComparison(
        added_words=added_words,
        deleted_changes=deleted_changes,
    )


def find_deletion_anchor(
    modified_words: list[PdfWord],
    anchor_index: int,
) -> PdfWord | None:
    if not modified_words:
        return None

    if anchor_index < len(modified_words):
        return modified_words[anchor_index]

    return modified_words[-1]


def add_highlight_to_added_words(document: fitz.Document, added_words: list[PdfWord]) -> None:
    for added_word in added_words:
        page = document[added_word.page_index]
        highlight = page.add_highlight_annot(added_word.rect)
        highlight.set_colors(stroke=ADD_HIGHLIGHT_COLOR)
        highlight.set_opacity(0.35)
        highlight.update()


def underline_marker_word(page: fitz.Page, marker_word: PdfWord) -> None:
    underline_y = marker_word.rect.y1 + 1

    page.draw_line(
        fitz.Point(marker_word.rect.x0, underline_y),
        fitz.Point(marker_word.rect.x1, underline_y),
        color=DELETE_MARK_COLOR,
        width=1.2,
        overlay=True,
    )


def underline_replacement_words(page: fitz.Page, marker_words: list[PdfWord]) -> None:
    for marker_word in marker_words:
        underline_marker_word(page, marker_word)


def build_insertion_marker_points(
    page: fitz.Page,
    anchor_word: PdfWord,
    anchor_index: int,
    modified_words_count: int,
) -> tuple[fitz.Point, fitz.Point]:
    marker_y = anchor_word.rect.y1 + 1

    if anchor_index < modified_words_count:
        marker_x1 = max(anchor_word.rect.x0 - 2, COMMENT_MARGIN_RIGHT)
        marker_x0 = max(marker_x1 - DELETE_INSERTION_MARKER_WIDTH, COMMENT_MARGIN_RIGHT)
    else:
        marker_x0 = min(
            anchor_word.rect.x1 + 2,
            page.rect.width - COMMENT_MARGIN_RIGHT,
        )
        marker_x1 = min(
            marker_x0 + DELETE_INSERTION_MARKER_WIDTH,
            page.rect.width - COMMENT_MARGIN_RIGHT,
        )

    if marker_x1 <= marker_x0:
        marker_x0 = anchor_word.rect.x0
        marker_x1 = min(anchor_word.rect.x1, marker_x0 + DELETE_INSERTION_MARKER_WIDTH)

    return fitz.Point(marker_x0, marker_y), fitz.Point(marker_x1, marker_y)


def add_insertion_deletion_marker(
    page: fitz.Page,
    anchor_word: PdfWord,
    anchor_index: int,
    modified_words_count: int,
) -> None:
    line_start, line_end = build_insertion_marker_points(
        page,
        anchor_word,
        anchor_index,
        modified_words_count,
    )

    page.draw_line(
        line_start,
        line_end,
        color=DELETE_MARK_COLOR,
        width=1.2,
        overlay=True,
    )


def build_comment_point(
    page: fitz.Page,
    anchor_rect: fitz.Rect,
    used_comment_points: list[fitz.Point],
) -> fitz.Point:
    comment_x = page.rect.width - COMMENT_MARGIN_RIGHT
    comment_y = min(
        max(anchor_rect.y0, COMMENT_MARGIN_TOP),
        page.rect.height - COMMENT_MARGIN_BOTTOM,
    )

    comment_point = fitz.Point(comment_x, comment_y)

    while any(abs(comment_point.y - used_point.y) < COMMENT_VERTICAL_GAP for used_point in used_comment_points):
        comment_y += COMMENT_VERTICAL_GAP

        if comment_y > page.rect.height - COMMENT_MARGIN_BOTTOM:
            comment_y = COMMENT_MARGIN_TOP
            break

        comment_point = fitz.Point(comment_x, comment_y)

    used_comment_points.append(comment_point)

    return comment_point


def add_deletion_comment_annotation(
    page: fitz.Page,
    deletion_change: DeletionChange,
    comment_point: fitz.Point,
) -> None:
    comment_text = f"delete: {deletion_change.deleted_text}"

    comment_annotation = page.add_text_annot(
        comment_point,
        comment_text,
    )
    comment_annotation.set_info(
        title="DocTools API",
        subject="Delete",
        content=comment_text,
    )
    comment_annotation.set_colors(
        stroke=DELETE_MARK_COLOR,
    )
    comment_annotation.update()


def add_orphan_deletion_comment(
    document: fitz.Document,
    deletion_change: DeletionChange,
    used_comments_by_page: dict[int, list[fitz.Point]],
) -> None:
    if document.page_count == 0:
        page = document.new_page()
    else:
        page = document[0]

    used_comment_points = used_comments_by_page.setdefault(0, [])
    anchor_rect = fitz.Rect(
        page.rect.width - COMMENT_MARGIN_RIGHT,
        COMMENT_MARGIN_TOP,
        page.rect.width - COMMENT_MARGIN_RIGHT,
        COMMENT_MARGIN_TOP + 10,
    )

    comment_point = build_comment_point(
        page,
        anchor_rect,
        used_comment_points,
    )

    add_deletion_comment_annotation(
        page,
        deletion_change,
        comment_point,
    )


def add_deletion_marker(
    document: fitz.Document,
    modified_words: list[PdfWord],
    deletion_change: DeletionChange,
    used_comments_by_page: dict[int, list[fitz.Point]],
) -> None:
    anchor_word = find_deletion_anchor(modified_words, deletion_change.anchor_index)

    if anchor_word is None:
        add_orphan_deletion_comment(
            document,
            deletion_change,
            used_comments_by_page,
        )
        return

    page = document[anchor_word.page_index]

    if deletion_change.marker_words:
        underline_replacement_words(page, deletion_change.marker_words)
    else:
        add_insertion_deletion_marker(
            page,
            anchor_word,
            deletion_change.anchor_index,
            len(modified_words),
        )

    used_comment_points = used_comments_by_page.setdefault(anchor_word.page_index, [])
    comment_point = build_comment_point(
        page,
        anchor_word.rect,
        used_comment_points,
    )

    add_deletion_comment_annotation(
        page,
        deletion_change,
        comment_point,
    )


def add_deletion_markers(
    document: fitz.Document,
    modified_words: list[PdfWord],
    deleted_changes: list[DeletionChange],
) -> None:
    used_comments_by_page = {}

    for deletion_change in deleted_changes:
        add_deletion_marker(
            document,
            modified_words,
            deletion_change,
            used_comments_by_page,
        )


def build_summary_table(added_count: int, deleted_count: int) -> dict[str, int]:
    total_changes = added_count + deleted_count

    return {
        "add": added_count,
        "delete": deleted_count,
        "total_changes": total_changes,
    }


def add_summary_page(document: fitz.Document, summary_table: dict[str, int]) -> None:
    summary_page = document.new_page(
        width=SUMMARY_PAGE_WIDTH,
        height=SUMMARY_PAGE_HEIGHT,
    )

    summary_page.insert_text(
        fitz.Point(50, 60),
        "Summary Table",
        fontsize=18,
    )

    table_left = 50
    table_top = 100
    row_height = 32
    first_column_width = 180
    second_column_width = 120

    table_rows = [
        ("add", summary_table["add"]),
        ("delete", summary_table["delete"]),
        ("total changes", summary_table["total_changes"]),
    ]

    for row_index, row_data in enumerate(table_rows):
        row_top = table_top + row_index * row_height

        first_cell = fitz.Rect(
            table_left,
            row_top,
            table_left + first_column_width,
            row_top + row_height,
        )
        second_cell = fitz.Rect(
            table_left + first_column_width,
            row_top,
            table_left + first_column_width + second_column_width,
            row_top + row_height,
        )

        summary_page.draw_rect(first_cell)
        summary_page.draw_rect(second_cell)

        summary_page.insert_text(
            fitz.Point(first_cell.x0 + 8, first_cell.y0 + 21),
            row_data[0],
            fontsize=11,
        )

        summary_page.insert_text(
            fitz.Point(second_cell.x0 + 8, second_cell.y0 + 21),
            str(row_data[1]),
            fontsize=11,
        )


def save_processed_pdf(document: fitz.Document, target_path: Path) -> None:
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if target_path.exists():
        target_path.unlink()

    document.save(
        target_path,
        garbage=4,
        deflate=True,
    )


def compare_files(original_path: Path, modified_path: Path, target_path: Path) -> dict:
    """
    Resumo:
        Compara dois arquivos PDF e gera um terceiro PDF baseado no arquivo modificado.

    Parâmetros:
        original_path (Path): caminho do PDF original.
        modified_path (Path): caminho do PDF modificado.
        target_path (Path): caminho onde o PDF comparado será salvo.

    Retorno:
        dict: contrato com caminho do arquivo processado e tabela de resumo.
    """
    original_words = build_pdf_words(original_path)
    modified_words = build_pdf_words(modified_path)
    pdf_comparison = build_pdf_comparison(original_words, modified_words)

    document = fitz.open(modified_path)

    try:
        add_highlight_to_added_words(document, pdf_comparison.added_words)
        add_deletion_markers(
            document,
            modified_words,
            pdf_comparison.deleted_changes,
        )

        deleted_count = sum(
            deletion_change.deleted_count
            for deletion_change in pdf_comparison.deleted_changes
        )

        summary_table = build_summary_table(
            added_count=len(pdf_comparison.added_words),
            deleted_count=deleted_count,
        )

        add_summary_page(document, summary_table)
        save_processed_pdf(document, target_path)

        return {
            "processed_path": target_path,
            "summary_table": summary_table,
        }

    finally:
        document.close()