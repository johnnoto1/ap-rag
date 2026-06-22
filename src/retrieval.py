"""
retrieval.py — Query the vector store built by ingest.py.

Given a question, embeds it, retrieves the most semantically similar
chunks from ChromaDB, and prints them with their source and page.

Usage:
    uv run python src/retrieval.py "your question here"
    uv run python src/retrieval.py            # uses a default demo query
"""

import sys
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions

CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "ap_cardiovascular"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
TOP_K = 5  # how many chunks to retrieve


def get_collection(collection_name=COLLECTION_NAME):
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    return client.get_collection(
        name=collection_name, embedding_function=embedding_fn
    )


def retrieve(query, top_k=TOP_K, collection_name=COLLECTION_NAME):
    collection = get_collection(collection_name)
    results = collection.query(query_texts=[query], n_results=top_k)
    # ChromaDB returns lists-of-lists (one per query); we sent one query.
    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]
    return list(zip(documents, metadatas, distances))


def main():
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = "Why does the left ventricle have a thicker wall than the right ventricle?"

    print(f"Query: {query}\n")
    print(f"Retrieving top {TOP_K} chunks ...\n")

    hits = retrieve(query)
    for i, (doc, meta, dist) in enumerate(hits, 1):
        print(f"{'=' * 70}")
        print(f"Result {i}  |  page {meta.get('page')}  |  distance {dist:.4f}")
        print(f"{'=' * 70}")
        print(doc.strip()[:600])
        print()


if __name__ == "__main__":
    main()
