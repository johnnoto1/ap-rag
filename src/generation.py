"""
generation.py — End-to-end RAG with a scope guardrail.

Retrieves relevant chunks, checks whether the question is within the
scope of the corpus (using retrieval distances as a signal), and either
declines (out of scope) or generates a grounded answer from a local
Ollama model.

Usage:
    uv run python src/generation.py "your question here"
    uv run python src/generation.py            # uses a default demo query
"""

import sys

import ollama

from retrieval import retrieve, TOP_K

GEN_MODEL = "qwen2.5:7b"

# --- Scope guardrail configuration -----------------------------------------
# Tuned from observed distances: clean in-scope questions retrieve several
# chunks below ~0.42; out-of-scope questions get at most a lucky near-match
# then fall off steeply. We require BOTH a close best match AND enough
# supporting chunks to consider a question in-scope.
SCOPE_DISTANCE_THRESHOLD = 0.42   # a chunk is "close" if below this
MIN_CLOSE_CHUNKS = 2              # need at least this many close chunks


PROMPT_TEMPLATE = """You are a careful anatomy and physiology tutor. Answer the \
student's question using ONLY the context provided below. If the context does \
not contain enough information to answer, say so plainly rather than guessing.

Context:
{context}

Question: {question}

Answer:"""

OUT_OF_SCOPE_MESSAGE = (
    "This question appears to be outside the scope of our course materials. "
    "I can only answer using the assigned textbook, and I couldn't find enough "
    "relevant material to give you a reliable, grounded answer. If you think "
    "this should be covered, check with your instructor or rephrase the "
    "question in terms of the course content."
)


def in_scope(hits):
    """Decide whether retrieved hits indicate the question is in-scope.

    Returns (is_in_scope, diagnostics_dict) so the caller can explain the
    decision — useful for a live demo.
    """
    distances = [dist for (_doc, _meta, dist) in hits]
    best = min(distances) if distances else None
    close_count = sum(1 for d in distances if d < SCOPE_DISTANCE_THRESHOLD)

    is_in_scope = (
        best is not None
        and best < SCOPE_DISTANCE_THRESHOLD
        and close_count >= MIN_CLOSE_CHUNKS
    )
    diagnostics = {
        "best_distance": best,
        "close_chunks": close_count,
        "threshold": SCOPE_DISTANCE_THRESHOLD,
        "min_close_required": MIN_CLOSE_CHUNKS,
    }
    return is_in_scope, diagnostics


def format_context(hits):
    blocks = []
    for i, (doc, meta, _dist) in enumerate(hits, 1):
        page = meta.get("page", "?")
        blocks.append(f"[{i}] (page {page}) {doc.strip()}")
    return "\n\n".join(blocks)


def answer(question, top_k=TOP_K):
    """Return (answer_text, hits, in_scope_flag, diagnostics)."""
    hits = retrieve(question, top_k=top_k)
    is_in, diag = in_scope(hits)

    if not is_in:
        return OUT_OF_SCOPE_MESSAGE, hits, False, diag

    context = format_context(hits)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)
    response = ollama.chat(
        model=GEN_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"], hits, True, diag


def main():
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "Why does the left ventricle have a thicker wall than the right ventricle?"

    print(f"Question: {question}\n")

    text, hits, is_in, diag = answer(question)

    # Show the scope decision first — this is the demo's teaching moment.
    print("=" * 70)
    print("SCOPE CHECK")
    print("=" * 70)
    print(f"  Best match distance : {diag['best_distance']:.4f}")
    print(f"  Chunks under {diag['threshold']:.2f}   : {diag['close_chunks']} "
          f"(need >= {diag['min_close_required']})")
    print(f"  Verdict             : {'IN SCOPE' if is_in else 'OUT OF SCOPE'}")
    print()

    if is_in:
        print("=" * 70)
        print("ANSWER")
        print("=" * 70)
        print(text.strip())
        print()
        print("=" * 70)
        print("SOURCES USED")
        print("=" * 70)
        for i, (_doc, meta, dist) in enumerate(hits, 1):
            print(f"  [{i}] page {meta.get('page')}  (distance {dist:.4f})")
    else:
        print("=" * 70)
        print("RESPONSE (declined)")
        print("=" * 70)
        print(text.strip())
        print()
        print("  (Nearest chunks considered, for transparency:)")
        for i, (_doc, meta, dist) in enumerate(hits, 1):
            print(f"    [{i}] page {meta.get('page')}  (distance {dist:.4f})")


if __name__ == "__main__":
    main()
