# Running Notes

## 2026-05-18 — First retrieval observations (baseline, all-MiniLM-L6-v2)

### Query: "What happens during ventricular systole?"
- Strong retrieval. Distances 0.36–0.41, all from cardiac cycle section (pp. 822–843).
- Result 2 was the best answer but ranked #2; Result 1 ranked higher despite
  drifting into pericardial anatomy after opening with the phrase "ventricular systole."
- FAILURE MODE: lexical match (exact phrase at chunk start) outranked semantic
  relevance. Motivates reranking.

### Query: "How is blood pressure regulated?"
- Looser distances (0.40–0.45). Results scattered: cardiovascular (pp. 874–877)
  AND renal (pp. 1181–1185, chapter 25).
- Renal chunks are topically valid (renin-angiotensin) but pedagogically
  out-of-scope for a student in the cardiovascular unit.
- FAILURE MODE: scope-blind retrieval. Semantic similarity ignores pedagogical
  context (what unit/chapter the student is working in). Motivates metadata
  filtering or chapter-aware retrieval.