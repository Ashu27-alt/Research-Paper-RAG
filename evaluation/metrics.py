"""Ranking metrics used by the retrieval evaluation script."""

def recall_at_k(
    retrieved_chunk_ids: list[int],
    relevant_chunk_ids: list[int],
    k: int
) -> float:
    """Calculate the fraction of relevant chunks found in the first ``k`` results.

    Args:
        retrieved_chunk_ids: Chunk IDs ordered by retrieval rank.
        relevant_chunk_ids: Ground-truth chunk IDs for the query.
        k: Number of leading retrieved results to inspect.

    Returns:
        Recall in the inclusive range from 0.0 to 1.0.
    """

    retrieved = set(retrieved_chunk_ids[:k])
    relevant = set(relevant_chunk_ids)

    if not relevant:
        return 0.0

    return len(
        retrieved.intersection(relevant)
    ) / len(relevant)


def precision_at_k(
    retrieved_chunk_ids: list[int],
    relevant_chunk_ids: list[int],
    k: int
) -> float:
    """Calculate the fraction of the first ``k`` results that are relevant.

    Args:
        retrieved_chunk_ids: Chunk IDs ordered by retrieval rank.
        relevant_chunk_ids: Ground-truth chunk IDs for the query.
        k: Number of leading retrieved results to inspect.

    Returns:
        Precision in the inclusive range from 0.0 to 1.0.
    """

    retrieved = retrieved_chunk_ids[:k]
    relevant = set(relevant_chunk_ids)

    if not retrieved:
        return 0.0

    relevant_retrieved = sum(
        chunk_id in relevant
        for chunk_id in retrieved
    )

    return relevant_retrieved / len(retrieved)


def reciprocal_rank(
    retrieved_chunk_ids: list[int],
    relevant_chunk_ids: list[int]
) -> float:
    """Calculate reciprocal rank of the first relevant retrieved chunk.

    Args:
        retrieved_chunk_ids: Chunk IDs ordered by retrieval rank.
        relevant_chunk_ids: Ground-truth chunk IDs for the query.

    Returns:
        ``1 / rank`` for the first relevant result, or 0.0 if none is found.
    """

    relevant = set(relevant_chunk_ids)

    for rank, chunk_id in enumerate(
        retrieved_chunk_ids,
        start=1
    ):

        if chunk_id in relevant:
            return 1 / rank

    return 0.0
