from lib.actions.action import Action

class WaitUntilAction(Action):
    def __init__(self, condition):
        super().__init__("WaitUntilCommand")
        self.condition = condition

    def initialize(self):
        pass

    def execute(self):
        pass

    def end(self, interrupted: bool):
        pass

    def is_finished(self) -> bool:
        return self.condition()