"""Sample tests."""

from core import calc


class TestsCalcFunctions:
    """Test functions from calc module."""

    def test_add_numbers(self):
        """Test adding numbers together."""

        result = calc.add(5, 6)
        assert result == 11

    def test_subtract_numbers(self):
        """Test subtracting numbers."""

        result = calc.subtract(10, 2)
        assert result == 8
