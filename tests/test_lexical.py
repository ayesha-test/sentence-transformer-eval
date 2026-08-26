from evalkit.lexical import jaccard


def test_identical_texts_are_one():
    text = "Payments fail on iOS 17"
    assert jaccard(text, text) == 1.0


def test_unrelated_texts_are_low():
    score = jaccard(
        "Two-factor authentication codes are not arriving on mobile.",
        "The cat sat on the mat.",
    )
    assert score < 0.2


def test_empty_is_zero():
    assert jaccard("hello", "") == 0.0
