import pytest
from redactor import redact_names, load_spacy_model

# test_redact_names.py
def test_redact_names():
    nlp = load_spacy_model()
    text = "Bruce went to the save the world."
    doc = nlp(text)
    redacted_text, name_count = redact_names(doc, [])
    assert name_count == 1
    assert "Bruce" not in redacted_text
    assert "went to the save the world" in redacted_text

if __name__ == "__main__":
    pytest.main()