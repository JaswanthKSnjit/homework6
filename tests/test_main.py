import pytest
import main
import subprocess
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
        # Match the real code's checks exactly:
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
    result = subprocess.run(["python", "main.py"], input="exit\n", text=True, capture_output=True)
    # Verify that the welcome, prompt, and exit messages appear, and that the script exits cleanly.
    assert "Welcome to the Plugin-Based Calculator!" in result.stdout
    assert "Type 'menu' to view options or 'exit' to quit." in result.stdout
    assert "Goodbye!" in result.stdout
    assert result.returncode == 0
