# type: ignore
from gestura.integration.models import LogicResult


class Logic_Pause:
    def __init__(self, fake_state):
        self.state = fake_state

    def execute(self):
        result = not self.state.fake_state
        return LogicResult(
            ui_message=f"result is {result}, {'pause' if result else 'resume'}",
            payload=result
        )

class Action_Pause:
    def __init__(self, fake_state):
        self.state = fake_state

    def execute(self, payload):
        self.state.fake_state = payload