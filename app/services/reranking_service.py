"""Cross-encoder reranking service used to rank retrieved document chunks."""

from fastembed.rerank.cross_encoder import TextCrossEncoder


MODEL_NAME = "Xenova/ms-marco-MiniLM-L-6-v2"


class RerankingService:
    """Rerank retrieved chunks using a lightweight cross-encoder."""

    def __init__(self):
        """Load the cross-encoder model once for reuse."""
        self.encoder = TextCrossEncoder(
            model_name=MODEL_NAME
        )

    def rerank(
        self,
        query: str,
        results: list[dict],
        top_k: int,
    ) -> list[dict]:
        """Rerank retrieved chunks against the user's query.

        Args:
            query: User's natural-language question.
            results: Vector-search results containing chunks and distances.
            top_k: Number of highest-ranked results to return.

        Returns:
            Reranked results containing the original chunk,
            vector distance, and cross-encoder score.
        """
        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not results:
            return []

        if top_k <= 0:
            return []

        documents = [
            result["chunk"].text
            for result in results
        ]

        scores = list(
            self.encoder.rerank(
                query,
                documents,
            )
        )

        reranked_results = []

        for result, score in zip(results, scores):
            reranked_results.append(
                {
                    "chunk": result["chunk"],
                    "vector_distance": result["distance"],
                    "rerank_score": float(score),
                }
            )

        reranked_results.sort(
            key=lambda result: result["rerank_score"],
            reverse=True,
        )

        return reranked_results[:top_k]


reranker_service = RerankingService()


if __name__ == "__main__":
    service = RerankingService()

    query = "Who is maintaining Qdrant?"

    documents = [
        "This is built to be faster and lighter than other libraries.",
        "fastembed is supported by and maintained by Qdrant.",
    ]

    scores = list(
        service.encoder.rerank(
            query,
            documents,
        )
    )

    print("Scores:", scores)