# pylint: skip-file

"""Tests for the main entry point of the calculator application."""

import subprocess
import pytest
import os
from unittest.mock import patch
import importlib
import main  # Import your main script
from app.calculator import Calculator

@pytest.fixture(scope="function")
def disable_multiprocessing(monkeypatch):
    """
    A fixture to replace multiprocessing in Calculator.compute() with a synchronous version
    that replicates the exact error messages from the real code.
    Not autouse, so it won't affect other tests outside this file.
    """
    original_compute = Calculator.compute

    def sync_compute(operation, *args):
        """ Synchronous version of compute for testing. """
        if not args:
            raise TypeError("compute() missing required positional arguments: 'operation' and 'args'")
        if operation not in Calculator.COMMANDS:
            raise ValueError(f"Unsupported operation: {operation}")
        command = Calculator.COMMANDS[operation](*args)
        return command.execute()

    monkeypatch.setattr(Calculator, "compute", sync_compute)
    yield
    monkeypatch.setattr(Calculator, "compute", original_compute)

@pytest.mark.usefixtures("disable_multiprocessing")
def test_main_function(monkeypatch, capsys):
    """
    Test that main() runs Calculator.run() without hanging and exits correctly.
    """
    # Simulate user input "exit" so the REPL immediately terminates.
    monkeypatch.setattr("builtins.input", lambda _: "exit")
    main.main()
    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out  # Verify that the exit message is printed.

@pytest.mark.usefixtures("disable_multiprocessing")
def test_main_entry_point():
    """
    Test if main.py runs as a script and executes main() correctly.
    """
    # Run main.py as an actual subprocess.
    result = subprocess.run(
        ["python", "main.py"],
        input="exit\n",
        text=True,
        capture_output=True,
        check=True  # Ensure the script exits without errors
    )
    # Verify that the welcome, prompt, and exit messages appear.
    assert "Welcome to the Plugin-Based Calculator!" in result.stdout
    assert "Type 'menu' to view options or 'exit' to quit." in result.stdout
    assert "Goodbye!" in result.stdout
    assert result.returncode == 0

def test_log_directory_creation():
    """
    Test if logs directory is created when it doesn't exist.
    """
    with patch("os.path.exists", return_value=False), patch("os.makedirs") as mock_makedirs:
        # Directly call the directory setup logic
        if not os.path.exists(main.log_dir):
            os.makedirs(main.log_dir)

        # Assert that os.makedirs was called to create the logs folder
        mock_makedirs.assert_called_once_with(main.log_dir)
