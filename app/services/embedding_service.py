from sentence_transformers import SentenceTransformer


MODEL_NAME = "all-MiniLM-L6-v2"

model = SentenceTransformer(MODEL_NAME)


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding for a single text.
    """

    embedding = model.encode(text)

    return embedding.tolist()


def generate_embeddings(
    texts: list[str]
) -> list[list[float]]:
    """
    Generate embeddings for multiple texts.
    """

    embeddings = model.encode(texts)

    return embeddings.tolist()