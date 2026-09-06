from pathlib import Path
import re
import fitz

UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_pdf(file, filename: str) -> str:
    file_path = UPLOAD_DIR / filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path)


def extract_text(file_path: str) -> list[dict]:
    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        blocks = page.get_text("blocks")

        text_blocks = []

        for block in blocks:
            x0, y0, x1, y1, text, *_ = block

            if not text.strip():
                continue

            # Ignore page numbers at the bottom
            if y0 > page.rect.height - 30:
                continue

            text_blocks.append({"x0": x0, "y0": y0, "x1": x1, "y1": y1, "text": text})

        if not text_blocks:
            continue

        # Find the approximate middle of the page
        page_midpoint = page.rect.width / 2

        left_column = []
        right_column = []

        for block in text_blocks:
            block_center = (block["x0"] + block["x1"]) / 2

            if block_center < page_midpoint:
                left_column.append(block)
            else:
                right_column.append(block)

        # Read each column from top to bottom
        left_column.sort(key=lambda block: block["y0"])
        right_column.sort(key=lambda block: block["y0"])

        ordered_blocks = left_column + right_column

        text = "\n".join(block["text"] for block in ordered_blocks)

        text = clean_text(text)

        if text:
            pages.append({"page_number": page_number, "text": text})

    document.close()

    return pages


def clean_text(text: str) -> str:
    # Normalize spaces
    text = re.sub(r"[ \t]+", " ", text)

    # Join words split across lines:
    # "compu-\ntation" -> "computation"
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)

    # Normalize excessive blank lines
    text = re.sub(r"\n\s*\n+", "\n\n", text)

    # Convert remaining newlines to spaces
    text = re.sub(r"\s*\n\s*", " ", text)

    return text.strip()
