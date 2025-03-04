from dotenv import load_dotenv
import os
from app.calculator import Calculator

# Load environment variables from .env file
load_dotenv()

# Access environment variables
app_env = os.getenv("APP_ENV")
secret_key = os.getenv("SECRET_KEY")
debug_mode = os.getenv("DEBUG")

# Print environment information
print(f"Running in {app_env} mode")
print(f"Debug mode: {debug_mode}")

def main():
    """Start the REPL calculator."""
    Calculator.run()

if __name__ == "__main__":
    main()
