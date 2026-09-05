from sqlalchemy.orm import Session

from app.db.models import DocumentChunk
from app.services.embedding_service import generate_embedding


def search_chunks(db: Session, query: str, top_k: int = 5):

    query_embedding = generate_embedding(query)

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    results = (
        db.query(DocumentChunk, distance.label("distance"))
        .order_by(distance)
        .limit(top_k)
        .all()
    )

    return results
