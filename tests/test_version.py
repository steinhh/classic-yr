"""Test version information."""

import classic_yr


def test_version() -> None:
    """Test that version is defined."""
    assert classic_yr.__version__ == "0.1.0"
    assert isinstance(classic_yr.__version__, str)
