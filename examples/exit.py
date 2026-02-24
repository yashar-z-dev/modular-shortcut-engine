# type: ignore
import logging
from gestura.integration.models import LogicResult


class Logic_Exit:
    def __init__(self):
        pass

    def execute(self) -> LogicResult:
        return LogicResult(ui_message="exit with ui toggle.", payload="exit")


class Action_Exit:
    def __init__(
        self,
        _GesturaEngine,
        app_state):

        self._GesturaEngine = _GesturaEngine
        self.app_state = app_state

    def execute(self, payload) -> None:
        logging.info("Engine is EXIT.")

        self._GesturaEngine.stop()
        self.app_state(False)