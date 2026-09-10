"""Embedding model wrapper used by ingestion and vector retrieval."""

from fastembed import TextEmbedding


MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


class EmbeddingService:
    """Load the FastEmbed model and create normalized vectors."""

    def __init__(self):
        """Load the embedding model once for reuse by the application."""
        self.model = TextEmbedding(
            model_name=MODEL_NAME,
            batch_size=8,
        )

    def embed_text(self, text: str) -> list[float]:
        """Generate an embedding for one non-empty string.

        Args:
            text: Text to convert into a vector.

        Returns:
            A 384-dimensional embedding as a list of floats.

        Raises:
            ValueError: If ``text`` is empty or only whitespace.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        embedding = list(
            self.model.embed([text])
        )[0]

        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """Generate embeddings for multiple non-empty strings.

        Args:
            texts: Text strings to embed.

        Returns:
            One 384-dimensional embedding per input text, or an empty list.

        Raises:
            ValueError: If any supplied text is empty or only whitespace.
        """
        if not texts:
            return []

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty strings")

        embeddings = self.model.embed(
            texts,
            batch_size=8,
        )

        return [
            embedding.tolist()
            for embedding in embeddings
        ]


embedding_service = EmbeddingService()


if __name__ == "__main__":
    service = EmbeddingService()

    text = """
    Autoencoders are neural networks that learn to reconstruct
    their input data through a lower-dimensional representation.
    """

    embedding = service.embed_text(text)

    print("Embedding dimension:", len(embedding))
    print("First 10 values:", embedding[:10])