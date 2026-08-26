from evalkit.coverage import extract_critical_terms, score_coverage


def test_extracts_platform_version_and_phrases():
    source = (
        "Customer cannot log in on Android version 14 after the latest update. "
        "Password reset emails are delayed. No workaround available."
    )
    terms = {term.lower() for term in extract_critical_terms(source)}
    assert "android 14" in terms
    assert "password reset" in terms
    assert "no workaround" in terms
    assert "delayed" in terms


def test_missing_terms_fail_coverage():
    source = "The dashboard is slow when importing a CSV of invoices."
    output = "Export still works."
    score, reasons, missing = score_coverage(source, output)
    assert score < 1.0
    assert missing
    assert "missing critical terms" in reasons[0]


def test_all_terms_present():
    source = "Payments fail on iOS 17. Token refresh returns invalid token."
    output = "Payments fail on iOS 17 because of an invalid token."
    score, reasons, missing = score_coverage(source, output)
    assert missing == []
    assert score == 1.0
    assert reasons[0].startswith("all ")
