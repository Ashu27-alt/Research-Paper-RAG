"""Endpoint for direct semantic search over indexed chunks."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.search import SearchRequest, SearchResponse
from app.services.retrieval_service import search_chunks


router = APIRouter()


@router.get(
    "/search",
    response_model=SearchResponse,
)
def search(
    request: Annotated[SearchRequest, Query()],
    db: Session = Depends(get_db),
):
    """Return chunks closest to a query embedding.

    Args:
        request: Validated query parameters defined by ``SearchRequest``.
        db: Request-scoped SQLAlchemy session.

    Returns:
        The query and matching chunks with their distances.
    """

    results = search_chunks(
        db=db,
        query=request.query,
        top_k=request.top_k,
        max_distance=request.max_distance,
        document_id=request.document_id,
    )

    return {
        "query": request.query,
        "results": [
            {
                "chunk_id": chunk.id,
                "page_number": chunk.page_number,
                "text": chunk.text,
                "distance": float(distance)
            }
            for chunk, distance in results
        ]
    }
