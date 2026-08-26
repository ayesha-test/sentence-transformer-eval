# Semantic evaluation of LLM outputs

Offline evaluator for generated text. **Sentence-transformer embeddings** score whether an AI output means the same thing as the source. Keyword coverage and a length check sit in front so a fluent, off-topic answer cannot pass on similarity alone.

This is the pattern I use when judging non-deterministic AI: lexical metrics (BLEU, ROUGE, token overlap) punish valid paraphrase and reward copy-paste. Cosine similarity on `all-MiniLM-L6-v2` does the opposite — it scores meaning.

```
source text ──► [structure] ──► [term coverage] ──► [sentence-transformer cosine]
                     20%              60%                     20%
                                      │
                              missing term = fail
```

## Why sentence transformers, not BLEU / ROUGE

`python compare_metrics.py` prints this on the bundled pairs (`all-MiniLM-L6-v2`):

| Pair | Jaccard (lexical) | Cosine (semantic) |
|---|---|---|
| Ticket paraphrase (rewrite, same facts) | 0.29 | **0.86** |
| Near copy-paste | 0.82 | 0.98 |
| Unrelated sentences | 0.00 | 0.11 |
| Classic "cat/mat" vs "feline/rug" | 0.20 | 0.56 |

BLEU and ROUGE count overlapping n-grams. A good summary that rewrites the source looks like a failure. A bad summary that copies a sentence and drops a critical fact can look like a pass.

The ticket paraphrase is the case that matters: lexical overlap is low, cosine is high, and a human would call it correct. MiniLM is a small model — "cat" vs "feline" only reaches 0.56 — so I use it as a semantic signal, not as the whole judge. Coverage (60%) is the hard gate for dropped facts.

The embedding layer does **not** fix faithfulness. A model can add an invented refund, keep the right keywords, and still score high (see `hallucination-gap` in the samples). Catching that needs NLI or an LLM-as-judge, which this repo keeps out so the run stays local, free, and deterministic.

## Scoring

| Layer | Weight | What it catches |
|---|---|---|
| Structure | 20% | Empty or out-of-bounds output |
| Coverage | 60% | Dropped facts (platforms, versions, "no workaround") |
| Similarity | 20% | Off-topic or weakly related output |

**Pass:** overall ≥ 0.75 **and** zero missing critical terms. Coverage is a hard gate: a polished summary that omits `Android 14` still fails.

Measured on `data/samples.json`:

| Case | Result | Overall | Similarity | What it shows |
|---|---|---|---|---|
| Good paraphrase | PASS | 0.98 | 0.91 | Rewrite still looks like the source |
| Near copy-paste | PASS | 1.00 | 0.98 | Lexical and semantic agree |
| Drops critical facts | FAIL | 0.44 | 0.61 | Similarity is middling; coverage hard-fails |
| Invented refund | PASS | 0.97 | 0.86 | Faithfulness gap: extra fact still passes |
| Unrelated output | FAIL | 0.22 | 0.11 | Off-topic text is scored down |
| Empty output | FAIL | 0.00 | 0.00 | Structure layer catches garbage output |

## Run

Python 3.9+. First run downloads `all-MiniLM-L6-v2` (~80 MB).

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python run_eval.py
python compare_metrics.py
```

`run_eval.py` prints a per-item report and writes `report.json`. Point it at your own data with `--data path/to/items.json`. Each item needs `id`, `source_text`, and `generated_output`.

```bash
pip install -r requirements-dev.txt
pytest tests/ -q
```

Unit tests mock the embedding model so CI does not download weights.

## Layout

```
evalkit/
  structure.py     # layer 1
  coverage.py      # layer 2 — rule-based terms from the source
  similarity.py    # layer 3 — all-MiniLM-L6-v2 cosine
  evaluator.py     # weights, hard gate, pass/fail
  lexical.py       # Jaccard overlap for the comparison script
data/samples.json  # six labelled cases
run_eval.py
compare_metrics.py
```

## What this is for

Evaluating LLM-generated support-ticket summaries, or any setting where you have a source document and a generated rewrite. Swap the coverage term lists in `evalkit/coverage.py` if your domain is different; leave the similarity layer as-is.
