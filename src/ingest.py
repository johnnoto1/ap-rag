"""
ingest.py — Build a searchable vector store from the corpus.

Extracts text from PDFs in data/corpus/ using pypdf (one document per
page, with page-number metadata), splits the text into overlapping
chunks, embeds each chunk with a sentence-transformers model, and stores
the result in a persistent ChromaDB collection on disk.
"""

from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from pypdf import PdfReader
from llama_index.core import Document
from llama_index.core.node_parser import SentenceSplitter

CORPUS_DIR = Path("data/corpus")
CHROMA_DIR = Path("chroma_db")
COLLECTION_NAME = "ap_cardiovascular"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50
MIN_PAGE_CHARS = 50


def load_documents(corpus_dir):
    documents = []
    pdf_paths = sorted(corpus_dir.glob("*.pdf"))
    print(f"Found {len(pdf_paths)} PDF(s) in {corpus_dir}.")

    for pdf_path in pdf_paths:
        print(f"Reading {pdf_path.name} ...")
        reader = PdfReader(str(pdf_path))
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

    print(f"Loaded {len(documents)} page-documents total.")
    return documents


def chunk_documents(documents):
    print(f"Chunking into ~{CHUNK_SIZE}-token pieces with {CHUNK_OVERLAP}-token overlap ...")
    splitter = SentenceSplitter(chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP)
    nodes = splitter.get_nodes_from_documents(documents)
    print(f"  Produced {len(nodes)} chunks.")
    return nodes


def build_vector_store(nodes):
    print(f"Setting up ChromaDB at {CHROMA_DIR} ...")
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))

    try:
        client.delete_collection(COLLECTION_NAME)
        print(f"  Removed existing collection '{COLLECTION_NAME}'.")
    except Exception:
        pass

    embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBED_MODEL_NAME
    )
    collection = client.create_collection(
        name=COLLECTION_NAME, embedding_function=embedding_fn
    )

    print(f"Embedding and storing {len(nodes)} chunks (model: {EMBED_MODEL_NAME}) ...")

    batch_size = 256
    for start in range(0, len(nodes), batch_size):
        batch = nodes[start:start + batch_size]
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
        done = min(start + batch_size, len(nodes))
        print(f"  Stored {done}/{len(nodes)} chunks.")

    print(f"Done. Collection '{COLLECTION_NAME}' now has {collection.count()} chunks.")
    return collection


def main():
    documents = load_documents(CORPUS_DIR)
    nodes = chunk_documents(documents)
    build_vector_store(nodes)
    print("\nIngestion complete. The vector store is ready for retrieval.")


if __name__ == "__main__":
    main()
