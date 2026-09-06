import json
from pathlib import Path

from app.db.database import SessionLocal
from app.services.retrieval_service import search_chunks
from app.services.reranking_service import rerank_chunks

from evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    reciprocal_rank,
)


DATASET_PATH = Path("evaluation/datasets/retrieval_test.json")


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate():
    dataset = load_dataset()

    db = SessionLocal()

    try:
        results = []

        for item in dataset:

            question = item["question"]

            document_id = item["document_id"]

            relevant_chunk_ids = set(item["relevant_chunk_ids"])

            # -----------------------------------------
            # STEP 1: Vector retrieval
            # -----------------------------------------

            retrieved = search_chunks(
                db=db,
                query=question,
                top_k=20,
                max_distance=1.0,
                document_id=document_id,
            )

            # -----------------------------------------
            # STEP 2: Reranking
            # -----------------------------------------

            reranked = rerank_chunks(
                question=question,
                chunks=retrieved,
                top_k=5,
            )

            # Extract chunk IDs after reranking
            reranked_chunk_ids = [item["chunk"].id for item in reranked]

            print("\n" + "=" * 70)
            print("QUESTION:")
            print(question)

            print("\nRERANKED CHUNKS:")

            for rank, item in enumerate(reranked, start=1):

                chunk = item["chunk"]

                print(
                    f"\nRank {rank}"
                    f" | Chunk {chunk.id}"
                    f" | Page {chunk.page_number}"
                    f" | Vector distance "
                    f"{float(item['distance']):.4f}"
                    f" | Reranker score "
                    f"{item['score']:.4f}"
                )

                print(chunk.text[:500])

            # -----------------------------------------
            # STEP 3: Calculate metrics
            # -----------------------------------------

            results.append(
                {
                    "question": question,
                    "relevant": list(relevant_chunk_ids),
                    "retrieved": reranked_chunk_ids,
                    "recall@5": recall_at_k(
                        reranked_chunk_ids,
                        relevant_chunk_ids,
                        5,
                    ),
                    "precision@5": precision_at_k(
                        reranked_chunk_ids,
                        relevant_chunk_ids,
                        5,
                    ),
                    "mrr": reciprocal_rank(
                        reranked_chunk_ids,
                        relevant_chunk_ids,
                    ),
                }
            )

        return results

    finally:
        db.close()


if __name__ == "__main__":

    results = evaluate()

    # -----------------------------------------
    # Per-question results
    # -----------------------------------------

    for result in results:

        print("\nQuestion:")
        print(result["question"])

        print("Relevant:", result["relevant"])

        print("Reranked:", result["retrieved"])

        print(f"Recall@5: " f"{result['recall@5']:.2f}")

        print(f"Precision@5: " f"{result['precision@5']:.2f}")

        print(f"MRR: " f"{result['mrr']:.2f}")

    # -----------------------------------------
    # Average metrics
    # -----------------------------------------

    average_recall = sum(result["recall@5"] for result in results) / len(results)

    average_precision = sum(result["precision@5"] for result in results) / len(results)

    average_mrr = sum(result["mrr"] for result in results) / len(results)

    # -----------------------------------------
    # Summary
    # -----------------------------------------

    print("\n" + "=" * 50)
    print("RERANKER EVALUATION SUMMARY")
    print("=" * 50)

    print(f"Average Recall@5: " f"{average_recall:.3f}")

    print(f"Average Precision@5: " f"{average_precision:.3f}")

    print(f"Average MRR: " f"{average_mrr:.3f}")
