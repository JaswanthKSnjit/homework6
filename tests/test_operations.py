# pylint: skip-file
"""Tests for individual calculator operation plugins."""

import pytest
from app.plugins.addition import AddCommand
from app.plugins.subtraction import SubtractCommand
from app.plugins.multiplication import MultiplyCommand
from app.plugins.division import DivideCommand
from app.plugins.exit import ExitCommand
from app.commands.command_base import Command

@pytest.mark.parametrize("x, y, expected", [(3, 2, 5), (-1, -1, -2), (0, 0, 0)])
def test_add(x, y, expected):
    """Test addition operation."""
    command = AddCommand(x, y)
    assert command.execute() == expected

@pytest.mark.parametrize("x, y, expected", [(5, 2, 3), (0, -1, 1), (-3, -3, 0)])
def test_subtract(x, y, expected):
    """Test subtraction operation."""
    command = SubtractCommand(x, y)
    assert command.execute() == expected

@pytest.mark.parametrize("x, y, expected", [(3, 3, 9), (-1, 4, -4), (0, 100, 0)])
def test_multiply(x, y, expected):
    """Test multiplication operation."""
    command = MultiplyCommand(x, y)
    assert command.execute() == expected

@pytest.mark.parametrize("x, y, expected", [(6, 2, 3), (-10, 5, -2), (8, 4, 2)])
def test_divide(x, y, expected):
    """Test division operation."""
    command = DivideCommand(x, y)
    assert command.execute() == expected

def test_divide_by_zero():
    """Test division by zero raises ZeroDivisionError."""
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        DivideCommand(5, 0).execute()

def test_exit_command():
    """Test exit command to ensure it raises SystemExit."""
    with pytest.raises(SystemExit) as exit_exception:
        ExitCommand().execute()
    assert exit_exception.value.code == 0  # Ensure exit code is 0 (successful termination)

def test_command_base_cannot_instantiate():
    """Test that abstract Command class cannot be instantiated."""
    with pytest.raises(TypeError):
        Command()  # This is technically creating an instance, but the test expects an error

class TestCommand(Command):
    """A test subclass of Command to ensure execute() is properly tested."""
    def execute(self):
        super().execute()  # Explicitly call parent method for coverage
        return "Test Execution"

def test_command_execution():
    """Ensure abstract method execute() is implemented and called."""
    command = TestCommand()
    assert command.execute() == "Test Execution"
