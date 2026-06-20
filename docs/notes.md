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

  ## 2026-05-18 — Full RAG pipeline working (qwen2.5:7b generation)

### Query: "Why does the left ventricle have a thicker wall...?"
- Excellent answer. Correct (systemic vs pulmonary resistance), grounded in
  heart anatomy section (pp. 796-802), obeyed prompt, pedagogically clear.
- OPEN QUESTION: answer quality may partly reflect qwen2.5's own training
  knowledge, not purely retrieval. Need a probe where textbook framing and
  model knowledge diverge to test true grounding.

### Query: "How is blood pressure regulated?" (full pipeline)
- Answer is comprehensive and accurate (neural, baroreceptors, RAAS,
  sympathetic, cardiac output) — would score high on standard RAG metrics
  (faithfulness, correctness, relevance).
- BUT incorporated renal-chapter content (RAAS, juxtaglomerular cells,
  aldosterone/Na+ reabsorption; sources pp. 1181, 1185 = chapter 25).
- KEY INSIGHT: answer quality and pedagogical appropriateness are
  DIFFERENT AXES. Naive RAG optimizes comprehensiveness/correctness and is
  blind to learner scope. A student in the cardiovascular unit may be
  confused or overwhelmed by kidney physiology they haven't studied.
- This is the central tension the project targets: standard RAG metrics
  would call this a success; an A&P instructor sees a scope mismatch.
- Possible mitigations to test later: metadata filtering by chapter,
  chapter-aware retrieval, or a pedagogical-scope instruction in the prompt.