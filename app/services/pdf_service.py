from pathlib import Path
import fitz


UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)


async def save_pdf(file, filename: str) -> str:
    """
    Save uploaded PDF to the uploads directory.
    """

    file_path = UPLOAD_DIR / filename

    content = await file.read()

    with open(file_path, "wb") as f:
        f.write(content)

    return str(file_path)


def extract_text(file_path: str) -> list[dict]:
    """
    Extract text from every page of a PDF.

    Returns:
        [
            {
                "page_number": 1,
                "text": "..."
            },
            ...
        ]
    """

    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(document, start=1):
        text = page.get_text()

        pages.append({
            "page_number": page_number,
            "text": text
        })

    document.close()

    return pages