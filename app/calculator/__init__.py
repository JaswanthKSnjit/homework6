import os
import importlib.util
from multiprocessing import Process, Queue
from app.commands.command_base import Command

class Calculator:
    """Handles execution of arithmetic operations using modular plugins."""
    
    COMMANDS = {}

    @staticmethod
    def load_plugins():
        """Dynamically loads all command plugins from the app/plugins/ directory."""
        plugins_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "plugins"))

        if not os.path.exists(plugins_path):  # Ensure plugin directory exists
            Calculator.COMMANDS.clear()  # Fix: Clear COMMANDS if plugins directory is missing
            print("Plugin directory not found.")
            return  

        for foldername in os.listdir(plugins_path):
            plugin_folder = os.path.join(plugins_path, foldername)
            init_file = os.path.join(plugin_folder, "__init__.py")

            if os.path.isdir(plugin_folder) and os.path.exists(init_file):
                module_name = f"app.plugins.{foldername}"  
                try:
                    spec = importlib.util.spec_from_file_location(module_name, init_file)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    for attr_name in dir(module):
                        attr = getattr(module, attr_name)
                        if isinstance(attr, type) and issubclass(attr, Command) and attr is not Command:
                            Calculator.COMMANDS[foldername] = attr
                except Exception as e:
                    print(f"Failed to load plugin {foldername}: {e}")  
                    if foldername in Calculator.COMMANDS:  # Fix: Ensure failed plugins are not retained
                        del Calculator.COMMANDS[foldername]  

    @staticmethod
    def compute(operation, *args):
        """Executes a dynamically loaded command using multiprocessing."""
        if not args:
            raise TypeError("compute() missing required positional arguments: 'operation' and 'args'")

        if operation not in Calculator.COMMANDS:
            raise ValueError(f"Unsupported operation: {operation}")

        def worker(q, operation, args):
            try:
                command = Calculator.COMMANDS[operation](*args)
                q.put(command.execute())
            except Exception as e:
                q.put(e)

        q = Queue()
        p = Process(target=worker, args=(q, operation, args))
        p.start()
        p.join()

        result = q.get()
        if isinstance(result, Exception):  # Handling edge case
            raise result

        return float(result)

    @staticmethod
    def show_menu():
        """Displays available commands without reloading plugins."""
        print("\nAvailable Commands:")
        for command in Calculator.COMMANDS.keys():
            if command != "exit":  
                print(f"- {command} <num1> <num2> (e.g., {command} 5 5)")
        print("- exit (Exit the calculator)")

    @staticmethod
    def run():
        """Interactive REPL for the calculator."""
        Calculator.load_plugins()  # Ensure plugins are loaded before execution

        print("\nWelcome to the Plugin-Based Calculator!")
        print("Type 'menu' to view options or 'exit' to quit.")

        while True:
            try:
                user_input = input(">>> ").strip().lower()

                if user_input == "exit":
                    print("Goodbye!")
                    break
                elif user_input == "menu":
                    Calculator.show_menu()
                else:
                    parts = user_input.split()
                    if len(parts) >= 2 and parts[0] in Calculator.COMMANDS:
                        try:
                            numbers = list(map(float, parts[1:]))
                            result = Calculator.compute(parts[0], *numbers)
                            print(f"Result: {result:.1f}")  
                        except ValueError:
                            print("Invalid input. Please enter numeric values.")
                        except ZeroDivisionError as e:
                            print(f"Error: {e}")
                    else:
                        print("Invalid command. Type 'menu' to see available commands.")
            except Exception as e:  
                print(f"Unexpected error: {e}")  
