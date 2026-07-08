import re

from werkzeug.datastructures import FileStorage

from app.core.exceptions import BadRequestError


ALLOWED_SPLIT_TYPES = {"one_by_one", "pack"}
PAGE_RANGE_PATTERN = re.compile(r"^(\d+)\s*-\s*(\d+)$")
PAGE_NUMBER_PATTERN = re.compile(r"^\d+$")


def validate_pdf_file(files: list[FileStorage]) -> FileStorage:
    if not files:
        raise BadRequestError("envie 1 arquivo PDF para realizar o split")

    if len(files) > 1:
        raise BadRequestError("a funcionalidade split aceita somente 1 arquivo PDF por requisição")

    pdf_file = files[0]

    if not pdf_file.filename:
        raise BadRequestError("o arquivo enviado não possui nome válido")

    if not pdf_file.filename.lower().endswith(".pdf"):
        raise BadRequestError("a funcionalidade split aceita somente arquivos PDF")

    return pdf_file


def validate_split_type(split_type: str | None) -> str:
    if not split_type:
        raise BadRequestError("informe o tipo de split: one_by_one ou pack")

    normalized_split_type = split_type.strip().lower()

    if normalized_split_type not in ALLOWED_SPLIT_TYPES:
        raise BadRequestError("tipo de split inválido. Use one_by_one ou pack")

    return normalized_split_type


def validate_pack_fields(
    split_type: str,
    pack_numbers: list[str],
    pack_pages_items: list[str],
) -> dict[int, list[int]]:
    """
    Resumo:
        Valida os pares de campos pack/pages enviados no form-data e converte
        as páginas em listas numéricas, incluindo intervalos como 1-3.

    Parâmetros:
        split_type: tipo de split solicitado.
        pack_numbers: lista com os números dos packs.
        pack_pages_items: lista com os textos de páginas de cada pack.

    Retorno:
        Dicionário no formato {numero_do_pack: [paginas]}.
    """
    if split_type == "one_by_one":
        return {}

    normalized_pack_numbers = normalize_pack_numbers(pack_numbers)
    normalized_pack_pages_items = normalize_pack_pages_items(pack_pages_items)

    if not normalized_pack_numbers:
        raise BadRequestError("informe ao menos 1 campo pack")

    if not normalized_pack_pages_items:
        raise BadRequestError("informe ao menos 1 campo pages")

    if len(normalized_pack_numbers) != len(normalized_pack_pages_items):
        raise BadRequestError("cada campo pack deve possuir um campo pages correspondente")

    return parse_pack_fields(normalized_pack_numbers, normalized_pack_pages_items)


def normalize_pack_numbers(pack_numbers: list[str]) -> list[str]:
    if len(pack_numbers) == 1:
        return split_single_form_value(pack_numbers[0], allow_comma=True)

    return [pack_number.strip() for pack_number in pack_numbers if pack_number.strip()]


def normalize_pack_pages_items(pack_pages_items: list[str]) -> list[str]:
    if len(pack_pages_items) == 1:
        return split_single_form_value(pack_pages_items[0], allow_comma=False)

    return [pack_pages.strip() for pack_pages in pack_pages_items if pack_pages.strip()]


def split_single_form_value(form_value: str, allow_comma: bool) -> list[str]:
    cleaned_value = form_value.strip()

    if not cleaned_value:
        return []

    separators_pattern = r"[\n;]+"

    if allow_comma:
        separators_pattern = r"[\n;,]+"

    return [
        value.strip()
        for value in re.split(separators_pattern, cleaned_value)
        if value.strip()
    ]


def parse_pack_fields(
    pack_numbers: list[str],
    pack_pages_items: list[str],
) -> dict[int, list[int]]:
    parsed_packs: dict[int, list[int]] = {}
    used_pages: set[int] = set()

    for pack_number_text, pack_pages_text in zip(pack_numbers, pack_pages_items):
        pack_number = parse_pack_number(pack_number_text)

        if pack_number in parsed_packs:
            raise BadRequestError(f"o pack {pack_number} foi informado mais de uma vez")

        pack_pages = parse_pages_text(pack_pages_text)
        validate_repeated_pages_in_same_pack(pack_pages)

        repeated_pages = used_pages.intersection(pack_pages)

        if repeated_pages:
            repeated_pages_text = ", ".join(str(page) for page in sorted(repeated_pages))
            raise BadRequestError(
                f"as páginas {repeated_pages_text} foram informadas em mais de um pack"
            )

        parsed_packs[pack_number] = pack_pages
        used_pages.update(pack_pages)

    return parsed_packs


def parse_pack_number(pack_number_text: str) -> int:
    normalized_pack_number = pack_number_text.strip()

    if not PAGE_NUMBER_PATTERN.match(normalized_pack_number):
        raise BadRequestError("o campo pack deve receber apenas números inteiros maiores que zero")

    pack_number = int(normalized_pack_number)

    if pack_number <= 0:
        raise BadRequestError("o número do pack deve ser maior que zero")

    return pack_number


def parse_pages_text(pages_text: str) -> list[int]:
    """
    Resumo:
        Converte textos de páginas em lista numérica. Aceita páginas avulsas,
        intervalos e combinações entre eles.

    Parâmetros:
        pages_text: texto de páginas recebido no campo pages.

    Retorno:
        Lista de páginas em formato numérico.
    """
    if not pages_text or not pages_text.strip():
        raise BadRequestError("o campo pages não pode ficar vazio")

    pages: list[int] = []
    page_tokens = [token.strip() for token in pages_text.split(",") if token.strip()]

    if not page_tokens:
        raise BadRequestError("informe páginas válidas no campo pages")

    for page_token in page_tokens:
        pages.extend(parse_page_token(page_token))

    return pages


def parse_page_token(page_token: str) -> list[int]:
    range_match = PAGE_RANGE_PATTERN.match(page_token)

    if range_match:
        first_page = int(range_match.group(1))
        last_page = int(range_match.group(2))

        if first_page <= 0 or last_page <= 0:
            raise BadRequestError("as páginas devem ser maiores que zero")

        if first_page > last_page:
            raise BadRequestError("o intervalo de páginas deve estar em ordem crescente")

        return list(range(first_page, last_page + 1))

    if PAGE_NUMBER_PATTERN.match(page_token):
        page_number = int(page_token)

        if page_number <= 0:
            raise BadRequestError("as páginas devem ser maiores que zero")

        return [page_number]

    raise BadRequestError("formato de páginas inválido. Use exemplos como 1,2,3 ou 1-3")


def validate_repeated_pages_in_same_pack(pack_pages: list[int]) -> None:
    repeated_pages = sorted({page for page in pack_pages if pack_pages.count(page) > 1})

    if repeated_pages:
        repeated_pages_text = ", ".join(str(page) for page in repeated_pages)
        raise BadRequestError(f"as páginas {repeated_pages_text} foram repetidas no mesmo pack")


def validate_pages_within_pdf_range(packs: dict[int, list[int]], total_pages: int) -> None:
    invalid_pages = sorted(
        page
        for pack_pages in packs.values()
        for page in pack_pages
        if page > total_pages
    )

    if invalid_pages:
        invalid_pages_text = ", ".join(str(page) for page in invalid_pages)
        raise BadRequestError(
            f"as páginas {invalid_pages_text} não existem no PDF. "
            f"O documento possui {total_pages} página(s)"
        )