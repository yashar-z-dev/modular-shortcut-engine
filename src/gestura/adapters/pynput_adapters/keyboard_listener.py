from typing import Callable, Optional, Any

import pynput
from ...models.inputs import KeyboardEvent


class KeyboardListener:
    """
    Keyboard listener using pynput that hooks all key press/release events
    and forwards them to the provided callback.

    The callback should handle event IDs, parsing, or gesture logic.
    """

    def __init__(self, on_event: Callable[[KeyboardEvent], None]) -> None:
        """
        Initialize the keyboard handler.

        Args:
            on_event: Function to call for each key event.

        return: (key: str, press: bool)
        """
        self.on_event = on_event
        self._listener: Optional[pynput.keyboard.Listener] = None

    # ---------------- Internal Event Callback ---------------- #
    def _on_press(self, key: Any) -> None:
        """
        Internal handler for key press events.
        """
        key_str = self._normalize_key(key)
        self.on_event(KeyboardEvent(key=key_str, press=True))

    def _on_release(self, key: Any) -> None:
        """
        Internal handler for key release events.
        """
        key_str = self._normalize_key(key)
        self.on_event(KeyboardEvent(key=key_str, press=False))

    def _normalize_key(self, key: Any) -> str:
        """
        Convert external key object to normalized string.
        Boundary adaptation only.
        """
        if hasattr(key, "char") and key.char:
            return key.char

        return str(key).replace("Key.", "")

    # ---------------- Start Listening ---------------- #
    def start(self) -> None:
        """
        Start listening to all keyboard events.
        """
        if self._listener is None:
            self._listener = pynput.keyboard.Listener(
                on_press=self._on_press,
                on_release=self._on_release
            )
            self._listener.start()

    # ---------------- Stop Listening ---------------- #
    def stop(self) -> None:
        """
        Stop listening to keyboard events.
        """
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
