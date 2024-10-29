import pytest
from redactor import redact_addresses

def test_redact_addresses():
    # Original text line with an address
    text = "In case you wish to visit BatTech' headquarters or drop by to discuss community initiatives, the office is located at 8251 Steven Lane 50884."
    redacted_text, count = redact_addresses(text)
    assert count == 1
    assert "8251 Steven Lane 50884" not in redacted_text
    assert "the office is located at" in redacted_text

if __name__ == "__main__":
    pytest.main()
