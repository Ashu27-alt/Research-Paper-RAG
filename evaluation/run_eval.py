import json
from pathlib import Path

from app.db.database import SessionLocal
from app.services.retrieval_service import search_chunks
from app.services.reranking_service import reranker_service

from evaluation.metrics import (
    recall_at_k,
    precision_at_k,
    reciprocal_rank,
)

DATASET_PATH = Path("evaluation/datasets/retrieval_test.json")

CANDIDATE_DEPTHS = [10, 20, 26]
RERANK_TOP_K = 5


def load_dataset():
    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def evaluate():
    dataset = load_dataset()
    db = SessionLocal()

    summary = {
        depth: {
            "recall": [],
            "precision": [],
            "mrr": [],
        }
        for depth in CANDIDATE_DEPTHS
    }

    try:
        for item in dataset:

            question = item["question"]
            document_id = item["document_id"]
            relevant_chunk_ids = set(
                item["relevant_chunk_ids"]
            )

            print()
            print("=" * 100)
            print(f"QUESTION: {question}")
            print("=" * 100)
            print(
                f"Relevant chunks: "
                f"{sorted(relevant_chunk_ids)}"
            )

            for candidate_depth in CANDIDATE_DEPTHS:

                # ==================================================
                # 1. VECTOR RETRIEVAL
                # ==================================================

                retrieved = search_chunks(
                    db=db,
                    query=question,
                    top_k=candidate_depth,
                    max_distance=1.0,
                    document_id=document_id,
                )

                vector_chunk_ids = [
                    chunk.id
                    for chunk, distance in retrieved
                ]

                vector_recall = recall_at_k(
                    vector_chunk_ids,
                    relevant_chunk_ids,
                    candidate_depth,
                )

                # ==================================================
                # 2. RERANKING
                # ==================================================

                reranked = reranker_service.rerank(
                    query=question,
                    results=retrieved,
                    top_k=RERANK_TOP_K,
                )

                reranked_chunk_ids = [
                    result["chunk"].id
                    for result in reranked
                ]

                rerank_recall = recall_at_k(
                    reranked_chunk_ids,
                    relevant_chunk_ids,
                    RERANK_TOP_K,
                )

                rerank_precision = precision_at_k(
                    reranked_chunk_ids,
                    relevant_chunk_ids,
                    RERANK_TOP_K,
                )

                rerank_mrr = reciprocal_rank(
                    reranked_chunk_ids,
                    relevant_chunk_ids,
                )

                # ==================================================
                # 3. STORE METRICS
                # ==================================================

                summary[candidate_depth]["recall"].append(
                    rerank_recall
                )

                summary[candidate_depth]["precision"].append(
                    rerank_precision
                )

                summary[candidate_depth]["mrr"].append(
                    rerank_mrr
                )

                # ==================================================
                # 4. PRINT RESULTS
                # ==================================================

                print()
                print(
                    f"--- Candidate Depth: "
                    f"{candidate_depth} ---"
                )

                print(
                    f"Vector chunks: "
                    f"{vector_chunk_ids}"
                )

                print(
                    f"Vector Recall@{candidate_depth}: "
                    f"{vector_recall:.2f}"
                )

                print(
                    f"Reranked Top-{RERANK_TOP_K}: "
                    f"{reranked_chunk_ids}"
                )

                print(
                    f"Rerank Recall@5: "
                    f"{rerank_recall:.2f}"
                )

                print(
                    f"Rerank Precision@5: "
                    f"{rerank_precision:.2f}"
                )

                print(
                    f"Rerank MRR: "
                    f"{rerank_mrr:.2f}"
                )

                # ==================================================
                # 5. RELEVANT CHUNK POSITIONS
                # ==================================================

                print()
                print("Relevant chunk positions:")

                for chunk_id in sorted(
                    relevant_chunk_ids
                ):

                    if chunk_id in vector_chunk_ids:

                        vector_rank = (
                            vector_chunk_ids.index(
                                chunk_id
                            ) + 1
                        )

                        print(
                            f"  Chunk {chunk_id}: "
                            f"vector rank {vector_rank}",
                            end=""
                        )

                        if chunk_id in reranked_chunk_ids:

                            rerank_rank = (
                                reranked_chunk_ids.index(
                                    chunk_id
                                ) + 1
                            )

                            print(
                                f", reranker rank "
                                f"{rerank_rank}"
                            )

                        else:

                            print(
                                ", not in reranked Top-5"
                            )

                    else:

                        print(
                            f"  Chunk {chunk_id}: "
                            f"not retrieved"
                        )

                # ==================================================
                # 6. RERANKER FAILURE DIAGNOSTICS
                # ==================================================

                if rerank_recall < 1.0:

                    print()
                    print("=" * 100)
                    print("!!! RERANKER FAILURE !!!")
                    print("=" * 100)

                    print(
                        f"Question: {question}"
                    )

                    print(
                        f"Candidate depth: "
                        f"{candidate_depth}"
                    )

                    print(
                        f"Relevant chunks: "
                        f"{sorted(relevant_chunk_ids)}"
                    )

                    print()

                    # ----------------------------------------------
                    # Full relevant chunks
                    # ----------------------------------------------

                    print(
                        "FULL RELEVANT CHUNKS:"
                    )

                    for chunk_id in sorted(
                        relevant_chunk_ids
                    ):

                        chunk = next(
                            (
                                c
                                for c, _ in retrieved
                                if c.id == chunk_id
                            ),
                            None,
                        )

                        if chunk:

                            print()
                            print(
                                "-" * 80
                            )

                            print(
                                f"CHUNK {chunk.id}"
                            )

                            print(
                                f"PAGE: "
                                f"{chunk.page_number}"
                            )

                            print(
                                "-" * 80
                            )

                            print(
                                chunk.text
                            )

                        else:

                            print()
                            print(
                                f"Chunk {chunk_id} "
                                f"was not retrieved "
                                f"at candidate depth "
                                f"{candidate_depth}."
                            )

                    # ----------------------------------------------
                    # Reranker Top-5
                    # ----------------------------------------------

                    print()
                    print(
                        "RERANKER TOP-5:"
                    )

                    for rank, result in enumerate(
                        reranked,
                        start=1,
                    ):

                        chunk = result["chunk"]

                        marker = (
                            "✓ RELEVANT"
                            if chunk.id
                            in relevant_chunk_ids
                            else "✗ NOT RELEVANT"
                        )

                        print()

                        print(
                            f"{rank}. "
                            f"Chunk {chunk.id} "
                            f"| score="
                            f"{result['rerank_score']:.4f} "
                            f"| {marker}"
                        )

                        print(
                            f"   Page: "
                            f"{chunk.page_number}"
                        )

                        print(
                            f"   Text: "
                            f"{chunk.text[:500]}..."
                        )

        # ==========================================================
        # FINAL SUMMARY
        # ==========================================================

        print()
        print()
        print("=" * 100)
        print("FINAL SUMMARY")
        print("=" * 100)

        for candidate_depth in CANDIDATE_DEPTHS:

            recall_values = (
                summary[candidate_depth]["recall"]
            )

            precision_values = (
                summary[candidate_depth]["precision"]
            )

            mrr_values = (
                summary[candidate_depth]["mrr"]
            )

            avg_recall = (
                sum(recall_values)
                / len(recall_values)
            )

            avg_precision = (
                sum(precision_values)
                / len(precision_values)
            )

            avg_mrr = (
                sum(mrr_values)
                / len(mrr_values)
            )

            print()
            print(
                f"Vector Top-{candidate_depth} "
                f"→ Reranker Top-5"
            )

            print(
                f"Recall@5:    "
                f"{avg_recall:.3f}"
            )

            print(
                f"Precision@5: "
                f"{avg_precision:.3f}"
            )

            print(
                f"MRR:         "
                f"{avg_mrr:.3f}"
            )

    finally:
        db.close()


if __name__ == "__main__":
    evaluate()
