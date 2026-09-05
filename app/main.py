from fastapi import FastAPI
from app.api.routes.documents import router as documents_router

app = FastAPI(
    title="AI Document Intelligence API",
    description="RAG-based document question answering system",
    version="1.0.0"
)

app.include_router(
    documents_router,
    prefix="/documents",
    tags=["Documents"]
)


@app.get("/")
def root():
    return {
        "message": "RAG API is running"
    }