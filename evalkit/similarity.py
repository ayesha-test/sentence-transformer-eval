from evalkit.config import SIMILARITY_MODEL

_model = None


def _get_model():
    global _model
    if _model is None:
        from sentence_transformers import SentenceTransformer

        _model = SentenceTransformer(SIMILARITY_MODEL)
    return _model


def score_similarity(source_text: str, output: str) -> tuple[float, list[str]]:
    """Layer 3: cosine similarity between source and output embeddings."""
    if not source_text.strip() or not output.strip():
        return 0.0, ["semantic similarity 0.000 (empty input)"]

    from sentence_transformers.util import cos_sim

    model = _get_model()
    embeddings = model.encode([source_text, output], convert_to_tensor=True)
    similarity = float(cos_sim(embeddings[0], embeddings[1]).item())
    similarity = max(0.0, min(1.0, similarity))
    return similarity, [f"semantic similarity {similarity:.3f}"]
