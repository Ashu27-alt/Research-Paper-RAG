from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.services.embedding_service import generate_embedding


def search_chunks(db: Session, query: str, top_k: int = 5):

    # Convert question into vector
    query_embedding = generate_embedding(query)

    # Search database
    results = (
        db.query(DocumentChunk)
        .order_by(DocumentChunk.embedding.cosine_distance(query_embedding))
        .limit(top_k)
        .all()
    )

    return results
