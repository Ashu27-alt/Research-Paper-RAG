from sentence_transformers import SentenceTransformer
import numpy as np


model = SentenceTransformer("all-MiniLM-L6-v2")


sentences = [
    "What optimizer was used?",
    "The model was trained using AdamW.",
    "The weather is sunny today."
]


embeddings = model.encode(sentences)


def cosine_similarity(a, b):
    return np.dot(a, b) / (
        np.linalg.norm(a) * np.linalg.norm(b)
    )


similarity_1 = cosine_similarity(
    embeddings[0],
    embeddings[1]
)

similarity_2 = cosine_similarity(
    embeddings[0],
    embeddings[2]
)


print("Question ↔ AdamW:", similarity_1)
print("Question ↔ Weather:", similarity_2)