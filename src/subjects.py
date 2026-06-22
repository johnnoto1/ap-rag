"""subjects.py — registry of corpora for the multi-subject RAG tutors.

One entry per OpenStax book. Each sibling tutor is IDENTICAL to A&P RAG
except for which PDF it ingested and which Chroma collection it queries.
The method travels unchanged; only the textbook differs.

To add a new subject: drop its PDF in data/corpus/ and add one entry here.

  key          -> what you type on the CLI (e.g. --subject psychology)
  pdf          -> filename inside data/corpus/
  collection   -> Chroma collection name (must be unique)
  label        -> human-readable name shown on screen during the demo
  persona      -> fills the prompt: "a careful {persona} tutor"
  page_offset  -> printed_page = pdf_page - page_offset  (see docs/tier2.md);
                  leave 0 until you've checked the book (procedure in docs).
"""

from pathlib import Path

CORPUS_DIR = Path("data/corpus")

SUBJECTS = {
    # Existing A&P collection. Included so --subject ap works in the wrapper,
    # but ingest_subject.py REFUSES to (re)build it — it is already ingested.
    "ap": {
        "pdf": "anatomy-and-physiology-2e_-_WEB.pdf",
        "collection": "ap_cardiovascular",
        "label": "Anatomy & Physiology 2e",
        "persona": "anatomy and physiology",
        "page_offset": 0,
    },
    "microbiology": {
        "pdf": "microbiology_-_WEB.pdf",
        "collection": "micro_full",
        "label": "Microbiology",
        "persona": "microbiology",
        "page_offset": 14,
    },
    "psychology": {
        "pdf": "Psychology2e_WEB.pdf",
        "collection": "psychology_full",
        "label": "Psychology 2e",
        "persona": "psychology",
        "page_offset": 12,
    },
    "history": {
        "pdf": "US_History_-_WEB.pdf",
        "collection": "ushistory_full",
        "label": "U.S. History",
        "persona": "U.S. history",
        "page_offset": 16,
    },
    "economics": {
        "pdf": "principles-economics-3e_-_WEB.pdf",
        "collection": "economics_full",
        "label": "Principles of Economics 3e",
        "persona": "economics",
        "page_offset": 14,
    },
}

# Subjects that should never be (re)ingested by ingest_subject.py.
PROTECTED = {"ap"}


def get(subject):
    """Look up a subject config by key. Exits cleanly on an unknown key."""
    key = subject.strip().lower()
    if key not in SUBJECTS:
        valid = ", ".join(k for k in SUBJECTS if k not in PROTECTED)
        raise SystemExit(
            f"Unknown subject '{subject}'.\n"
            f"Valid subjects: {valid}"
        )
    cfg = dict(SUBJECTS[key])
    cfg["key"] = key
    cfg["pdf_path"] = CORPUS_DIR / cfg["pdf"]
    return cfg
