from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.retrieval_service import search_chunks


router = APIRouter()


@router.get("/search")
def search(
    query: str,
    top_k: int = 5,
    max_distance: float = 1.0,
    db: Session = Depends(get_db)
):

    results = search_chunks(
        db=db,
        query=query,
        top_k=top_k,
        max_distance=max_distance
    )

    return {
        "query": query,
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