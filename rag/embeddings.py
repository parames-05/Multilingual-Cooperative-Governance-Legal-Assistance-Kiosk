import os
import json
import faiss

from sentence_transformers import SentenceTransformer


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

INPUT_FILE = os.path.join(
    BASE_DIR,
    "rag",
    "processed_chunks.json"
)

VECTOR_DB_DIR = os.path.join(
    BASE_DIR,
    "vector_db"
)

INDEX_FILE = os.path.join(
    VECTOR_DB_DIR,
    "schemes.index"
)

CHUNKS_FILE = os.path.join(
    VECTOR_DB_DIR,
    "chunks.json"
)

MODEL_NAME = "all-MiniLM-L6-v2"


def load_chunks():

    print("\n[1] Loading processed chunks...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        chunks = json.load(file)

    print("Chunks loaded:", len(chunks))

    return chunks


def create_embeddings(chunks):

    print("\n[2] Loading embedding model...")
    print("Model:", MODEL_NAME)

    model = SentenceTransformer(MODEL_NAME)

    texts = [
        chunk["text"]
        for chunk in chunks
    ]

    print("\n[3] Creating embeddings...")
    print("Texts:", len(texts))

    embeddings = model.encode(
        texts,
        show_progress_bar=True,
        convert_to_numpy=True,
        normalize_embeddings=True
    )

    print("\nEmbedding shape:", embeddings.shape)

    return embeddings


def create_faiss_index(embeddings):

    print("\n[4] Creating FAISS index...")

    dimension = embeddings.shape[1]

    index = faiss.IndexFlatIP(dimension)

    index.add(embeddings)

    print("Vector dimension:", dimension)
    print("Vectors stored:", index.ntotal)

    return index


def save_database(index, chunks):

    print("\n[5] Saving vector database...")

    os.makedirs(VECTOR_DB_DIR, exist_ok=True)

    faiss.write_index(
        index,
        INDEX_FILE
    )

    with open(
        CHUNKS_FILE,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            chunks,
            file,
            ensure_ascii=False,
            indent=2
        )

    print("\nFAISS index:")
    print(INDEX_FILE)

    print("\nChunk metadata:")
    print(CHUNKS_FILE)


def main():

    print("\n")
    print("=" * 60)
    print("             SCHEME EMBEDDING")
    print("=" * 60)

    chunks = load_chunks()

    if not chunks:
        print("\n[ERROR] No chunks found.")
        return

    embeddings = create_embeddings(chunks)

    index = create_faiss_index(
        embeddings
    )

    save_database(
        index,
        chunks
    )

    print("\n")
    print("=" * 60)
    print("          EMBEDDING COMPLETE")
    print("=" * 60)

    print("\nTotal vectors:", index.ntotal)
    print("Vector dimension:", embeddings.shape[1])

    print("\nNext step:")
    print("Create retriever.py → semantic scheme search")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()