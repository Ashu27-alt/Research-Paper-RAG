from fastapi import FastAPI

from app.api.routes.documents import router as documents_router

from app.api.routes.search import router as search_router


app = FastAPI(
    title="AI Document Intelligence API",
    description="RAG-based document question answering system",
    version="1.0.0",
)

app.include_router(documents_router, prefix="/documents", tags=["Documents"])

app.include_router(search_router, prefix="/documents", tags=["Search"])


@app.get("/")
def root():
    return {"message": "RAG API is running"}
