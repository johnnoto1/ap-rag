"""check_pages.py — find the PDF-to-printed-page offset for a book.

Citations store the PDF's physical page index (page_index + 1). OpenStax
WEB PDFs have front matter, so the printed page number on the page is
smaller by a fixed offset. This script dumps a few pages of extracted text
so you can read the printed page number off the running header/footer and
compute:  page_offset = pdf_page - printed_page

Put that number in subjects.py and citations will show real book pages.

It also flags two-column extraction garbage (headers/footers/figure
captions bleeding into the text).

Usage:
    uv run python src/check_pages.py microbiology
    uv run python src/check_pages.py economics 60 120 300   # custom pages
"""

import sys
from pypdf import PdfReader

from subjects import get


def main():
    if len(sys.argv) < 2:
        raise SystemExit("Usage: uv run python src/check_pages.py <subject> [pdf_page ...]")

    cfg = get(sys.argv[1])
    pages = [int(p) for p in sys.argv[2:]] or [1, 30, 100, 300, 600]

    if not cfg["pdf_path"].exists():
        raise SystemExit(f"PDF not found: {cfg['pdf_path']}")

    reader = PdfReader(str(cfg["pdf_path"]))
    print(f"{cfg['label']} — {len(reader.pages)} physical PDF pages\n")
    print("For each sample: read the PRINTED page number off the text, then")
    print("offset = (PDF page shown here) - (printed page you see).\n")

    for pdf_page in pages:
        idx = pdf_page - 1  # 1-based PDF page -> 0-based index
        if idx < 0 or idx >= len(reader.pages):
            continue
        text = reader.pages[idx].extract_text() or ""
        print("=" * 70)
        print(f"PDF page {pdf_page}  |  extracted {len(text):,} chars")
        print("=" * 70)
        # Show head and tail — printed page numbers usually live in the
        # header or footer, and the tail reveals caption/footer garbage.
        print("  [head] " + repr(text[:200]))
        print("  [tail] " + repr(text[-200:]))
        print()


if __name__ == "__main__":
    main()
