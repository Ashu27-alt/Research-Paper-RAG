"""Convert extracted PDF blocks into retrieval-sized, overlapping text chunks."""

import re

from app.services.pdf_service import extract_text


DEFAULT_CHUNK_SIZE = 400
DEFAULT_OVERLAP = 80


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def count_words(text: str) -> int:
    """Count whitespace-delimited words in ``text``.

    Args:
        text: Text whose words should be counted.

    Returns:
        Number of non-whitespace tokens.
    """
    return len(re.findall(r"\S+", text))


# ---------------------------------------------------------
# MAIN CHUNKING
# ---------------------------------------------------------

def chunk_pages(
    pages: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict]:
    """Chunk every extracted page while retaining page metadata.

    Args:
        pages: Page dictionaries produced by ``extract_text``.
        chunk_size: Maximum target word count for each chunk.
        overlap: Maximum number of words carried into the next chunk.

    Returns:
        Chunk dictionaries containing page number, index, section, types, and text.

    Raises:
        ValueError: If ``overlap`` is at least ``chunk_size``.
    """

    if overlap >= chunk_size:
        raise ValueError(
            "overlap must be smaller than chunk_size"
        )

    chunks = []

    for page in pages:

        chunks.extend(
            chunk_page(
                page=page,
                chunk_size=chunk_size,
                overlap=overlap,
            )
        )

    return chunks


