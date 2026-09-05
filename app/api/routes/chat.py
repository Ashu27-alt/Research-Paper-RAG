from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.rag_service import answer_question


router = APIRouter()


@router.get("/ask")
def ask_question(
    question: str,
    top_k: int = 5,
    db: Session = Depends(get_db)
):

    result = answer_question(
        db=db,
        question=question,
        top_k=top_k
    )

    return {
        "question": question,
        "answer": result["answer"],
        "sources": result["sources"]
    }