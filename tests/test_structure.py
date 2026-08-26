from evalkit.structure import score_structure


def test_empty_output_scores_zero():
    score, reasons = score_structure("   ")
    assert score == 0.0
    assert "empty" in reasons[0]


def test_ok_length_scores_one():
    score, reasons = score_structure("Login failed after the password update.")
    assert score == 1.0
    assert reasons == ["structure ok"]


def test_too_short_is_partial():
    score, _ = score_structure("Hi")
    assert score == 0.5
