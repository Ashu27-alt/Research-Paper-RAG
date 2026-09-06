from app.services.chunking_service import chunk_pages


text = """
Artificial intelligence has become increasingly important
in modern software systems. Retrieval augmented generation
allows language models to use external knowledge. This can
reduce hallucinations and improve factual accuracy.

A RAG system usually contains several components.
Documents are first processed and divided into chunks.
The chunks are then converted into vector embeddings.
These embeddings are stored in a vector database.

When a user asks a question, the question is embedded.
The system retrieves the most relevant chunks.
Those chunks are then provided to a language model.
"""


chunks = chunk_pages(
    pages=[
        {
            "page_number": 1,
            "blocks": [{"text": text, "type": "text"}],
        }
    ],
    chunk_size=30,
    overlap=10,
)


for chunk in chunks:

    print(
        f"\nChunk {chunk['chunk_index']}"
    )

    print(
        chunk["text"]
    )
