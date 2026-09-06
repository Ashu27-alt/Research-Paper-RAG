from sqlalchemy.orm import Session, joinedload

from app.db.models import DocumentChunk
from app.services.embedding_service import generate_embedding


def search_chunks(
    db: Session,
    query: str,
    top_k: int = 5,
    max_distance: float = 0.4,
    document_id=None,
):

    # -------------------------
    # 1. Generate query embedding
    # -------------------------

    query_embedding = generate_embedding(query)

    # -------------------------
    # 2. Calculate distance
    # -------------------------

    distance = DocumentChunk.embedding.cosine_distance(query_embedding)

    # -------------------------
    # 3. Build query
    # -------------------------

    query_builder = (
        db.query(DocumentChunk, distance.label("distance"))
        .options(joinedload(DocumentChunk.document))
        .filter(distance <= max_distance)
    )

    # -------------------------
    # 4. Optional document filter
    # -------------------------

    if document_id is not None:

        query_builder = query_builder.filter(DocumentChunk.document_id == document_id)

    # -------------------------
    # 5. Sort + limit
    # -------------------------

    results = query_builder.order_by(distance).limit(top_k).all()

    return results
