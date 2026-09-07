"""Vector similarity retrieval over persisted document chunks."""

from sqlalchemy.orm import Session, joinedload

from app.db.models import DocumentChunk
from app.services.embedding_service import embedding_service


def search_chunks(
    db: Session,
    query: str,
    top_k: int = 20,
    max_distance: float | None = None,
    document_id=None,
):
    """Retrieve the document chunks closest to a query embedding.

    Args:
        db: SQLAlchemy database session.
        query: User's natural-language query.
        top_k: Number of candidates to retrieve.
        max_distance: Optional cosine-distance threshold.
        document_id: Optional document UUID to restrict the search.
    Returns:
        Tuples of ``(DocumentChunk, cosine_distance)``, nearest first.

    Raises:
        ValueError: If ``query`` is empty or only whitespace.
    """

    if not query or not query.strip():
        raise ValueError("Query cannot be empty")

    # 1. Generate embedding for the user's query
    query_embedding = embedding_service.embed_text(query)

    # 2. Calculate cosine distance between query and chunks
    distance = DocumentChunk.embedding.cosine_distance(
        query_embedding
    )

    # 3. Build base query
    query_builder = (
        db.query(
            DocumentChunk,
            distance.label("distance")
        )
        .options(joinedload(DocumentChunk.document))
    )

    # 4. Optional document filtering
    if document_id is not None:
        query_builder = query_builder.filter(
            DocumentChunk.document_id == document_id
        )

    # 5. Optional distance threshold
    if max_distance is not None:
        query_builder = query_builder.filter(
            distance <= max_distance
        )

    # 6. Closest chunks first
    results = (
        query_builder
        .order_by(distance)
        .limit(top_k)
        .all()
    )

    return results
