import pytest
from redactor import redact_names, load_spacy_model

# test_redact_names.py
def test_redact_names():
    nlp = load_spacy_model()
    text = "John Doe went to the market."
    doc = nlp(text)
    redacted_text, name_count = redact_names(doc, [])
    assert name_count == 1
    assert "John Doe" not in redacted_text
    assert "went to the market" in redacted_text

if __name__ == "__main__":
    pytest.main()