from fastapi import APIRouter, UploadFile, File, HTTPException

from app.services.pdf_service import (
    save_pdf,
    extract_text
)

from app.services.chunking_service import (
    chunk_text
)


router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...)):

    # Validate file type
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Save PDF
    file_path = await save_pdf(
        file,
        file.filename
    )

    # Extract text page-by-page
    pages = extract_text(file_path)

    # Create chunks
    all_chunks = []

    for page in pages:

        page_chunks = chunk_text(
            text=page["text"],
            page_number=page["page_number"],
            chunk_size=500,
            overlap=100
        )

        all_chunks.extend(page_chunks)

    return {
        "filename": file.filename,
        "pages": len(pages),
        "chunks": len(all_chunks),
        "content": all_chunks
    }