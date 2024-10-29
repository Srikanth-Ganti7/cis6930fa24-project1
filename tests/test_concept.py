import pytest
from redactor import redact_concept_sentences

def test_redact_concept_sentences():
    # Original text line with the concept "house" to test sentence redaction
    text = "BatTech is always at the forefront of crime prevention through technology, education, and community development."
    concepts = ["technology"]  # Choosing a concept word relevant to BatTech's purpose
    redacted_text, count = redact_concept_sentences(text, concepts)
    assert count == 1
    assert "BatTech is always at the forefront of crime prevention through technology, education, and community development." not in redacted_text

if __name__ == "__main__":
    pytest.main()
