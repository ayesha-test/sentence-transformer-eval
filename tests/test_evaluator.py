from evalkit.evaluator import evaluate_all, evaluate_output


def test_missing_facts_hard_fail(monkeypatch):
    monkeypatch.setattr(
        "evalkit.evaluator.score_similarity",
        lambda source, output: (0.9, ["semantic similarity 0.900"]),
    )
    result = evaluate_output(
        {
            "id": "missing",
            "source_text": "The dashboard is slow when importing a CSV of invoices.",
            "generated_output": "Export still works for invoices.",
        }
    )
    assert result["passed"] is False
    assert result["missing_terms"]
    assert any("hard gate" in reason for reason in result["reasons"])


def test_empty_output_fails(monkeypatch):
    monkeypatch.setattr(
        "evalkit.evaluator.score_similarity",
        lambda source, output: (0.0, ["semantic similarity 0.000"]),
    )
    result = evaluate_output(
        {
            "id": "empty",
            "source_text": "Crash on login after password update.",
            "generated_output": "",
        }
    )
    assert result["passed"] is False
    assert result["structure_score"] == 0.0


def test_evaluate_all_pass_rate(monkeypatch):
    monkeypatch.setattr(
        "evalkit.evaluator.score_similarity",
        lambda source, output: (0.95, ["semantic similarity 0.950"]),
    )
    report = evaluate_all(
        [
            {
                "id": "ok",
                "source_text": "Payments fail on iOS 17. Token refresh returns invalid token.",
                "generated_output": "Payments fail on iOS 17 because of an invalid token.",
            }
        ]
    )
    assert report["summary"]["total"] == 1
    assert report["summary"]["passed"] == 1
    assert report["results"][0]["id"] == "ok"
