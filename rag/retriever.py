import os
import json
import faiss

from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INDEX_FILE = os.path.join(
    BASE_DIR,
    "vector_db",
    "schemes.index"
)

CHUNKS_FILE = os.path.join(
    BASE_DIR,
    "vector_db",
    "chunks.json"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def load_database():

    print("\n[1] Loading FAISS database...")

    if not os.path.exists(INDEX_FILE):
        raise FileNotFoundError(
            "FAISS index not found. Run embeddings.py first."
        )

    if not os.path.exists(CHUNKS_FILE):
        raise FileNotFoundError(
            "chunks.json not found. Run embeddings.py first."
        )

    index = faiss.read_index(INDEX_FILE)

    with open(
        CHUNKS_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        chunks = json.load(file)

    print("Vectors:", index.ntotal)
    print("Chunks :", len(chunks))

    return index, chunks


def load_model():

    print("\n[2] Loading embedding model...")

    model = SentenceTransformer(MODEL_NAME)

    return model


def search(query, index, chunks, model, top_k=5):

    if not query.strip():
        return []

    print("\n[3] Searching...")
    print("Query:", query)

    query_embedding = model.encode(
        [query],
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    scores, indices = index.search(
        query_embedding,
        top_k
    )

    results = []

    for score, index_number in zip(
        scores[0],
        indices[0]
    ):

        if index_number == -1:
            continue

        result = {
            "score": float(score),
            "text": chunks[index_number]["text"],
            "metadata": chunks[index_number]["metadata"]
        }

        results.append(result)

    return results


def main():

    print("\n")
    print("=" * 60)
    print("             GOVERNMENT SCHEME RETRIEVER")
    print("=" * 60)

    index, chunks = load_database()

    model = load_model()

    print("\nReady for queries.")

    while True:

        query = input("\nAsk about a government scheme: ")

        if query.lower() in ["exit", "quit"]:
            break

        results = search(
            query,
            index,
            chunks,
            model,
            top_k=5
        )

        print("\n" + "=" * 60)
        print("                  RESULTS")
        print("=" * 60)

        if not results:
            print("\nNo results found.")
            continue

        for i, result in enumerate(results, start=1):

            metadata = result["metadata"]

            print(f"\n--- RESULT {i} ---")

            print(
                f"Similarity : {result['score']:.4f}"
            )

            print(
                f"Sector     : {metadata['sector']}"
            )

            print(
                f"Category   : {metadata['category']}"
            )

            print(
                f"Source     : {metadata['filename']}"
            )

            print(
                f"Page       : {metadata['page']}"
            )

            print("\nText:")
            print(result["text"])

    print("\nRetriever stopped.")


if __name__ == "__main__":
    main()