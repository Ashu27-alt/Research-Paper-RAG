"""Orchestration for retrieval, reranking, context construction, and answering."""

from sqlalchemy.orm import Session

from app.services.retrieval_service import search_chunks
from app.services.llm_service import generate_answer
from app.services.reranking_service import reranker_service
from app.config import settings

def answer_question(
    db: Session,
    question: str,
    top_k: int = settings.reranking_top_k,
    max_distance: float =settings.max_distance,
    document_id=None,
):
    """Answer a question using the most relevant indexed document chunks.

    Args:
        db: Active SQLAlchemy session used for vector retrieval.
        question: Natural-language question to answer.
        top_k: Number of reranked chunks passed to the language model.
        max_distance: Maximum vector distance allowed during candidate retrieval.
        document_id: Optional document UUID that narrows the search scope.

    Returns:
        A dictionary containing an ``answer`` and citation-ready ``sources``.
    """
    # -------------------------
    # 1. Retrieve candidates
    # -------------------------

    retrieved = search_chunks(
        db=db,
        query=question,
        top_k=20,
        max_distance=max_distance,
        document_id=document_id,
    )

    # -------------------------
    # 2. Rerank candidates
    # -------------------------

    results = reranker_service.rerank(
        query=question,
        results=retrieved,
        top_k=top_k,
    )

    # -------------------------
    # 3. No relevant context
    # -------------------------

    if not results:
        return {
            "answer": (
                "I could not find relevant information " "in the provided documents."
            ),
            "sources": [],
        }

    # -------------------------
    # 4. Build context
    # -------------------------

    context_parts = []

    for index, result in enumerate(results, start=1):

        chunk = result["chunk"]

        context_parts.append(
            f"""
                [SOURCE {index}]
                Document: {chunk.document.filename}
                Page: {chunk.page_number}
                Chunk ID: {chunk.id}
                {chunk.text}
            """
        )

    context = "\n".join(context_parts)

    # -------------------------
    # 5. Generate answer
    # -------------------------

    answer = generate_answer(
        question=question,
        context=context,
    )

    # -------------------------
    # 6. Build sources
    # -------------------------

    sources = []

    for index, result in enumerate(results, start=1):

        chunk = result["chunk"]

        score = result["rerank_score"]
        distance = result["vector_distance"]

        sources.append(
            {
                "source": f"SOURCE {index}",
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename,
                "chunk_id": chunk.id,
                "page_number": chunk.page_number,
                "distance": float(distance),
                "reranker_score": float(score),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }
