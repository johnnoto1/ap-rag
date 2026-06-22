# VERIFIED DEMO BEHAVIOR — Tier-2 corpora

> Confirmed on-machine via `uv run python src/pretest.py`. Guardrail: threshold
> **0.42**, minimum **2** close chunks (A&P-tuned — transferred to all four books
> unmodified). Page offsets set per book in `src/subjects.py`.

## Corpus summary

| Corpus | Chunks | Offset | IN-scope (×3) answer? | OUT-of-scope (×2) decline? | Guardrail sane? | In live menu? |
|---|---|---|---|---|---|---|
| Microbiology | 2318 | 14 | YES | YES | YES | YES |
| Psychology 2e | 1528 | 12 | YES | YES | YES | YES |
| U.S. History | 1888 | 16 | YES | YES | YES | YES (thin margins) |
| Economics 3e | 1891 | 14 | YES | YES | YES | YES |

---

## Microbiology — `--subject microbiology`

| Question | Verdict | Best dist | Close chunks |
|---|---|---|---|
| What is the structure of a bacterial cell wall? | IN SCOPE — answers | 0.3548 | 5 |
| How does the Gram stain differentiate bacteria? | IN SCOPE — answers | 0.2317 | 5 |
| What are the stages of the bacteriophage lytic cycle? | IN SCOPE — answers | 0.2787 | 5 |
| What were the causes of the American Civil War? | OUT OF SCOPE — declines | 0.7529 | 0 |
| How does the Federal Reserve set interest rates? | OUT OF SCOPE — declines | 0.8041 | 0 |

## Psychology 2e — `--subject psychology`

| Question | Verdict | Best dist | Close chunks |
|---|---|---|---|
| What are the stages of Piaget's theory of cognitive development? | IN SCOPE — answers | 0.2342 | 5 |
| How does classical conditioning work? | IN SCOPE — answers | 0.2838 | 5 |
| What is the difference between short-term and long-term memory? | IN SCOPE — answers | 0.3039 | 4 |
| What is the structure of a prokaryotic cell wall? | OUT OF SCOPE — declines | 0.5911 | 0 |
| What was the significance of the Louisiana Purchase? | OUT OF SCOPE — declines | 0.7404 | 0 |

## U.S. History — `--subject history`

| Question | Verdict | Best dist | Close chunks |
|---|---|---|---|
| What was the Missouri Compromise? | IN SCOPE — answers | 0.3583 | 3 |
| What was the significance of the Declaration of Independence? | IN SCOPE — answers | 0.3559 | 2 |
| What were the major programs of the New Deal? | IN SCOPE — answers | 0.3256 | 3 |
| How does an enzyme lower activation energy? | OUT OF SCOPE — declines | 0.8788 | 0 |
| What is operant conditioning in psychology? | OUT OF SCOPE — declines | 0.6357 | 0 |

> Note: this book writes narratively, so topics scatter. Scattered phrasings
> ("causes of the Civil War", "significance of Gettysburg") declined at ~0.40/1 —
> swapped for the concentrated questions above. A vague audience question may
> decline; pivot to a frozen question (run-of-show fallback ladder).

## Principles of Economics 3e — `--subject economics`

| Question | Verdict | Best dist | Close chunks |
|---|---|---|---|
| What is the law of supply and demand? | IN SCOPE — answers | 0.2850 | 5 |
| What is comparative advantage in trade? | IN SCOPE — answers | 0.2946 | 5 |
| How does a price ceiling create a shortage? | IN SCOPE — answers | 0.3056 | 5 |
| What are the four chambers of the human heart? | OUT OF SCOPE — declines | 0.8041 | 0 |
| How does DNA replication work? | OUT OF SCOPE — declines | 0.8231 | 0 |

---

## Back-pocket picks (strongest margin per corpus)

| Corpus | Go-to IN-scope | Go-to OUT-of-scope |
|---|---|---|
| Microbiology | How does the Gram stain differentiate bacteria? (0.2317/5) | How does the Federal Reserve set interest rates? (0.8041/0) |
| Psychology 2e | What are the stages of Piaget's theory...? (0.2342/5) | What was the significance of the Louisiana Purchase? (0.7404/0) |
| U.S. History | What was the Missouri Compromise? (0.3583/3) | How does an enzyme lower activation energy? (0.8788/0) |
| Economics 3e | What is the law of supply and demand? (0.2850/5) | How does DNA replication work? (0.8231/0) |
