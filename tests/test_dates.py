import pytest
from redactor import redact_dates

def test_redact_dates():
    # Original text line with dates
    text = "Bruce Wayne is set to give an inspiring speech on Tuesday, 11/01/2024."
    redacted_text, count = redact_dates(text)
    assert count == 1
    assert "11/01/2024" not in redacted_text

if __name__ == "__main__":
    pytest.main()
