from app.commands.command_base import Command

class SubtractCommand(Command):
    """Command to perform subtraction."""

    def __init__(self, *args):
        self.numbers = list(map(float, args))

    def execute(self):
        result = self.numbers[0]
        for num in self.numbers[1:]:
            result -= num
        return result
