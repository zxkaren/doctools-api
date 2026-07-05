import re


URL_PATTERN = re.compile(
    r"\b(?:https?://|www\.)\S+",
    re.IGNORECASE,
)

EMAIL_PATTERN = re.compile(
    r"\b[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+\b"
)

EMOJI_PATTERN = re.compile(
    "["
    "\U0001F1E6-\U0001F1FF"
    "\U0001F300-\U0001F5FF"
    "\U0001F600-\U0001F64F"
    "\U0001F680-\U0001F6FF"
    "\U0001F700-\U0001F77F"
    "\U0001F780-\U0001F7FF"
    "\U0001F800-\U0001F8FF"
    "\U0001F900-\U0001F9FF"
    "\U0001FA00-\U0001FA6F"
    "\U0001FA70-\U0001FAFF"
    "\u2600-\u26FF"
    "\u2700-\u27BF"
    "]+",
    flags=re.UNICODE,
)

PAGE_NUMBER_PATTERNS = [
    re.compile(r"^\d+$"),
    re.compile(r"^-+\s*\d+\s*-+$"),
    re.compile(r"^(página|pagina|page)\s+\d+(\s+de\s+\d+)?$", re.IGNORECASE),
    re.compile(r"^\d+\s*/\s*\d+$"),
]

IMAGE_CAPTION_PATTERNS = [
    re.compile(
        r"^(figura|fig\.|imagem|foto|ilustração|ilustracao)\s*\d+"
        r"(\s*[:.\-–—]\s*|\s+).+",
        re.IGNORECASE,
    ),
    re.compile(
        r"^(figure|fig\.|image|photo|illustration)\s*\d+"
        r"(\s*[:.\-–—]\s*|\s+).+",
        re.IGNORECASE,
    ),
]

FOOTNOTE_MARKER_PATTERN = re.compile(
    r"(?<!\w)[¹²³⁴⁵⁶⁷⁸⁹⁰]+(?!\w)|(?<!\w)\[\d+\](?!\w)"
)


def is_page_number_line(text_line: str) -> bool:
    normalized_text_line = text_line.strip()

    return any(
        page_number_pattern.match(normalized_text_line)
        for page_number_pattern in PAGE_NUMBER_PATTERNS
    )


def is_image_caption_line(text_line: str) -> bool:
    normalized_text_line = text_line.strip()

    return any(
        image_caption_pattern.match(normalized_text_line)
        for image_caption_pattern in IMAGE_CAPTION_PATTERNS
    )


def clean_text_line(text_line: str) -> str:
    cleaned_text_line = URL_PATTERN.sub("", text_line)
    cleaned_text_line = EMAIL_PATTERN.sub("", cleaned_text_line)
    cleaned_text_line = EMOJI_PATTERN.sub("", cleaned_text_line)
    cleaned_text_line = FOOTNOTE_MARKER_PATTERN.sub("", cleaned_text_line)
    cleaned_text_line = re.sub(r"[ \t]+", " ", cleaned_text_line)

    return cleaned_text_line.strip()


def normalize_paragraph_spacing(text_content: str) -> str:
    normalized_text_content = re.sub(r"\n{3,}", "\n\n", text_content)
    normalized_text_content = re.sub(r"[ \t]+\n", "\n", normalized_text_content)

    return normalized_text_content.strip()


def normalize_until_stable(text_content: str) -> str:
    normalized_text_content = normalize_paragraph_spacing(text_content)

    if normalized_text_content == text_content:
        return normalized_text_content

    return normalize_until_stable(normalized_text_content)


def clean_extracted_text(text_content: str) -> str:
    """
    Resumo:
        Limpa o texto extraído dos documentos, removendo elementos que não fazem
        parte do conteúdo principal, sem remover pontuação útil para leitura.

    Parâmetros:
        text_content (str): texto bruto extraído de PDF, DOCX ou PPTX.

    Retorno:
        str: texto limpo e pronto para download ou consumo por outra API.
    """
    if not text_content:
        return ""

    cleaned_text_lines = []

    for text_line in text_content.splitlines():
        if is_page_number_line(text_line):
            continue

        if is_image_caption_line(text_line):
            continue

        cleaned_text_line = clean_text_line(text_line)

        if cleaned_text_line:
            cleaned_text_lines.append(cleaned_text_line)

    cleaned_text_content = "\n".join(cleaned_text_lines)

    return normalize_until_stable(cleaned_text_content)