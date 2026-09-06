from sqlalchemy.orm import Session

from app.services.retrieval_service import search_chunks
from app.services.reranking_service import reranker_service


def search(
    db: Session,
    query: str,
    candidate_k: int = 20,
    top_k: int = 5,
    document_id=None,
):
    """
    Two-stage retrieval:

    1. Vector similarity search
    2. Cross-encoder reranking
    """

    # Stage 1: retrieve candidates using pgvector
    candidates = search_chunks(
        db=db,
        query=query,
        top_k=candidate_k,
        document_id=document_id,
    )

    # Stage 2: rerank candidates
    results = reranker_service.rerank(
        query=query,
        results=candidates,
        top_k=top_k,
    )

    return results

if __name__ == "__main__":
    from app.db.database import SessionLocal

    db = SessionLocal()

    try:
        results = search(
            db=db,
            query="What is the main objective of the model?",
            candidate_k=20,
            top_k=5,
        )

        for i, result in enumerate(results, start=1):
            chunk = result["chunk"]

            print("\n" + "=" * 80)
            print(f"RANK: {i}")
            print(f"PAGE: {chunk.page_number}")
            print(f"CHUNK: {chunk.chunk_index}")
            print(f"VECTOR DISTANCE: {result['vector_distance']:.4f}")
            print(f"RERANK SCORE: {result['rerank_score']:.4f}")
            print("-" * 80)
            print(chunk.text[:1000])

    finally:
        db.close()