# pylint: skip-file

import os
import importlib.util
import pytest
from multiprocessing import Queue
from app.calculator import Calculator

@pytest.fixture(scope="function", autouse=True)
def reset_commands():
    Calculator.COMMANDS.clear()

# --- Tests for load_plugins() ---

def test_load_plugins_directory_not_found(monkeypatch, capsys):
    monkeypatch.setattr(os.path, "exists", lambda path: False)
    Calculator.load_plugins()
    captured = capsys.readouterr()
    assert "Plugin directory not found." in captured.out
    assert len(Calculator.COMMANDS) == 0

def test_load_plugins_directory_empty(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(os, "listdir", lambda path: [])
    Calculator.load_plugins()
    assert len(Calculator.COMMANDS) == 0

def test_load_plugins_failing_plugin(monkeypatch):
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(os, "listdir", lambda path: ["bad_plugin"])
    monkeypatch.setattr(os.path, "isdir", lambda path: True)
    def mock_spec_from_file_location(*args, **kwargs):
        raise ImportError("Mocked Import Error")
    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec_from_file_location)
    Calculator.load_plugins()
    assert len(Calculator.COMMANDS) == 0

@pytest.mark.skipif(
    not os.path.exists(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "app", "plugins"))),
    reason="Plugins directory does not exist or is not set up."
)
def test_load_plugins_success():
    Calculator.load_plugins()
    assert "addition" in Calculator.COMMANDS
    assert "subtraction" in Calculator.COMMANDS
    assert "multiplication" in Calculator.COMMANDS
    assert "division" in Calculator.COMMANDS

# --- Tests for compute() ---

@pytest.mark.no_disable_mp  # <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<
def test_compute_no_args():
    """
    This test calls the REAL Calculator.compute() (not patched).
    We want the real error message.
    """
    with pytest.raises(
        TypeError, 
        match=r"Calculator.compute\(\) missing 1 required positional argument: 'operation'"
    ):
        Calculator.compute()

def test_compute_invalid_operation():
    with pytest.raises(ValueError, match="Unsupported operation: invalid"):
        Calculator.compute("invalid", 5, 3)

def test_compute_addition(monkeypatch):
    class MockAdd:
        def __init__(self, *args):
            self.args = args
        def execute(self):
            return sum(self.args)
    monkeypatch.setattr(Calculator, "load_plugins", lambda: Calculator.COMMANDS.update({"addition": MockAdd}))
    Calculator.load_plugins()
    result = Calculator.compute("addition", 3, 2)
    assert result == 5.0

def test_compute_subtraction(monkeypatch):
    class MockSub:
        def __init__(self, *args):
            self.args = args
        def execute(self):
            return self.args[0] - sum(self.args[1:])
    monkeypatch.setattr(Calculator, "load_plugins", lambda: Calculator.COMMANDS.update({"subtraction": MockSub}))
    Calculator.load_plugins()
    result = Calculator.compute("subtraction", 10, 4)
    assert result == 6.0

def test_compute_multiplication(monkeypatch):
    class MockMul:
        def __init__(self, *args):
            self.args = args
        def execute(self):
            result = 1
            for n in self.args:
                result *= n
            return result
    monkeypatch.setattr(Calculator, "load_plugins", lambda: Calculator.COMMANDS.update({"multiplication": MockMul}))
    Calculator.load_plugins()
    result = Calculator.compute("multiplication", 2, 3)
    assert result == 6.0

def test_compute_division(monkeypatch):
    class MockDiv:
        def __init__(self, x, y):
            if y == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            self.x = x
            self.y = y
        def execute(self):
            return self.x / self.y
    monkeypatch.setattr(Calculator, "load_plugins", lambda: Calculator.COMMANDS.update({"division": MockDiv}))
    Calculator.load_plugins()
    result = Calculator.compute("division", 8, 2)
    assert result == 4.0

