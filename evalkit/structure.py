from evalkit.config import MAX_SUMMARY_LENGTH, MIN_SUMMARY_LENGTH


def score_structure(output: str) -> tuple[float, list[str]]:
    """Layer 1: non-empty output within length bounds. Score is 0–1."""
    text = output.strip()
    if not text:
        return 0.0, ["output is empty"]

    length = len(text)
    min_ok = length >= MIN_SUMMARY_LENGTH
    max_ok = length <= MAX_SUMMARY_LENGTH
    reasons: list[str] = []

    if not min_ok:
        reasons.append(f"output too short ({length} < {MIN_SUMMARY_LENGTH} chars)")
    if not max_ok:
        reasons.append(f"output too long ({length} > {MAX_SUMMARY_LENGTH} chars)")
    if min_ok and max_ok:
        reasons.append("structure ok")

    return (int(min_ok) + int(max_ok)) / 2, reasons
