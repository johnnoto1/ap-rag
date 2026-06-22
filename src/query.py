"""query.py — one-command, multi-subject RAG tutor.

Same pipeline, same guardrail, same output as A&P RAG's generation.py.
The ONLY differences: it queries the collection for the chosen subject,
and its prompt persona is subject-neutral. On stage you type one thing:

    uv run python src/query.py --subject psychology "your question"
    uv run python src/query.py --subject microbiology "your question"
    uv run python src/query.py --subject history "your question"
    uv run python src/query.py --subject economics "your question"

The SCOPE CHECK / ANSWER / SOURCES USED blocks are byte-identical to
Demo 1 so the audience sees the same behavior on a different book.
"""

import argparse

import ollama

# Reuse the existing pipeline pieces — do NOT duplicate the guardrail.
from retrieval import retrieve, TOP_K
from generation import (
    in_scope,
    format_context,
    OUT_OF_SCOPE_MESSAGE,
    GEN_MODEL,
)
from subjects import get

# Subject-neutral version of generation.py's prompt. For A&P this renders
# as "a careful anatomy and physiology tutor" — identical to the original.
PROMPT_TEMPLATE = """You are a careful {persona} tutor. Answer the \
student's question using ONLY the context provided below. If the context \
does not contain enough information to answer, say so plainly rather than \
guessing.

Context:
{context}

Question: {question}

Answer:"""


def printed_page(meta, cfg):
    """Apply the per-book page offset for citations, if one is set."""
    page = meta.get("page")
    offset = cfg.get("page_offset", 0)
    if offset and isinstance(page, int):
        return page - offset
    return page


def answer(question, cfg, top_k=TOP_K):
    """Return (answer_text, hits, in_scope_flag, diagnostics)."""
    hits = retrieve(question, top_k=top_k, collection_name=cfg["collection"])
    is_in, diag = in_scope(hits)

    if not is_in:
        return OUT_OF_SCOPE_MESSAGE, hits, False, diag

    context = format_context(hits)
    prompt = PROMPT_TEMPLATE.format(
        persona=cfg["persona"], context=context, question=question
    )
    response = ollama.chat(
        model=GEN_MODEL,
        messages=[{"role": "user", "content": prompt}],
    )
    return response["message"]["content"], hits, True, diag


def main():
    parser = argparse.ArgumentParser(
        description="Query a subject-bounded RAG tutor."
    )
    parser.add_argument(
        "--subject", required=True,
        help="microbiology | psychology | history | economics | ap",
    )
    parser.add_argument("question", nargs="+", help="the student's question")
    args = parser.parse_args()

    cfg = get(args.subject)
    question = " ".join(args.question)

    # Banner so the audience can see which book is loaded.
    print("=" * 70)
    print(f"SUBJECT: {cfg['label']}   (collection: {cfg['collection']})")
    print("=" * 70)
    print(f"Question: {question}\n")

    text, hits, is_in, diag = answer(question, cfg)

    # --- SCOPE CHECK: identical format to Demo 1 ---------------------------
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
            print(f"  [{i}] page {printed_page(meta, cfg)}  "
                  f"(distance {dist:.4f})")
    else:
        print("=" * 70)
        print("RESPONSE (declined)")
        print("=" * 70)
        print(text.strip())
        print()
        print("  (Nearest chunks considered, for transparency:)")
        for i, (_doc, meta, dist) in enumerate(hits, 1):
            print(f"    [{i}] page {printed_page(meta, cfg)}  "
                  f"(distance {dist:.4f})")


if __name__ == "__main__":
    main()
