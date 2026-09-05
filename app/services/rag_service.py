from sqlalchemy.orm import Session

from app.services.retrieval_service import search_chunks
from app.services.llm_service import generate_answer


def answer_question(db: Session, question: str, top_k: int = 5, max_distance: float = 0.30, document_id=None):
    # -------------------------
    # 1. Retrieve relevant chunks
    # -------------------------

    results = search_chunks(
        db=db,
        query=question,
        top_k=top_k,
        max_distance=max_distance,
        document_id=document_id,
    )

    # -------------------------
    # 2. No relevant context
    # -------------------------

    if not results:

        return {
            "answer": (
                "I could not find relevant information " "in the provided documents."
            ),
            "sources": [],
        }

    # -------------------------
    # 3. Build context
    # -------------------------

    context_parts = []

    for index, (chunk, distance) in enumerate(results, start=1):

        context_parts.append(
            f"""
                [SOURCE {index} | {chunk.document.filename} | Page {chunk.page_number}]
                {chunk.text}
            """
        )

    context = "\n".join(context_parts)

    # -------------------------
    # 4. Generate answer
    # -------------------------

    answer = generate_answer(question=question, context=context)

    # -------------------------
    # 5. Build sources
    # -------------------------

    sources = []

    for index, (chunk, distance) in enumerate(results, start=1):

        sources.append(
            {
                "source": f"SOURCE {index}",
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename,
                "chunk_id": chunk.id,
                "page_number": chunk.page_number,
                "distance": float(distance),
            }
        )

    return {"answer": answer, "sources": sources}
