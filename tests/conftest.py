"""Configuration and fixtures for pytest."""

import decimal
import pytest
from faker import Faker
from app.calculator import Calculator

fake = Faker()

@pytest.fixture(scope="session", autouse=True)
def load_plugins():
    """
    Load plugins once per session so the COMMANDS are populated.
    Remove 'autouse=True' if you prefer manual control.
    """
    Calculator.load_plugins()

def generate_test_data(num_records):
    """
    Generate test data for arithmetic operations using Calculator.compute().
    Useful if you have parametrized tests that need random numeric inputs.
    """
    operations = ["addition", "subtraction", "multiplication", "division"]
    test_cases = []

    for _ in range(num_records):
        num1 = decimal.Decimal(fake.random_int(min=-100, max=100))
        num2 = decimal.Decimal(fake.random_int(min=-100, max=100))
        operation = fake.random_element(elements=operations)

        if operation == "division" and num2 == 0:
            num2 = decimal.Decimal(1)

        try:
            result = Calculator.compute(operation, float(num1), float(num2))
            test_cases.append((num1, num2, operation, result))
        except ValueError as e:
            print(f"Skipping test case due to error: {e}")

    return test_cases

def pytest_addoption(parser):
    """Add command line options to pytest."""
    parser.addoption(
        "--num_records",
        action="store",
        default=10,
        type=int,
        help="Number of test records to generate",
    )

def pytest_generate_tests(metafunc):
    """
    Dynamically parameterize tests requiring (num1, num2, operation, expected_result).
    """
    if {"num1", "num2", "operation", "expected_result"}.issubset(set(metafunc.fixturenames)):
        num_records = metafunc.config.getoption("num_records")
        test_data = generate_test_data(num_records)
        metafunc.parametrize("num1,num2,operation,expected_result", test_data)
