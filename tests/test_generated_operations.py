"""Tests for dynamically generating and executing calculator operations."""

import pytest
from app.calculator import Calculator

@pytest.fixture(autouse=True)
def reload_real_plugins():
    """Clear out any mocked plugins and load the real ones."""
    # Clear out any mocked plugins and load the real ones
    Calculator.COMMANDS.clear()
    Calculator.load_plugins()

def test_generated_operations():
    """Test basic arithmetic operations using Calculator.compute()."""

    # Now that we've reloaded real plugins, 'addition' etc. should be real
    result = Calculator.compute("addition", 3.0, 2.0)
    assert result == 5.0

    result = Calculator.compute("subtraction", 10.0, 4.0)
    assert result == 6.0

    result = Calculator.compute("multiplication", 2.0, 3.0)
    assert result == 6.0

    result = Calculator.compute("division", 8.0, 2.0)
    assert result == 4.0

    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        Calculator.compute("division", 10.0, 0.0)
