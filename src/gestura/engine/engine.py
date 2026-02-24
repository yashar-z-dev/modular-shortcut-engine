from types import TracebackType
from typing import Callable, Any, Type

from gestura.adapters import (
    Listener, KeyboardListenerType, MouseListenerType
)

# ===== Core =====
from gestura.config import (
    ShortcutConfig,
    MouseConfig,
    KeyboardConfig
)

# ===== Default OS Adapters =====
from gestura.adapters.pynput_adapters import (
    KeyboardListener,
    MouseListener,
)

# ===== Core =====
from gestura.config.parser import parse_shortcut_config
from gestura.config.models import ShortcutConfig
from gestura.policy.engine import PolicyEngine
from gestura.engine.worker import ShortcutWorker
from gestura.models.policy import ActionEvent
from gestura.input.keyboard.handler import KeyboardApp
from gestura.input.mouse.handler import MouseApp


class GesturaEngine:
    """
    High-level orchestration facade.

    Responsibilities:
    - Parse user config
    - Wire policy engine
    - Wire worker
    - Connect OS listeners to input apps
    - Manage lifecycle of owned listeners
    """

    def __init__(
        self,
        config: list[dict[str, Any]],
        publish_action: Callable[[ActionEvent], None],

        # OS listener factories (DI entry point)
        keyboard_listener_factory: KeyboardListenerType = KeyboardListener,
        mouse_listener_factory: MouseListenerType = MouseListener
    ) -> None:

        # -------------------------------
        # Parse configuration
        # -------------------------------
        self._bundle = parse_shortcut_config(config)
        self._publish_action = publish_action

        # -------------------------------
        # Setup core components
        # -------------------------------
        # Worker
        self._worker = ShortcutWorker(
            ShortcutConfig(
                policy_engine=PolicyEngine(self._bundle.policies),
                publish_action=self._publish_action,
                worker_map=self._bundle.worker_map,
                combined_window_seconds=4.0)
        )

        # Keyboard
        self._keyboard_app = KeyboardApp(
            KeyboardConfig(
                gestures=self._bundle.keyboard_gestures,
                on_trigger=self._worker.submit_keyboard_triggers,
                BufferWindowSeconds=1.5)
        )

        # Mouse
        self._mouse_app = MouseApp(
            MouseConfig(
                gestures=self._bundle.mouse_gestures,
                on_trigger=self._worker.submit_mouse_triggers,
                BufferWindowSeconds=4.0,
                min_delta=8.0)
        )

        # -------------------------------
        # Create OS listeners (engine owns them)
        # -------------------------------
        self._keyboard_listener: Listener = keyboard_listener_factory(
            on_event=self._keyboard_app.HandleEvens
        )

        self._mouse_listener: Listener = mouse_listener_factory(
            on_event=self._mouse_app.HandleEvens
        )

        self._running = False

    # ---------------------------------------------------------
    # Lifecycle
    # ---------------------------------------------------------

    def start(self) -> None:
        if self._running:
            return

        self._worker.start()
        self._keyboard_listener.start()
        self._mouse_listener.start()

        self._running = True

    def stop(self) -> None:
        if not self._running:
            return

        self._keyboard_listener.stop()
        self._mouse_listener.stop()
        self._worker.stop()

        self._running = False

    # ---------------------------------------------------------
    # Context Manager Support
    # ---------------------------------------------------------

    def __enter__(self):
        self.start()
        return self

    def __exit__(
        self,
        exc_type: Type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None
    ) -> None:
        self.stop()