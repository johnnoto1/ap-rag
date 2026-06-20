"""Diagnostic: test pypdf text extraction on the corpus PDF."""

from pathlib import Path
from pypdf import PdfReader

PDF_PATH = Path("data/corpus/anatomy-and-physiology-2e_-_WEB.pdf")

print(f"Opening {PDF_PATH.name} ...")
reader = PdfReader(str(PDF_PATH))
print(f"Number of pages: {len(reader.pages)}")
print()

# Extract a few representative pages and show what the text looks like.
# Page 0 is usually a cover; sample some pages from the middle of the book.
for page_num in [0, 100, 500, 800]:
    if page_num < len(reader.pages):
        text = reader.pages[page_num].extract_text()
        print(f"--- Page {page_num} ---")
        print(f"  Text length: {len(text):,} chars")
        print(f"  First 300 chars:")
        print("  " + repr(text[:300]))
        print()