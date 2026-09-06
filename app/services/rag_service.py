from sqlalchemy.orm import Session

from app.services.retrieval_service import search_chunks
from app.services.llm_service import generate_answer
from app.services.reranking_service import reranker_service


def answer_question(
    db: Session,
    question: str,
    top_k: int = 5,
    max_distance: float = 1.0,
    document_id=None,
):
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

        sources.append(
            {
                "source": f"SOURCE {index}",
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename,
                "chunk_id": chunk.id,
                "page_number": chunk.page_number,
                "reranker_score": float(score),
            }
        )

    return {
        "answer": answer,
        "sources": sources,
    }
