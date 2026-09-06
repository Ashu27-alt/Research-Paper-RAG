from sentence_transformers import CrossEncoder


MODEL_NAME = "cross-encoder/ms-marco-MiniLM-L-6-v2"


class RerankerService:

    def __init__(self):
        self.model = CrossEncoder(MODEL_NAME)

    def rerank(
        self,
        query: str,
        results: list,
        top_k: int = 5,
    ) -> list:
        """
        Rerank retrieved document chunks using a cross-encoder.

        Args:
            query: User's search query.
            results: Results returned by vector retrieval.
            top_k: Number of final results to return.

        Returns:
            Reranked results with relevance scores.
        """

        if not query or not query.strip():
            raise ValueError("Query cannot be empty")

        if not results:
            return []

        # Create (query, chunk_text) pairs
        pairs = [
            (query, result[0].text)
            for result in results
        ]

        # Calculate cross-encoder relevance scores
        scores = self.model.predict(pairs)

        # Attach scores to results
        reranked_results = []

        for result, score in zip(results, scores):
            chunk, distance = result

            reranked_results.append({
                "chunk": chunk,
                "vector_distance": float(distance),
                "rerank_score": float(score),
            })

        # Highest reranker score = most relevant
        reranked_results.sort(
            key=lambda x: x["rerank_score"],
            reverse=True,
        )

        return reranked_results[:top_k]


reranker_service = RerankerService()