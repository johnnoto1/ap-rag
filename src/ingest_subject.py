"""ingest_subject.py — build ONE Chroma collection from ONE OpenStax book.

Same pipeline as ingest.py (pypdf page extraction -> SentenceSplitter
500/50 -> all-MiniLM-L6-v2 embeddings -> persistent ChromaDB), but it
targets a single book selected by subject key, so each sibling tutor gets
its own collection instead of everything landing in one.

Usage:
    uv run python src/ingest_subject.py microbiology
    uv run python src/ingest_subject.py psychology
    uv run python src/ingest_subject.py history
    uv run python src/ingest_subject.py economics

This is a ONE-TIME, pre-build step per book. It may run several minutes on
an M1 (embedding ~2,500+ chunks). It never runs live during the talk.
"""

import sys
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

from subjects import get, PROTECTED

# --- Identical knobs to ingest.py ------------------------------------------
CHROMA_DIR = Path("chroma_db")
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"
CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MIN_PAGE_CHARS = 50
BATCH_SIZE = 256


def load_pages(pdf_path):
    """One Document per page, with 1-based PDF page numbers as metadata.

    NOTE: 'page' is the PDF's physical page index + 1, NOT the printed book
    page. OpenStax WEB PDFs have front matter, so they differ by a fixed
    offset per book (see docs/tier2.md for how to find it).
    """
    if not pdf_path.exists():
        raise SystemExit(
            f"PDF not found: {pdf_path}\n"
            f"Put the book in data/corpus/ with exactly that filename."
        )

    print(f"Reading {pdf_path.name} ...")
    reader = PdfReader(str(pdf_path))
    documents = []
    kept, skipped = 0, 0
    for page_num, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        if len(text.strip()) < MIN_PAGE_CHARS:
            skipped += 1
            continue
        documents.append(
            Document(
                text=text,
                metadata={"source": pdf_path.name, "page": page_num + 1},
            )
        )
        kept += 1
    print(f"  Kept {kept} pages, skipped {skipped} near-empty pages.")
    print(f"  PDF has {len(reader.pages)} physical pages total.")
    return documents


def chunk_documents(documents):
    print(f"Chunking into ~{CHUNK_SIZE}-token pieces "
          f"with {CHUNK_OVERLAP}-token overlap ...")
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"  Produced {len(nodes)} chunks.")
    return nodes


def build_collection(nodes, collection_name):
    print(f"Setting up ChromaDB at {CHROMA_DIR} ...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        client.delete_collection(collection_name)
        print(f"  Removed existing collection '{collection_name}'.")
    except Exception:
        pass

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    collection = client.create_collection(
        name=collection_name, embedding_function=embedding_fn
    )

    print(f"Embedding and storing {len(nodes)} chunks "
          f"(model: {EMBED_MODEL_NAME}) ...")
    for start in range(0, len(nodes), BATCH_SIZE):
        batch = nodes[start:start + BATCH_SIZE]
        collection.add(
            ids=[node.node_id for node in batch],
            documents=[node.get_content() for node in batch],
            metadatas=[
                {
                    "source": node.metadata.get("source", "unknown"),
                    "page": node.metadata.get("page", "unknown"),
                }
                for node in batch
            ],
        )
        done = min(start + BATCH_SIZE, len(nodes))
        print(f"  Stored {done}/{len(nodes)} chunks.")

    print(f"Done. Collection '{collection_name}' now has "
          f"{collection.count()} chunks.")
    return collection


def main():
    if len(sys.argv) < 2:
        raise SystemExit(
            "Usage: uv run python src/ingest_subject.py <subject>\n"
            "  e.g. uv run python src/ingest_subject.py microbiology"
        )

    cfg = get(sys.argv[1])

    if cfg["key"] in PROTECTED:
        raise SystemExit(
            f"'{cfg['key']}' ({cfg['label']}) is already ingested as "
            f"collection '{cfg['collection']}'. Refusing to overwrite it.\n"
            f"This script is for the sibling tutors only."
        )

    print(f"=== Ingesting {cfg['label']} -> collection '{cfg['collection']}' ===\n")
    documents = load_pages(cfg["pdf_path"])
    nodes = chunk_documents(documents)
    build_collection(nodes, cfg["collection"])
    print(f"\nIngestion complete for {cfg['label']}.")
    print(f"Query it with: uv run python src/query.py --subject "
          f"{cfg['key']} \"your question\"")


if __name__ == "__main__":
    main()
