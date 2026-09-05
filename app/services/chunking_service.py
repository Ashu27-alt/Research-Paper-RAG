def chunk_text(text: str, page_number: int, chunk_size: int = 500, overlap: int = 100) -> list[dict]:

    if overlap >= chunk_size:
        raise ValueError("overlap must be smaller than chunk_size")

    words = text.split()

    if not words:
        return []

    chunks = []

    step = chunk_size - overlap

    chunk_index = 0

    for start in range(0, len(words), step):

        end = start + chunk_size

        chunk = " ".join(words[start:end])

        if not chunk:
            continue

        chunks.append(
            {"page_number": page_number, "chunk_index": chunk_index, "text": chunk}
        )

        chunk_index += 1

    return chunks
