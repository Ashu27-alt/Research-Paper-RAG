from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.rag_service import answer_question


router = APIRouter()




@router.post("/chat")
def chat(
    question: str,
    document_id: UUID | None = None,
    top_k: int = 5,
    max_distance: float = 1.0,
    db: Session = Depends(get_db),
):
    return answer_question(
        db=db,
        question=question,
        top_k=top_k,
        max_distance=max_distance,
        document_id=document_id,
    )