"""PDF persistence and layout-aware text/table extraction helpers."""

import re
import fitz
import os

from fastapi import UploadFile


UPLOAD_DIR = "uploads"


async def save_pdf(
    file: UploadFile,
    filename: str,
) -> str:
    """Save an uploaded PDF to the configured local upload directory.

    Args:
        file: FastAPI upload object containing PDF bytes.
        filename: Filename to use below ``UPLOAD_DIR``.

    Returns:
        Relative local path of the saved PDF.
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    file_path = os.path.join(
        UPLOAD_DIR,
        filename,
    )

    contents = await file.read()

    with open(file_path, "wb") as buffer:
        buffer.write(contents)

    return file_path


# ---------------------------------------------------------
# BASIC HELPERS
# ---------------------------------------------------------

def normalize_text(text: str) -> str:
    """Normalize whitespace while preserving readable text.

    Args:
        text: Raw text extracted from a PDF span or block.

    Returns:
        Trimmed text with normalized spaces and excessive blank lines removed.
    """
    text = text.replace("\u00a0", " ")
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def rects_overlap(a, b) -> bool:
    """Return whether two ``(x0, y0, x1, y1)`` rectangles overlap.

    Args:
        a: Bounding box of the first element.
        b: Bounding box of the second element.

    Returns:
        ``True`` when the rectangles share any area.
    """
    """
    Check whether two bounding boxes overlap.
    """
    ax0, ay0, ax1, ay1 = a
    bx0, by0, bx1, by1 = b

    return not (
        ax1 <= bx0
        or ax0 >= bx1
        or ay1 <= by0
        or ay0 >= by1
    )


def block_overlaps_tables(block: dict, table_bboxes: list) -> bool:
    """Check whether a text block overlaps an already extracted table.

    Args:
        block: Extracted block containing a ``bbox`` field.
        table_bboxes: Bounding boxes for tables on the same page.

    Returns:
        ``True`` if the block intersects at least one table.
    """
    bbox = block["bbox"]

    return any(
        rects_overlap(bbox, table_bbox)
        for table_bbox in table_bboxes
    )


# ---------------------------------------------------------
# TEXT BLOCK EXTRACTION
# ---------------------------------------------------------

def extract_page_blocks(page) -> list[dict]:
    """Extract structured non-table text blocks from one PyMuPDF page.

    Keeps useful layout information such as:
    - text
    - bounding box
    - font size
    - font
    - bold
    Args:
        page: PyMuPDF page object to inspect.

    Returns:
        Text block dictionaries with content, geometry, font data, and type.
    """

    data = page.get_text("dict")

    blocks = []

    for block_number, raw_block in enumerate(data.get("blocks", [])):

        # Ignore images.
        if raw_block.get("type") != 0:
            continue

        lines = raw_block.get("lines", [])

        text_parts = []

        font_sizes = []
        fonts = []
        bold_flags = []

        for line in lines:

            for span in line.get("spans", []):

                text = span.get("text", "").strip()

                if not text:
                    continue

                text_parts.append(text)

                font_sizes.append(
                    float(span.get("size", 0))
                )

                fonts.append(
                    span.get("font", "")
                )

                flags = span.get("flags", 0)

                # PyMuPDF flag 16 = bold.
                bold_flags.append(
                    bool(flags & 16)
                )

        text = " ".join(text_parts).strip()

        if not text:
            continue

        bbox = raw_block.get("bbox")

        if not bbox:
            continue

        x0, y0, x1, y1 = bbox

        blocks.append(
            {
                "text": normalize_text(text),
                "bbox": [x0, y0, x1, y1],
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "width": x1 - x0,
                "height": y1 - y0,
                "block_number": block_number,
                "font_size": (
                    sum(font_sizes) / len(font_sizes)
                    if font_sizes
                    else 0.0
                ),
                "max_font_size": (
                    max(font_sizes)
                    if font_sizes
                    else 0.0
                ),
                "fonts": fonts,
                "bold": any(bold_flags),
                "type": "text",
            }
        )

    return blocks


# ---------------------------------------------------------
# TABLE EXTRACTION
# ---------------------------------------------------------

def is_valid_table(rows: list[list]) -> bool:
    """Return whether extracted rows plausibly represent a data table.

    A table should:
    - contain at least 2 rows
    - contain at least 2 columns
    - not be mostly empty
    - contain some numeric information
    - avoid cells that look like paragraphs
    Args:
        rows: Cell values emitted by PyMuPDF's table extractor.

    Returns:
        ``True`` for multi-row, multi-column, mostly populated numeric tables.
    """

    if not rows or len(rows) < 2:
        return False

    num_cols = max(
        (len(row) for row in rows),
        default=0,
    )

    if num_cols < 2:
        return False

    total_cells = 0
    empty_cells = 0
    numeric_cells = 0

    for row in rows:

        for cell in row:

            total_cells += 1

            text = (
                ""
                if cell is None
                else str(cell).strip()
            )

            if not text:
                empty_cells += 1
                continue

            # A table cell containing a paragraph is
            # usually a false positive.
            if "\n" in text:
                return False

            if len(text) > 60:
                return False

            if re.search(r"\d", text):
                numeric_cells += 1

    if total_cells == 0:
        return False

    if empty_cells / total_cells > 0.4:
        return False

    numeric_ratio = numeric_cells / total_cells

    # Keep this threshold intentionally conservative.
    if numeric_ratio < 0.08:
        return False

    return True


def rows_to_markdown(rows: list[list]) -> str:
    """Convert extracted table rows into a padded Markdown table.

    Args:
        rows: Table rows, whose cells may be ``None`` or uneven in length.

    Returns:
        Markdown table text, or an empty string when no rows are supplied.
    """

    if not rows:
        return ""

    normalized_rows = []

    for row in rows:

        normalized = []

        for cell in row:

            if cell is None:
                cell = ""

            cell = str(cell).strip()

            # Keep Markdown valid.
            cell = cell.replace("|", "\\|")

            normalized.append(cell)

        normalized_rows.append(normalized)

    if not normalized_rows:
        return ""

    num_cols = max(
        len(row)
        for row in normalized_rows
    )

    # Pad rows to equal width.
    for row in normalized_rows:

        while len(row) < num_cols:
            row.append("")

    header = normalized_rows[0]

    lines = []

    lines.append(
        "| " + " | ".join(header) + " |"
    )

    lines.append(
        "| "
        + " | ".join(["---"] * num_cols)
        + " |"
    )

    for row in normalized_rows[1:]:

        lines.append(
            "| " + " | ".join(row) + " |"
        )

    return "\n".join(lines)


def extract_page_tables(page) -> list[dict]:
    """Extract validated tables from one PyMuPDF page.

    False page-sized detections are rejected.
    Args:
        page: PyMuPDF page object to inspect.

    Returns:
        Table block dictionaries containing Markdown text and geometry.
    """

    blocks = []

    try:
        table_finder = page.find_tables(
            strategy="text"
        )
    except Exception:
        return blocks

    page_width = page.rect.width
    page_height = page.rect.height

    for block_number, table in enumerate(
        table_finder.tables
    ):

        x0, y0, x1, y1 = table.bbox

        table_width = x1 - x0
        table_height = y1 - y0

        width_ratio = table_width / page_width
        height_ratio = table_height / page_height

        # Reject detections that effectively cover
        # the whole page.
        if (
            width_ratio > 0.90
            and height_ratio > 0.75
        ):
            continue

        try:
            rows = table.extract()
        except Exception:
            continue

        if not is_valid_table(rows):
            continue

        markdown = rows_to_markdown(rows)

        if not markdown:
            continue

        blocks.append(
            {
                "text": markdown,
                "bbox": [x0, y0, x1, y1],
                "x0": x0,
                "y0": y0,
                "x1": x1,
                "y1": y1,
                "width": table_width,
                "height": table_height,
                "block_number": -1000 - block_number,
                "font_size": 0.0,
                "max_font_size": 0.0,
                "bold": False,
                "fonts": [],
                "type": "table",
            }
        )

    return blocks


# ---------------------------------------------------------
# HEADER / FOOTER REMOVAL
# ---------------------------------------------------------

def remove_headers_and_footers(
    blocks: list[dict],
    page_height: float,
) -> list[dict]:
    """Remove page numbers and blocks in top/bottom page margins.

    Args:
        blocks: Text or table blocks from one page.
        page_height: Height of that page in PDF coordinates.

    Returns:
        Blocks that are likely document content rather than headers or footers.
    """

    top_limit = page_height * 0.05
    bottom_limit = page_height * 0.95

    cleaned = []

    for block in blocks:

        y0 = block["y0"]
        y1 = block["y1"]

        text = block["text"].strip()

        # Remove standalone page numbers.
        if re.fullmatch(
            r"\d+",
            text,
        ):
            continue

        # Remove header/footer blocks.
        if y1 <= top_limit:
            continue

        if y0 >= bottom_limit:
            continue

        cleaned.append(block)

    return cleaned


# ---------------------------------------------------------
# COLUMN DETECTION
# ---------------------------------------------------------

def is_two_column_layout(
    blocks: list[dict],
    page_width: float,
) -> bool:
    """Heuristically detect whether blocks form a two-column page layout.

    Args:
        blocks: Extracted blocks with horizontal bounding-box coordinates.
        page_width: Width of the page in PDF coordinates.

    Returns:
        ``True`` when blocks form distinct left and right narrow columns.
    """

    if len(blocks) < 5:
        return False

    page_center = page_width / 2

    left_blocks = []
    right_blocks = []

    narrow_blocks = 0

    for block in blocks:

        x0 = block["x0"]
        x1 = block["x1"]

        width = x1 - x0

        # Ignore extremely wide blocks.
        if width > page_width * 0.80:
            return False

        if width < page_width * 0.48:
            narrow_blocks += 1

        center = (x0 + x1) / 2

        if center < page_center:
            left_blocks.append(block)
        else:
            right_blocks.append(block)

    if len(left_blocks) < 2:
        return False

    if len(right_blocks) < 2:
        return False

    if narrow_blocks / len(blocks) < 0.60:
        return False

    # Ensure there is a reasonable gap.
    left_edge = max(
        block["x1"]
        for block in left_blocks
    )

    right_edge = min(
        block["x0"]
        for block in right_blocks
    )

    gap = right_edge - left_edge

    if gap < page_width * 0.03:
        return False

    return True


def order_blocks(
    blocks: list[dict],
    page_width: float,
) -> list[dict]:
    """Order blocks in natural reading order for one- or two-column pages.

    Args:
        blocks: Extracted blocks with ``x0`` and ``y0`` geometry.
        page_width: Width of the page in PDF coordinates.

    Returns:
        Sorted blocks; left column precedes right column for two-column pages.
    """

    if not blocks:
        return []

    if not is_two_column_layout(
        blocks,
        page_width,
    ):
        return sorted(
            blocks,
            key=lambda b: (
                b["y0"],
                b["x0"],
            ),
        )

    page_center = page_width / 2

    left = [
        block
        for block in blocks
        if (block["x0"] + block["x1"]) / 2
        < page_center
    ]

    right = [
        block
        for block in blocks
        if (block["x0"] + block["x1"]) / 2
        >= page_center
    ]

    left.sort(
        key=lambda b: (
            b["y0"],
            b["x0"],
        )
    )

    right.sort(
        key=lambda b: (
            b["y0"],
            b["x0"],
        )
    )

    return left + right


# ---------------------------------------------------------
# HEADING DETECTION
# ---------------------------------------------------------

NUMBERED_HEADING_RE = re.compile(
    r"^\d+(?:\.\d+)*\.?\s+\S+"
)

APPENDIX_HEADING_RE = re.compile(
    r"^[A-Z]\.\s+\S+"
)

COMMON_HEADINGS = {
    "abstract",
    "introduction",
    "related work",
    "approach",
    "experiments",
    "results",
    "discussion",
    "discussion and conclusion",
    "conclusion",
    "references",
    "implementation details",
    "transfer learning experiments",
}


def looks_like_numeric_chart_label(text: str) -> bool:
    """Detect chart labels that should not be treated as headings.

        10 20 30 40 50 60 70
        0 1 2 4 6 12 18 24 70
        100 200 400 800 1600
        66.1 linear probing

    These frequently appear as PDF text blocks around figures.

    Args:
        text: Candidate heading text.

    Returns:
        ``True`` when the text is predominantly numeric or axis-label-like.
    """

    text = text.strip()

    if not text:
        return True

    tokens = text.split()

    if len(tokens) < 2:
        return False

    numeric_tokens = 0

    for token in tokens:

        cleaned = token.rstrip("%,.")

        try:
            float(cleaned)
            numeric_tokens += 1
        except ValueError:
            pass

    numeric_ratio = numeric_tokens / len(tokens)

    # Mostly numeric text is not a heading.
    if numeric_ratio >= 0.60:
        return True

    # Patterns such as:
    # 66.1 linear probing
    # 83.2 fine-tuning
    if (
        len(tokens) <= 4
        and re.match(
            r"^\d+(?:\.\d+)?$",
            tokens[0],
        )
    ):
        return True

    return False


def is_heading(block: dict) -> bool:
    """Determine whether a text block is a short document section heading.

    Args:
        block: Text block produced by ``extract_page_blocks``.

    Returns:
        ``True`` for recognized, numbered, or appendix-style headings.
    """

    text = block["text"].strip()

    if not text:
        return False

    # Don't classify chart labels as headings.
    if looks_like_numeric_chart_label(text):
        return False

    # Very long blocks are prose.
    if len(text) > 180:
        return False

    normalized = text.lower().strip()

    # Exact common academic headings.
    if normalized in COMMON_HEADINGS:
        return True

    # Numbered sections.
    if NUMBERED_HEADING_RE.match(text):

        # Avoid accidentally treating a long sentence
        # beginning with a number as a heading.
        if len(text.split()) <= 15:
            return True

    # Appendix sections.
    if APPENDIX_HEADING_RE.match(text):

        if len(text.split()) <= 15:
            return True

    return False


def classify_blocks(
    blocks: list[dict],
) -> list[dict]:
    """Assign each block a semantic type for downstream chunking.

    Args:
        blocks: Ordered page blocks, including any extracted tables.

    Returns:
        Copies of blocks labeled as ``table``, ``caption``, ``heading``, or ``text``.
    """

    classified = []

    for block in blocks:

        block = block.copy()

        if block["type"] == "table":
            classified.append(block)
            continue

        text = block["text"].strip()

        # Captions.
        if re.match(
            r"^(Figure|Fig\.|Table)\s+\d+",
            text,
            re.IGNORECASE,
        ):
            block["type"] = "caption"

        elif is_heading(block):
            block["type"] = "heading"

        else:
            block["type"] = "text"

        classified.append(block)

    return classified


# ---------------------------------------------------------
# MAIN EXTRACTION FUNCTION
# ---------------------------------------------------------

def extract_text(file_path: str) -> list[dict]:
    """Extract layout-aware text, table, and semantic block data from a PDF.

    Args:
        file_path: Local filesystem path to the PDF to process.

    Returns:
        Page dictionaries containing one-based page numbers and ordered blocks.
    """

    document = fitz.open(file_path)

    pages = []

    for page_number, page in enumerate(
        document,
        start=1,
    ):

        # Extract tables first.
        table_blocks = extract_page_tables(page)

        table_bboxes = [
            block["bbox"]
            for block in table_blocks
        ]

        # Extract normal text.
        text_blocks = extract_page_blocks(page)

        # Don't duplicate text that belongs inside
        # an extracted table.
        text_blocks = [
            block
            for block in text_blocks
            if not block_overlaps_tables(
                block,
                table_bboxes,
            )
        ]

        blocks = text_blocks + table_blocks

        if not blocks:
            continue

        # Remove headers and footers.
        blocks = remove_headers_and_footers(
            blocks,
            page.rect.height,
        )

        # Reconstruct reading order.
        blocks = order_blocks(
            blocks,
            page.rect.width,
        )

        # Assign semantic block types.
        blocks = classify_blocks(blocks)

        pages.append(
            {
                "page_number": page_number,
                "blocks": blocks,
            }
        )

    document.close()

    return pages
