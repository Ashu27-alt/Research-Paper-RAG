def recall_at_k(
    retrieved_chunk_ids: list[int],
    relevant_chunk_ids: list[int],
    k: int
) -> float:

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

    relevant = set(relevant_chunk_ids)

    for rank, chunk_id in enumerate(
        retrieved_chunk_ids,
        start=1
    ):

        if chunk_id in relevant:
            return 1 / rank

    return 0.0