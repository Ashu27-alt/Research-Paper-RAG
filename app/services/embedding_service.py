from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIMENSION = 384


class EmbeddingService:
    def __init__(self):
        self.model = SentenceTransformer(MODEL_NAME)

    def embed_text(self, text: str) -> list[float]:
        """
        Generate an embedding for a single piece of text.
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        embedding = self.model.encode(
            text,
            normalize_embeddings=True
        )

        return embedding.tolist()

    def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        """
        if not texts:
            return []

        if any(not text or not text.strip() for text in texts):
            raise ValueError("Texts cannot contain empty strings")

        embeddings = self.model.encode(
            texts,
            normalize_embeddings=True,
            show_progress_bar=True
        )

        return embeddings.tolist()


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