import re

_TOKEN = re.compile(r"[a-z0-9]+")


def tokenize(text: str) -> set[str]:
    return set(_TOKEN.findall(text.lower()))


def jaccard(source_text: str, output: str) -> float:
    """Unigram Jaccard overlap. A stand-in for lexical metrics such as BLEU."""
    left = tokenize(source_text)
    right = tokenize(output)
    if not left or not right:
        return 0.0
    return len(left & right) / len(left | right)
