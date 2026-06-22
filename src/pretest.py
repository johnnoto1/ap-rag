"""pretest.py — generate the verified-behavior table for the run-of-show.

For each subject, runs a frozen set of known-good IN-SCOPE and OUT-OF-SCOPE
questions and prints best-match distance, # close chunks, and the verdict,
in the same format as the A&P verified-behavior table.

This uses RETRIEVAL ONLY — no Ollama, no generation — so it runs in
seconds. The scope verdict depends only on distances, which is exactly
what the table reports. (To also see generated answers, use query.py.)

Usage:
    uv run python src/pretest.py                 # all subjects
    uv run python src/pretest.py microbiology    # one subject
    uv run python src/pretest.py ap              # self-check vs the frozen A&P table

A subject's guardrail is "sane" when all IN questions answer and all OUT
questions decline. If a corpus misbehaves, drop it from the live menu.
"""

import sys

from retrieval import retrieve, TOP_K
from generation import in_scope
from subjects import get, SUBJECTS

# --- Frozen question sets ---------------------------------------------------
# These are CANDIDATES. Verify each one with this script on YOUR machine;
# the 0.42/2 threshold was tuned for A&P and may not transfer. Swap any that
# misbehave. OUT-OF-SCOPE items are deliberately drawn from a different
# subject so they are guaranteed off-book.
QUESTIONS = {
    # A&P included as a SELF-CHECK: if these reproduce your frozen numbers
    # (0.31/3, 0.40/2, 0.39/1, 0.57/0, 0.40/1) the harness is trustworthy.
    "ap": {
        "in_scope": [
            "What are the phases of the cardiac cycle?",
            "What is the function of the semilunar valves?",
        ],
        "out_of_scope": [
            "What medications are used to treat high blood pressure?",
            "What should I eat to keep my heart healthy?",
            "How is blood pressure regulated?",
        ],
    },
    "microbiology": {
        "in_scope": [
            "What is the structure of a bacterial cell wall?",
            "How does the Gram stain differentiate bacteria?",
            "What are the stages of the bacteriophage lytic cycle?",
        ],
        "out_of_scope": [
            "What were the causes of the American Civil War?",
            "How does the Federal Reserve set interest rates?",
        ],
    },
    "psychology": {
        "in_scope": [
            "What are the stages of Piaget's theory of cognitive development?",
            "How does classical conditioning work?",
            "What is the difference between short-term and long-term memory?",
        ],
        "out_of_scope": [
            "What is the structure of a prokaryotic cell wall?",
            "What was the significance of the Louisiana Purchase?",
        ],
    },
    "history": {
        "in_scope": [
            "What was the Missouri Compromise?",
            "What was the significance of the Declaration of Independence?",
            "What were the major programs of the New Deal?",
        ],
        "out_of_scope": [
            "How does an enzyme lower activation energy?",
            "What is operant conditioning in psychology?",
        ],
    },
    "economics": {
        "in_scope": [
            "What is the law of supply and demand?",
            "What is comparative advantage in trade?",
            "How does a price ceiling create a shortage?",
        ],
        "out_of_scope": [
            "What are the four chambers of the human heart?",
            "How does DNA replication work?",
        ],
    },
}


def run_one(question, collection_name):
    """Return (best_distance, close_chunks, is_in_scope) for one question."""
    hits = retrieve(question, top_k=TOP_K, collection_name=collection_name)
    is_in, diag = in_scope(hits)
    return diag["best_distance"], diag["close_chunks"], is_in


def report_subject(key):
    cfg = get(key)
    qs = QUESTIONS.get(key)
    if qs is None:
        print(f"(no frozen questions defined for '{key}', skipping)\n")
        return

    print("=" * 78)
    print(f"{cfg['label']}   (collection: {cfg['collection']})")
    print("=" * 78)
    print(f"{'Question':<52}{'Verdict':<16}{'Dist':<8}Close")
    print("-" * 78)

    all_in_ok, all_out_ok = True, True
    try:
        for q in qs["in_scope"]:
            best, close, is_in = run_one(q, cfg["collection"])
            verdict = "IN — answers" if is_in else "IN — *MISSED*"
            all_in_ok = all_in_ok and is_in
            print(f"{q[:50]:<52}{verdict:<16}{best:<8.4f}{close}")
        for q in qs["out_of_scope"]:
            best, close, is_in = run_one(q, cfg["collection"])
            verdict = "OUT — *LEAK*" if is_in else "OUT — declines"
            all_out_ok = all_out_ok and (not is_in)
            print(f"{q[:50]:<52}{verdict:<16}{best:<8.4f}{close}")
    except Exception as exc:
        print(f"\n  !! Could not query '{cfg['collection']}': {exc}")
        print(f"  Build it first: uv run python src/ingest_subject.py {key}\n")
        return

    sane = all_in_ok and all_out_ok
    print("-" * 78)
    print(f"Guardrail sane? {'YES' if sane else 'NO — review flagged rows above'}")
    print()


def main():
    if len(sys.argv) > 1:
        keys = sys.argv[1:]
    else:
        keys = [k for k in SUBJECTS]  # all, ap first for the self-check

    print("\nPRETEST — verified demo behavior (retrieval-only, no generation)\n")
    for key in keys:
        report_subject(key)
    print("Paste the rows above into the VERIFIED DEMO BEHAVIOR table.")
    print("Drop any corpus whose guardrail is NOT sane — four solid beats six shaky.\n")


if __name__ == "__main__":
    main()
