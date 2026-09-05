from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import (
    save_pdf,
    extract_text
)

router = APIRouter()

@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    # 1. Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # 2. Save PDF
    file_path = await save_pdf(
        file,
        file.filename
    )

	# 3. Extract text
    pages = extract_text(file_path)

    return {
        "filename": file.filename,
        "file_path": file_path,
        "pages": len(pages),
        "content": pages
    }