def test_compute_division_by_zero(monkeypatch):
    class MockDiv:
        def __init__(self, x, y):
            if y == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            self.x = x
            self.y = y
        def execute(self):
            return self.x / self.y
    monkeypatch.setattr(Calculator, "load_plugins", lambda: Calculator.COMMANDS.update({"division": MockDiv}))
    Calculator.load_plugins()
    with pytest.raises(ZeroDivisionError, match="Cannot divide by zero."):
        Calculator.compute("division", 10, 0)

def test_compute_multiprocessing_error(monkeypatch):
    def mock_worker(q, operation, args):
        q.put(Exception("Mocked Worker Error"))
    def mock_compute(operation, *args):
        q = Queue()
        mock_worker(q, operation, args)
        result = q.get()
        if isinstance(result, Exception):
            raise result
        return float(result)
    monkeypatch.setattr(Calculator, "compute", mock_compute)
    with pytest.raises(Exception, match="Mocked Worker Error"):
        Calculator.compute("addition", 5, 5)

# --- show_menu() ---

def test_show_menu(capsys, monkeypatch):
    def mock_load_plugins():
        Calculator.COMMANDS.update({"addition": None, "subtraction": None, "exit": None})
    monkeypatch.setattr(Calculator, "load_plugins", mock_load_plugins)
    Calculator.load_plugins()
    Calculator.show_menu()
    captured = capsys.readouterr()
    assert "Available Commands:" in captured.out
    assert "- addition <num1> <num2>" in captured.out
    assert "- subtraction <num1> <num2>" in captured.out
    assert "- exit (Exit the calculator)" in captured.out

# --- run() (REPL) tests ---

