from pathlib import Path
import json
import logging
import time

# API
from gestura import GesturaEngine

# Integration
from gestura.integration.action_bus import ActionBus
from gestura.integration.action_dispatcher import ActionDispatcher

# Action definition
from .exit import Logic_Exit, Action_Exit
from .pause import Logic_Pause, Action_Pause


class AppState:
    def __init__(self):
        self.fake_state = True

class main:
    def __init__(self):
        self.running = False
        self.fake_state = AppState()

        self._ActionBus = ActionBus()
        self._setup_engine()
        self._setup_shortcut_map()
        self.register_callbacks()

    def app_state(self, state: bool):
        self.running = state

    def _setup_engine(self):
        BASE_DIR = Path(__file__).resolve().parent
        json_path = BASE_DIR / "sample_config.json"

        with open(json_path, "r", encoding="utf-8") as f:
            config = json.load(f)

        self._GesturaEngine = GesturaEngine(config, self._ActionBus.publish)

    def _setup_shortcut_map(self):
        self._ActionDispatcher = ActionDispatcher(self._setup_deps(), lambda _: None)

    def _setup_deps(self) -> dict[str, object]:
        return {
            "fake_state": self.fake_state,
            "app_state": self.app_state,
            "_GesturaEngine": self._GesturaEngine,
            "_ActionBus": self._ActionBus,
            }

    def register_callbacks(self):
        self._ActionDispatcher.register("exit", Logic_Exit, Action_Exit)
        self._ActionDispatcher.register("pause", Logic_Pause, Action_Pause)

    def pump_worker_events(self):
        for cb_key in self._ActionBus.drain():
            self._ActionDispatcher.execute_callback(cb_key)

    def _loop(self):
        while self.running:
            self.pump_worker_events()

            time.sleep(0.01)

    def start(self):
        logging.info("Engine is Started...")
        self.app_state(True)
        self._GesturaEngine.start()
        self._loop()

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    _main = main()
    _main.start()
