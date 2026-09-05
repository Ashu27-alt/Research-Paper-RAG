import re


def split_into_sentences(text: str) -> list[str]:
    """
    Split text into sentences.
    """

    text = re.sub(r"\s+", " ", text).strip()

    if not text:
        return []

    sentences = re.split(r"(?<=[.!?])\s+", text)

    return [sentence.strip() for sentence in sentences if sentence.strip()]


def chunk_text(
    text: str, page_number: int, chunk_size: int = 500, overlap: int = 100
) -> list[dict]:
    """
    Create sentence-aware overlapping chunks.

    chunk_size:
        Maximum number of words in a chunk.

    overlap:
        Approximate number of words shared between
        consecutive chunks.
    """

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    sentences = split_into_sentences(text)

    if not sentences:
        return []

    chunks = []

    current_sentences = []
    current_word_count = 0

    chunk_index = 0

    for sentence in sentences:

        sentence_word_count = len(sentence.split())

        # If adding this sentence exceeds the limit,
        # finalize the current chunk.
        if current_sentences and current_word_count + sentence_word_count > chunk_size:

            chunk = " ".join(current_sentences)

            chunks.append(
                {"page_number": page_number, "chunk_index": chunk_index, "text": chunk}
            )

            chunk_index += 1

            # Build overlap from the end of the
            # previous chunk.
            overlap_sentences = []
            overlap_word_count = 0

            for previous_sentence in reversed(current_sentences):

                words = len(previous_sentence.split())

                if overlap_word_count + words > overlap:
                    break

                overlap_sentences.insert(0, previous_sentence)

                overlap_word_count += words

            current_sentences = overlap_sentences
            current_word_count = overlap_word_count

        current_sentences.append(sentence)
        current_word_count += sentence_word_count

    # Add final chunk
    if current_sentences:

        chunks.append(
            {
                "page_number": page_number,
                "chunk_index": chunk_index,
                "text": " ".join(current_sentences),
            }
        )

    return chunks