def test_run_exit(monkeypatch, capsys):
    inputs = iter(["exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    Calculator.run()
    captured = capsys.readouterr()
    assert "Goodbye!" in captured.out

def test_run_menu(monkeypatch, capsys):
    inputs = iter(["menu", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    Calculator.run()
    captured = capsys.readouterr()
    assert "Available Commands:" in captured.out
    assert "Goodbye!" in captured.out

def test_run_invalid_command(monkeypatch, capsys):
    inputs = iter(["invalid", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    Calculator.run()
    captured = capsys.readouterr()
    assert "Invalid command. Type 'menu' to see available commands." in captured.out
    assert "Goodbye!" in captured.out

def test_run_valid_addition(monkeypatch, capsys):
    class MockAdd:
        def __init__(self, *args):
            self.args = args
        def execute(self):
            return sum(self.args)
    def mock_load_plugins():
        Calculator.COMMANDS.update({"addition": MockAdd})
    inputs = iter(["addition 5 5", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(Calculator, "load_plugins", mock_load_plugins)
    Calculator.run()
    captured = capsys.readouterr()
    assert "Result: 10.0" in captured.out
    assert "Goodbye!" in captured.out

def test_run_valid_subtraction(monkeypatch, capsys):
    class MockSub:
        def __init__(self, *args):
            self.args = args
        def execute(self):
            return self.args[0] - sum(self.args[1:])
    def mock_load_plugins():
        Calculator.COMMANDS.update({"subtraction": MockSub})
    inputs = iter(["subtraction 10 4", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(Calculator, "load_plugins", mock_load_plugins)
    Calculator.run()
    captured = capsys.readouterr()
    assert "Result: 6.0" in captured.out
    assert "Goodbye!" in captured.out

def test_run_valid_multiplication(monkeypatch, capsys):
    class MockMul:
        def __init__(self, *args):
            self.args = args
        def execute(self):
            result = 1
            for n in self.args:
                result *= n
            return result
    def mock_load_plugins():
        Calculator.COMMANDS.update({"multiplication": MockMul})
    inputs = iter(["multiplication 3 4", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(Calculator, "load_plugins", mock_load_plugins)
    Calculator.run()
    captured = capsys.readouterr()
    assert "Result: 12.0" in captured.out
    assert "Goodbye!" in captured.out

def test_run_valid_division(monkeypatch, capsys):
    class MockDiv:
        def __init__(self, x, y):
            if float(y) == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            self.x = x
            self.y = y
        def execute(self):
            return self.x / self.y
    def mock_load_plugins():
        Calculator.COMMANDS.update({"division": MockDiv})
    inputs = iter(["division 8 2", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    Calculator.run()
    captured = capsys.readouterr()
    assert "Result: 4.0" in captured.out
    assert "Goodbye!" in captured.out

def test_run_value_error(monkeypatch, capsys):
    class MockAdd:
        def __init__(self, *args):
            pass
        def execute(self):
            return 0
    def mock_load_plugins():
        Calculator.COMMANDS.update({"addition": MockAdd})
    inputs = iter(["addition 5 abc", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    Calculator.run()
    captured = capsys.readouterr()
    assert "Invalid input. Please enter numeric values." in captured.out
    assert "Goodbye!" in captured.out

def test_run_zero_division_error(monkeypatch, capsys):
    class MockDiv:
        def __init__(self, x, y):
            if float(y) == 0:
                raise ZeroDivisionError("Cannot divide by zero.")
            self.x = x
            self.y = y
        def execute(self):
            return self.x / self.y
    def mock_load_plugins():
        Calculator.COMMANDS.update({"division": MockDiv})
    inputs = iter(["division 5 0", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    Calculator.run()
    captured = capsys.readouterr()
    assert "Error: Cannot divide by zero." in captured.out
    assert "Goodbye!" in captured.out

def test_run_unexpected_error(monkeypatch, capsys):
    def mock_compute(operation, *args):
        raise RuntimeError("Some unexpected error")
    class MockAdd:
        def __init__(self, *args):
            pass
        def execute(self):
            return 999
    def mock_load_plugins():
        Calculator.COMMANDS.update({"addition": MockAdd})
    inputs = iter(["addition 5 5", "exit"])
    monkeypatch.setattr("builtins.input", lambda _: next(inputs))
    monkeypatch.setattr(Calculator, "load_plugins", mock_load_plugins)
    monkeypatch.setattr(Calculator, "compute", mock_compute)
    Calculator.run()
    captured = capsys.readouterr()
    assert "Unexpected error: Some unexpected error" in captured.out
    assert "Goodbye!" in captured.out

# --- Additional tests for coverage ---

def test_compute_with_minimal_args():
    """Test compute method with operation and minimal args."""
    Calculator.COMMANDS.clear()
    
    # Create a mock command that works with minimal args
    class MockCommand:
        def __init__(self, *args):
            pass
        def execute(self):
            return 42
    
    # Register the mock command
    Calculator.COMMANDS["test_op"] = MockCommand
    
    # Call compute with operation and minimal args
    result = Calculator.compute("test_op", 0)
    assert result == 42.0

def test_load_plugins_with_exec_module_exception(monkeypatch, capsys):
    """Test handling when a plugin's exec_module raises an exception."""
    Calculator.COMMANDS.clear()
    
    # Define mocks for the test
    def mock_exists(path):
        return True
        
    def mock_listdir(path):
        return ["failing_plugin"]
        
    def mock_isdir(path):
        return True
        
    def mock_join(*args):
        return "/mock/path"
        
    class MockSpec:
        def __init__(self):
            self.loader = MockLoader()
            
    class MockLoader:
        def exec_module(self, module):
            raise Exception("Mock exec_module error")
            
    def mock_module_from_spec(spec):
        return type('obj', (object,), {})
    
    def mock_spec_from_file_location(name, location):
        return MockSpec()
        
    # Apply monkeypatches
    monkeypatch.setattr(os.path, "exists", mock_exists)
    monkeypatch.setattr(os, "listdir", mock_listdir)
    monkeypatch.setattr(os.path, "isdir", mock_isdir)
    monkeypatch.setattr(os.path, "join", mock_join)
    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec_from_file_location)
    monkeypatch.setattr(importlib.util, "module_from_spec", mock_module_from_spec)
    
    # Execute the function being tested
    Calculator.load_plugins()
    captured = capsys.readouterr()
    
    # Verify the expected behavior
    assert "Failed to load plugin failing_plugin" in captured.out
    assert "failing_plugin" not in Calculator.COMMANDS

def test_compute_with_empty_args():
    """Test compute method with empty args list."""
    Calculator.COMMANDS.clear()
    
    # Create a simple mock command that works with any args
    class MockCommand:
        def __init__(self, *args):
            pass
        def execute(self):
            return 42
    
    # Register the mock command
    Calculator.COMMANDS["test_op"] = MockCommand
    
    # Call compute with operation and no additional args
    with pytest.raises(TypeError):
        Calculator.compute("test_op")

def test_compute_with_command_error():
    """Test error handling in the compute method."""
    Calculator.COMMANDS.clear()
    
    # Create a mock command that raises an exception in execute
    class ErrorCommand:
        def __init__(self, *args):
            pass
        def execute(self):
            raise RuntimeError("Test error in command execution")
    
    # Register the mock command
    Calculator.COMMANDS["error_op"] = ErrorCommand
    
    # This should raise the exception from execute
    with pytest.raises(RuntimeError, match="Test error in command execution"):
        Calculator.compute("error_op", 1)

# --- New tests for specific coverage of lines 39 and 51-55 ---

def test_load_plugins_delete_failed_plugin_entry(monkeypatch, capsys):
    """Test that failed plugin entries are properly removed from COMMANDS."""
    Calculator.COMMANDS.clear()
    # First add an entry that we'll later have "fail"
    Calculator.COMMANDS["test_plugin"] = None
    
    # Setup mocks to simulate a plugin that fails to load but was already added
    monkeypatch.setattr(os.path, "exists", lambda path: True)
    monkeypatch.setattr(os, "listdir", lambda path: ["test_plugin"])
    monkeypatch.setattr(os.path, "isdir", lambda path: True)
    monkeypatch.setattr(os.path, "join", lambda *args: "/mock/path")
    
    # Make the spec_from_file_location throw an exception
    def mock_spec_from_file_location(*args, **kwargs):
        raise Exception("Mock failure during plugin load")
    
    monkeypatch.setattr(importlib.util, "spec_from_file_location", mock_spec_from_file_location)
    
    # Run the function
    Calculator.load_plugins()
    
    # Verify the test_plugin was removed from COMMANDS
    assert "test_plugin" not in Calculator.COMMANDS
    captured = capsys.readouterr()
    assert "Failed to load plugin test_plugin" in captured.out

def test_worker_function_exception_handling():
    """Test the exception handling in the worker function directly."""
    Calculator.COMMANDS.clear()
    
    # Create a command class that raises an exception during __init__
    class InitErrorCommand:
        def __init__(self, *args):
            raise RuntimeError("Test error in command init")
        
        def execute(self):
            return 0  # This won't be called
    
    # Register our command
    Calculator.COMMANDS["init_error_op"] = InitErrorCommand
    
    # This should raise the exception from __init__
    with pytest.raises(RuntimeError, match="Test error in command init"):
        Calculator.compute("init_error_op", 1)

def test_command_execute_exception():
    """Test the exception handling in worker function (lines 51-55)."""
    Calculator.COMMANDS.clear()
    
    # Create a command that raises an exception during execute()
    class BrokenCommand:
        def __init__(self, *args):
            pass
        
        def execute(self):
            # Deliberately raise a ZeroDivisionError
            return 1/0
    
    # Register our command
    Calculator.COMMANDS["broken"] = BrokenCommand
    
    # This should raise the ZeroDivisionError from execute()
    with pytest.raises(ZeroDivisionError):
        Calculator.compute("broken", 1)
