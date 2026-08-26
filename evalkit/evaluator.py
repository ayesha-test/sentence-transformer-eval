from typing import Any

from evalkit.config import (
    PASS_THRESHOLD,
    WEIGHT_COVERAGE,
    WEIGHT_SIMILARITY,
    WEIGHT_STRUCTURE,
)
from evalkit.coverage import score_coverage
from evalkit.similarity import score_similarity
from evalkit.structure import score_structure


def evaluate_output(item: dict[str, Any]) -> dict[str, Any]:
    item_id = item.get("id") or item.get("ticket_id") or "unknown"
    source = item.get("source_text") or item.get("original_text") or ""
    output = item.get("generated_output") or item.get("generated_summary") or ""

    struct_score, struct_reasons = score_structure(output)
    cov_score, cov_reasons, missing = score_coverage(source, output)
    sim_score, sim_reasons = score_similarity(source, output)

    overall = (
        WEIGHT_STRUCTURE * struct_score
        + WEIGHT_COVERAGE * cov_score
        + WEIGHT_SIMILARITY * sim_score
    )

    passed = overall >= PASS_THRESHOLD and not missing
    reasons = struct_reasons + cov_reasons + sim_reasons
    if not passed:
        if overall < PASS_THRESHOLD:
            reasons.append(f"overall score {overall:.3f} below threshold {PASS_THRESHOLD}")
        if missing:
            reasons.append("failed: missing critical terms (hard gate)")

    return {
        "id": item_id,
        "label": item.get("label", ""),
        "passed": passed,
        "overall_score": round(overall, 4),
        "structure_score": round(struct_score, 4),
        "coverage_score": round(cov_score, 4),
        "similarity_score": round(sim_score, 4),
        "missing_terms": missing,
        "reasons": reasons,
    }


def evaluate_all(items: list[dict[str, Any]]) -> dict[str, Any]:
    results = [evaluate_output(item) for item in items]
    passed_count = sum(1 for result in results if result["passed"])
    return {
        "summary": {
            "total": len(results),
            "passed": passed_count,
            "failed": len(results) - passed_count,
            "pass_rate": round(passed_count / len(results), 4) if results else 0.0,
        },
        "results": results,
    }
