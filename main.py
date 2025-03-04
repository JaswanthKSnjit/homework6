import logging
import os
from dotenv import load_dotenv
from app.calculator import Calculator

# Load environment variables from .env file
load_dotenv()

# Access environment variables
app_env = os.getenv("APP_ENV")
secret_key = os.getenv("SECRET_KEY")
debug_mode = os.getenv("DEBUG")

# Ensure logs directory exists
log_dir = "logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)  # pragma: no cover  # Ignore this line in test coverage

# Configure logging to use logs/app.log
logging.basicConfig(
    level=logging.DEBUG if debug_mode == "True" else logging.INFO,  # Set log level based on DEBUG mode
    format="%(asctime)s - %(levelname)s - %(message)s",  # Define log format
    filename=os.path.join(log_dir, "app.log"),  # Store logs in logs/app.log
    filemode="a",  # Append logs instead of overwriting
)

# Log startup information
logging.info(f"Application started in {app_env} mode.")
logging.info(f"Debug mode: {debug_mode}")

def main():
    """Start the REPL calculator."""
    logging.info("Starting the calculator.")
    try:
        Calculator.run()
    except Exception as e:
        logging.error(f"An error occurred: {e}")
    logging.info("Calculator session ended.")

if __name__ == "__main__":
    main()
