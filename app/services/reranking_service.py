from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"

reranker = CrossEncoder(MODEL_NAME)


def rerank_chunks(
    question: str,
    chunks: list,
    top_k: int = 5,
):
    """
    Rerank retrieved chunks according to their
    relevance to the question.
    """

    if not chunks:
        return []

    pairs = [(question, chunk.text) for chunk, distance in chunks]

    scores = reranker.predict(pairs)

    reranked = []

    for (chunk, distance), score in zip(chunks, scores):
        reranked.append(
            {
                "chunk": chunk,
                "distance": distance,
                "score": float(score),
            }
        )

    # Higher cross-encoder score = more relevant
    reranked.sort(key=lambda item: item["score"], reverse=True)

    return reranked[:top_k]
