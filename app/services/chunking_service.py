import re

from app.services.pdf_service import extract_text


DEFAULT_CHUNK_SIZE = 400
DEFAULT_OVERLAP = 80


# ---------------------------------------------------------
# HELPERS
# ---------------------------------------------------------

def count_words(text: str) -> int:
    return len(re.findall(r"\S+", text))


# ---------------------------------------------------------
# MAIN CHUNKING
# ---------------------------------------------------------

def chunk_pages(
    pages: list[dict],
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    overlap: int = DEFAULT_OVERLAP,
) -> list[dict]:

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