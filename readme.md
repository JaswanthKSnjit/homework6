# Assignment 6 Log and Environment

-- This is an improved version of the Plugin-Based Calculator with **Logging Support** and **Environment Variables**.<br>
## Feautres Added
1. **Environment Variables:** Uses `.env` file to manage configurations such as environment mode, secrets, and debug mode.
2. **Logging System:** Logs all application activities to `logs/app.log` for better debugging and monitoring.
3. **GitHub Actions Integration:** Automates running tests on every push, ensuring that the code is tested continuously.
4. **Improved Debugging:** Debug mode can be enabled via `.env` settings to capture additional logs and errors.

## Setup Instructions

1. Clone Repo: <code> git clone git@github.com:JaswanthKSnjit/homework6.git </code>
2. Navigate to project directory <code> cd basic_calculator </code>
3. Create a Python Virtual Environments <code> python -m venv venv </code>
4. Activate Python Virtual Environments <code> source venv/bin/activate </code>
5. Install dependencies <code> pip install -r requirements.txt </code>
6. Set up Environment Variables<br>
-- Create a .env file in root directory and add the following<br>
<code>APP_ENV=development<br>
SECRET_KEY=mysecretkey<br>
DEBUG=True </code>
7. To run the program <code> python main.py </code>
8. Logs are stored in <code>logs/</code> folder.
9. Running basic tests <code> pytest tests</code>
10. Faker generated random tests <code> pytest tests --num_records=100 </code>
11. For full debug output <code> pytest tests --num_records=10 -v -s </code>

**NOTE:** If you face any difficulties please contact me at <code> jk795@njit.edu </code>
