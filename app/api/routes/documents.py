from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.services.ingestion_service import ingest_document
from app.services.pdf_service import save_pdf


router = APIRouter()


@router.post("/upload")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):

    # -------------------------
    # 1. Validate file
    # -------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed.",
        )

    if not file.filename:
        raise HTTPException(
            status_code=400,
            detail="Filename is required.",
        )

    # -------------------------
    # 2. Save PDF
    # -------------------------

    file_path = await save_pdf(
        file=file,
        filename=file.filename,
    )

    # -------------------------
    # 3. Extract + chunk +
    #    embed + store
    # -------------------------

    try:
        document = ingest_document(
            db=db,
            file_path=file_path,
            filename=file.filename,
        )

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Failed to process the document.",
        )

    # -------------------------
    # 4. Return response
    # -------------------------

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "file_path": document.file_path,
        "message": "Document uploaded and processed successfully.",
    }