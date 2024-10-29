import pytest
from redactor import redact_phone_numbers

def test_redact_phone_numbers():
    # Original text line with phone numbers
    text = "For those looking to get in touch with Bruce, you can reach him via email at bruce.wayne@Chicagocity.org or by calling him directly at 555-123-4567."
    redacted_text, count = redact_phone_numbers(text)
    assert count == 1
    assert "555-123-4567" not in redacted_text
    assert "by calling him directly at" in redacted_text

if __name__ == "__main__":
    pytest.main()
