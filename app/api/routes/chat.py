"""Endpoints for asking questions about indexed documents."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.rag_service import answer_question


router = APIRouter()


@router.post(
    "/chat",
    response_model=ChatResponse,
)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db),
):
    """Answer a question using retrieved document context.

    Args:
        request: JSON request body validated against ``ChatRequest``.
        db: Request-scoped SQLAlchemy session.

    Returns:
        Generated answer together with supporting source metadata.
    """

    # -------------------------
    # 1. Run RAG pipeline
    # -------------------------

    result = answer_question(
        db=db,
        question=request.question,
        top_k=request.top_k,
        max_distance=request.max_distance,
        document_id=request.document_id,
    )

    # -------------------------
    # 2. Return answer + sources
    # -------------------------

    return result