def chunk_page(
    page: dict,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Split one page's typed blocks into coherent, bounded-size chunks.

    Args:
        page: Extracted page with ``page_number`` and ordered ``blocks``.
        chunk_size: Maximum target word count for a chunk.
        overlap: Maximum words retained between adjacent text chunks.

    Returns:
        Chunk dictionaries for the page; tables are returned as standalone chunks.
    """

    page_number = page["page_number"]
    blocks = page.get("blocks", [])

    if not blocks:
        return []

    chunks = []

    current_blocks = []
    current_word_count = 0
    current_section = None
    chunk_index = 0

    def flush_current():
        """Append accumulated blocks as one chunk and reset the accumulator."""

        nonlocal current_blocks
        nonlocal current_word_count
        nonlocal chunk_index

        if not current_blocks:
            return

        chunks.append(
            create_chunk(
                page_number=page_number,
                chunk_index=chunk_index,
                section=current_section,
                blocks=current_blocks,
            )
        )

        chunk_index += 1
        current_blocks = []
        current_word_count = 0

    for block in blocks:

        text = block.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        block_type = block.get(
            "type",
            "text",
        )

        # -----------------------------------------------------
        # TABLE
        # -----------------------------------------------------

        # Tables remain standalone chunks.
        if block_type == "table":

            flush_current()

            chunks.append(
                create_chunk(
                    page_number=page_number,
                    chunk_index=chunk_index,
                    section=current_section,
                    blocks=[block],
                )
            )

            chunk_index += 1

            continue

        # -----------------------------------------------------
        # HEADING
        # -----------------------------------------------------

        if block_type == "heading":

            # Finish previous chunk first.
            flush_current()

            # Update section.
            current_section = text

            # Keep heading with the content that follows it.
            current_blocks = [block]

            current_word_count = count_words(text)

            continue

        word_count = count_words(text)

        # -----------------------------------------------------
        # LARGE BLOCK
        # -----------------------------------------------------

        if word_count > chunk_size:

            flush_current()

            large_chunks = split_large_block(
                block=block,
                page_number=page_number,
                chunk_index=chunk_index,
                section=current_section,
                chunk_size=chunk_size,
                overlap=overlap,
            )

            chunks.extend(large_chunks)

            chunk_index += len(large_chunks)

            continue

        # -----------------------------------------------------
        # CHUNK SIZE EXCEEDED
        # -----------------------------------------------------

        if (
            current_blocks
            and current_word_count + word_count
            > chunk_size
        ):

            previous_blocks = current_blocks.copy()

            flush_current()

            overlap_blocks = build_overlap(
                previous_blocks,
                overlap,
            )

            current_blocks = overlap_blocks

            current_word_count = sum(
                count_words(
                    block.get("text", "")
                )
                for block in current_blocks
            )

        current_blocks.append(block)

        current_word_count += word_count

    # Final chunk.
    flush_current()

    return chunks


# ---------------------------------------------------------
# CHUNK CREATION
# ---------------------------------------------------------

def create_chunk(
    page_number: int,
    chunk_index: int,
    section: str | None,
    blocks: list[dict],
) -> dict:
    """Build the persisted representation for a group of PDF blocks.

    Args:
        page_number: One-based PDF page number.
        chunk_index: Zero-based chunk position within the page.
        section: Most recent heading, if one applies.
        blocks: Ordered text, heading, caption, or table blocks.

    Returns:
        A chunk dictionary ready for embedding and database storage.
    """

    text_parts = []
    block_types = []

    for block in blocks:

        text = block.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        text_parts.append(text)

        block_type = block.get(
            "type",
            "text",
        )

        if block_type not in block_types:
            block_types.append(block_type)

    return {
        "page_number": page_number,
        "chunk_index": chunk_index,
        "section": section,
        "block_types": block_types,
        "text": "\n\n".join(text_parts),
    }


# ---------------------------------------------------------
# LARGE BLOCK SPLITTING
# ---------------------------------------------------------

def split_large_block(
    block: dict,
    page_number: int,
    chunk_index: int,
    section: str | None,
    chunk_size: int,
    overlap: int,
) -> list[dict]:
    """Split an oversized text block at sentence boundaries.

    Args:
        block: Text block too large for one chunk.
        page_number: One-based PDF page number.
        chunk_index: Index assigned to the first generated chunk.
        section: Most recent heading, if one applies.
        chunk_size: Maximum target word count per generated chunk.
        overlap: Maximum words of trailing sentences repeated in the next chunk.

    Returns:
        Sentence-aligned chunk dictionaries, or an empty list for blank text.
    """

    text = block.get(
        "text",
        "",
    ).strip()

    if not text:
        return []

    # Split at sentence boundaries.
    sentences = re.split(
        r"(?<=[.!?])\s+",
        text,
    )

    chunks = []

    current_sentences = []
    current_word_count = 0
    local_index = 0

    for sentence in sentences:

        sentence = sentence.strip()

        if not sentence:
            continue

        sentence_words = count_words(sentence)

        if (
            current_sentences
            and current_word_count + sentence_words
            > chunk_size
        ):

            chunks.append(
                {
                    "page_number": page_number,
                    "chunk_index": (
                        chunk_index + local_index
                    ),
                    "section": section,
                    "block_types": ["text"],
                    "text": " ".join(
                        current_sentences
                    ),
                }
            )

            local_index += 1

            # Sentence-level overlap.
            current_sentences = (
                get_overlap_sentences(
                    current_sentences,
                    overlap,
                )
            )

            current_word_count = sum(
                count_words(sentence)
                for sentence in current_sentences
            )

        current_sentences.append(sentence)

        current_word_count += sentence_words

    # Final chunk.
    if current_sentences:

        chunks.append(
            {
                "page_number": page_number,
                "chunk_index": (
                    chunk_index + local_index
                ),
                "section": section,
                "block_types": ["text"],
                "text": " ".join(
                    current_sentences
                ),
            }
        )

    return chunks


# ---------------------------------------------------------
# SENTENCE OVERLAP
# ---------------------------------------------------------

def get_overlap_sentences(
    sentences: list[str],
    overlap: int,
) -> list[str]:
    """Select trailing sentences that fit inside an overlap word budget.

    Args:
        sentences: Sentences from the previous chunk.
        overlap: Maximum words to carry forward.

    Returns:
        The selected suffix of sentences in original order.
    """

    result = []
    word_count = 0

    for sentence in reversed(sentences):

        sentence_words = count_words(sentence)

        if (
            word_count + sentence_words
            > overlap
        ):
            break

        result.insert(
            0,
            sentence,
        )

        word_count += sentence_words

    return result


# ---------------------------------------------------------
# BLOCK OVERLAP
# ---------------------------------------------------------

def build_overlap(
    blocks: list[dict],
    overlap: int,
) -> list[dict]:
    """Select trailing non-table blocks that fit inside an overlap budget.

    Args:
        blocks: Blocks from the previous chunk.
        overlap: Maximum words to carry forward.

    Returns:
        The selected suffix of blocks in original order.
    """

    result = []
    word_count = 0

    for block in reversed(blocks):

        text = block.get(
            "text",
            "",
        ).strip()

        if not text:
            continue

        # Never carry tables into another chunk.
        if block.get("type") == "table":
            continue

        block_words = count_words(text)

        if (
            word_count + block_words
            > overlap
        ):
            break

        result.insert(
            0,
            block,
        )

        word_count += block_words

    return result


# ---------------------------------------------------------
# LOCAL TEST
# ---------------------------------------------------------

if __name__ == "__main__":

    pdf_path = "uploads/imageMAE.pdf"

    pages = extract_text(pdf_path)

    chunks = chunk_pages(pages)

    print(
        f"\nTotal chunks: {len(chunks)}"
    )

    for chunk in chunks:

        print("\n" + "=" * 80)

        print(
            f"PAGE: {chunk['page_number']} | "
            f"CHUNK: {chunk['chunk_index']} | "
            f"SECTION: {chunk['section']} | "
            f"TYPES: {chunk['block_types']}"
        )

        print("-" * 80)

        print(chunk["text"])
