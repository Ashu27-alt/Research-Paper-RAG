from fastapi import APIRouter, UploadFile, File, HTTPException, Depends

from sqlalchemy.orm import Session

from app.services.pdf_service import save_pdf, extract_text

from app.services.chunking_service import chunk_text

from app.services.embedding_service import generate_embeddings

from app.db.dependencies import get_db

from app.db.models import Document, DocumentChunk


router = APIRouter()


@router.post("/upload")
async def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):

    # -------------------------
    # 1. Validate PDF
    # -------------------------

    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed.")

    # -------------------------
    # 2. Save PDF
    # -------------------------

    file_path = await save_pdf(file, file.filename)

    # -------------------------
    # 3. Extract text
    # -------------------------

    pages = extract_text(file_path)

    # -------------------------
    # 4. Create chunks
    # -------------------------

    all_chunks = []

    for page in pages:

        page_chunks = chunk_text(
            text=page["text"],
            page_number=page["page_number"],
            chunk_size=500,
            overlap=100,
        )

        all_chunks.extend(page_chunks)

    if not all_chunks:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF.")

    # -------------------------
    # 5. Generate embeddings
    # -------------------------

    texts = [chunk["text"] for chunk in all_chunks]

    embeddings = generate_embeddings(texts)

    # -------------------------
    # 6. Create document
    # -------------------------

    document = Document(filename=file.filename, file_path=file_path)

    db.add(document)

    # -------------------------
    # 7. Create chunks
    # -------------------------

    for chunk, embedding in zip(all_chunks, embeddings):
        document_chunk = DocumentChunk(
            document=document,
            page_number=chunk["page_number"],
            chunk_index=chunk["chunk_index"],
            text=chunk["text"],
            embedding=embedding,
        )

        db.add(document_chunk)

    # -------------------------
    # 8. Save everything
    # -------------------------

    db.commit()

    # -------------------------
    # 9. Return response
    # -------------------------

    return {
        "document_id": str(document.id),
        "filename": document.filename,
        "pages": len(pages),
        "chunks": len(all_chunks),
    }
