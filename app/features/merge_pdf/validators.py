from werkzeug.datastructures import FileStorage

from app.core.exceptions import BadRequestError


def validate_pdf_files(uploaded_files: list[FileStorage]) -> list[FileStorage]:
    valid_uploaded_files = [
        uploaded_file
        for uploaded_file in uploaded_files
        if uploaded_file and uploaded_file.filename
    ]

    if len(valid_uploaded_files) < 2:
        raise BadRequestError("envie ao menos 2 arquivos PDF para realizar o merge")

    for uploaded_file in valid_uploaded_files:
        if not uploaded_file.filename.lower().endswith(".pdf"):
            raise BadRequestError("a funcionalidade merge aceita somente arquivos PDF")

    return valid_uploaded_files


def validate_merge_order(
    uploaded_files: list[FileStorage],
    order_items: list[str],
) -> list[FileStorage]:
    """
    Resumo:
    Valida a ordem opcional dos arquivos e reorganiza os PDFs conforme a posição enviada.

    Parâmetros:
    uploaded_files: lista de arquivos PDF recebidos na requisição.
    order_items: lista de posições enviadas pelo front-end.

    Retorno:
    Lista de arquivos PDF na ordem final do merge.
    """
    if not order_items:
        return uploaded_files

    normalized_order_items = normalize_order_items(order_items)

    if len(normalized_order_items) != len(uploaded_files):
        raise BadRequestError("a ordem informada deve conter todos os arquivos enviados")

    ordered_positions = parse_order_positions(
        normalized_order_items=normalized_order_items,
        total_files=len(uploaded_files),
    )

    return [
        uploaded_files[ordered_position - 1]
        for ordered_position in ordered_positions
    ]


def normalize_order_items(order_items: list[str]) -> list[str]:
    if len(order_items) == 1:
        return [
            order_item.strip()
            for order_item in order_items[0].split(",")
            if order_item.strip()
        ]

    return [
        order_item.strip()
        for order_item in order_items
        if order_item.strip()
    ]


def parse_order_positions(
    normalized_order_items: list[str],
    total_files: int,
) -> list[int]:
    ordered_positions: list[int] = []

    for order_item in normalized_order_items:
        if not order_item.isdigit():
            raise BadRequestError("a ordem dos arquivos deve conter apenas números inteiros")

        ordered_position = int(order_item)

        if ordered_position < 1 or ordered_position > total_files:
            raise BadRequestError(
                f"a posição {ordered_position} não corresponde a nenhum arquivo enviado"
            )

        ordered_positions.append(ordered_position)

    repeated_positions = sorted(
        {
            ordered_position
            for ordered_position in ordered_positions
            if ordered_positions.count(ordered_position) > 1
        }
    )

    if repeated_positions:
        repeated_positions_text = ", ".join(
            str(ordered_position)
            for ordered_position in repeated_positions
        )
        raise BadRequestError(
            f"as posições {repeated_positions_text} foram repetidas na ordem do merge"
        )

    return ordered_positions