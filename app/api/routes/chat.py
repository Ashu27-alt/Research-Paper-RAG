from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.rag_service import answer_question


router = APIRouter()


@router.get("/ask")
def ask_question( question: str, top_k: int = 5, max_distance: float = 0.8, document_id: str | None = None, db: Session = Depends(get_db) ):

    result = answer_question(
        db=db,
        question=question,
        top_k=top_k,
        max_distance=max_distance,
        document_id=document_id
    )

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"]
    }