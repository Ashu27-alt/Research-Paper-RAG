from sqlalchemy.orm import Session

from app.services.retrieval_service import search_chunks
from app.services.llm_service import generate_answer


def answer_question(db: Session, question: str, top_k: int = 5):

    # -------------------------
    # 1. Retrieve chunks
    # -------------------------

    results = search_chunks(db=db, query=question, top_k=top_k)

    # -------------------------
    # 2. Build context
    # -------------------------

    context_parts = []

    for index, (chunk, distance) in enumerate(results, start=1):
        context_parts.append(
            f"""
				[SOURCE {index} | Page {chunk.page_number}]
				{chunk.text}
			""")
        
    context = "\n".join(context_parts)

    # -------------------------
    # 3. Generate answer
    # -------------------------

    answer = generate_answer(question=question, context=context)

    # -------------------------
    # 4. Build source metadata
    # -------------------------

    sources = []

    for index, (chunk, distance) in enumerate(results, start=1):
        sources.append(
            {
                "source": f"SOURCE {index}",
                "chunk_id": chunk.id,
                "document_id": str(chunk.document_id),
                "filename": chunk.document.filename,
                "page_number": chunk.page_number,
                "distance": float(distance),
            }
        )

    return {"answer": answer, "sources": sources}
