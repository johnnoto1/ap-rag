# Tier-2: four sibling tutors (Microbiology · Psychology · U.S. History · Economics)

A minimal extension of A&P RAG. **Same pipeline, same guardrail, same output** —
only the textbook differs. Each subject is one OpenStax book ingested into its own
Chroma collection and queried through one wrapper.

Nothing about the core changed. `ingest.py`, `retrieval.py`, and `generation.py`
still run A&P RAG exactly as before. The only edit to existing code is one
backward-compatible optional argument (`collection_name`) added to
`retrieval.get_collection` / `retrieval.retrieve`.

## New files

| File | What it does |
|------|--------------|
| `src/subjects.py` | Registry: subject key → PDF, collection, label, persona, page offset. **Add a book here.** |
| `src/ingest_subject.py` | Build ONE collection from ONE book. Pre-build step. |
| `src/query.py` | One-command query wrapper: `--subject X "question"`. |
| `src/pretest.py` | Generates the verified-behavior table (retrieval only, fast). |
| `src/check_pages.py` | Find each book's PDF→printed page offset. |

## One-time setup (per book, runs minutes, never live)

Put the four PDFs in `data/corpus/` with these exact names:

```
data/corpus/microbiology_-_WEB.pdf
data/corpus/Psychology2e_WEB.pdf
data/corpus/US_History_-_WEB.pdf
data/corpus/principles-economics-3e_-_WEB.pdf
```

Then build each collection:

```bash
uv run python src/ingest_subject.py microbiology
uv run python src/ingest_subject.py psychology
uv run python src/ingest_subject.py history
uv run python src/ingest_subject.py economics
```

Expect ~2,500+ chunks per book and a few minutes each on an M1. The A&P
collection (`ap_cardiovascular`) is protected — the script refuses to touch it.

## Query a subject (this is the live command)

```bash
uv run python src/query.py --subject psychology "How does classical conditioning work?"
uv run python src/query.py --subject microbiology "What is the Gram stain?"
```

Output is identical to Demo 1: a `SCOPE CHECK` block, then either
`ANSWER` + `SOURCES USED`, or a declined `RESPONSE`. A one-line `SUBJECT:` banner
is added on top so the room sees which book is loaded.

## Verify behavior before the talk (do this!)

```bash
uv run python src/pretest.py            # all subjects, ~seconds (no Ollama needed)
uv run python src/pretest.py economics  # just one
```

It runs 3 in-scope + 2 out-of-scope frozen questions per book and prints best
distance, # close chunks, and verdict — paste straight into the run-of-show table.
A guardrail is "sane" when all IN answer and all OUT decline.

- **Self-check:** `uv run python src/pretest.py ap` should reproduce your frozen
  A&P numbers (0.31/3, 0.40/2, 0.39/1, 0.57/0, 0.40/1). If it does, trust the
  sibling numbers.
- **The 0.42/2 threshold was tuned for A&P.** If a corpus leaks (out-of-scope
  answers) or misses (in-scope declines), either swap the question or drop the
  corpus from the live menu. Four solid beats six shaky.

## Page-accurate citations (requirement: audience can turn to the page)

Citations store the **PDF physical page**, not the printed book page. To map them:

```bash
uv run python src/check_pages.py microbiology
```

Read the printed page number off the extracted header/footer, compute
`page_offset = pdf_page - printed_page`, and put it in that subject's entry in
`subjects.py`. Citations will then show real book pages. Leave it `0` if you'll
just tell the room "page in the PDF."

## Keep the model warm (avoid the cold-start pause live)

Generation uses Ollama `qwen2.5:7b`, which idles out of memory. Right before the
Demo 2 segment, run one throwaway query so the model is resident:

```bash
export HF_HUB_OFFLINE=1   # suppress the HuggingFace warning for a clean screen
uv run python src/query.py --subject microbiology "What is a microbe?"
```

Then your first real audience query returns in the usual ~15–20 s instead of
waiting on a cold load.

## Add a brand-new subject live (the "build one from scratch" finale)

1. Drop `newbook.pdf` in `data/corpus/`.
2. Add an entry to `SUBJECTS` in `src/subjects.py` (key, pdf, collection, label, persona).
3. `uv run python src/ingest_subject.py newsubject`
4. `uv run python src/query.py --subject newsubject "a question"`

That's the whole trick: swap the textbook, same ~200 lines.
