#!/usr/bin/env python3
"""Show why semantic similarity is used instead of lexical overlap.

Prints Jaccard token overlap (BLEU-like) next to sentence-transformer cosine
similarity for the same pairs. A good paraphrase scores low lexically and
high semantically; that is the case lexical metrics miss.
"""

from __future__ import annotations

import json
from pathlib import Path

from evalkit.lexical import jaccard
from evalkit.similarity import score_similarity

PAIRS = [
    {
        "name": "classic paraphrase",
        "source": "The cat sat on the mat.",
        "output": "A feline was resting on the rug.",
    },
    {
        "name": "ticket paraphrase",
        "source": "Customer cannot log in on Android version 14 after the latest update.",
        "output": "Login is broken on Android 14 following the recent update.",
    },
    {
        "name": "near copy-paste",
        "source": "Payments fail on iOS 17. Token refresh returns invalid token.",
        "output": "Payments fail on iOS 17. Token refresh returns invalid token during checkout.",
    },
    {
        "name": "unrelated",
        "source": "Two-factor authentication codes are not arriving on mobile.",
        "output": "The billing page layout has been updated for the admin panel.",
    },
]


def main() -> None:
    rows = []
    print(f"{'pair':<22} {'jaccard':>8} {'cosine':>8}  note")
    print("-" * 72)
    for pair in PAIRS:
        lex = jaccard(pair["source"], pair["output"])
        cosine, _ = score_similarity(pair["source"], pair["output"])
        if cosine - lex >= 0.25:
            note = "paraphrase: lexical low, semantic high"
        elif lex >= 0.7 and cosine >= 0.7:
            note = "copy-ish: both metrics agree"
        else:
            note = "low overlap on both"
        print(f"{pair['name']:<22} {lex:8.3f} {cosine:8.3f}  {note}")
        rows.append(
            {
                "name": pair["name"],
                "jaccard": round(lex, 4),
                "cosine": round(cosine, 4),
                "note": note,
            }
        )

    out = Path(__file__).parent / "compare_report.json"
    out.write_text(json.dumps(rows, indent=2) + "\n")
    print(f"\nWrote {out}")


if __name__ == "__main__":
    main()
