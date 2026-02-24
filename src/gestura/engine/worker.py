from typing import Callable, Dict
import logging, threading, queue

from ..config import ShortcutConfig
from ..models.policy import TriggerEvent, ActionEvent


class ShortcutWorker:
    """
    Event-driven shortcut coordinator.
    Handles keyboard-only, mouse-only and combined triggers.
    """

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def __init__(self, config: ShortcutConfig) -> None:

        self._policy_engine = config.policy_engine
        self._publish_action: Callable[[ActionEvent], None] = config.publish_action

        self._keyboard_only: set[str] = config.worker_map.keyboard_only
        self._mouse_only: set[str] = config.worker_map.mouse_only
        self._combined: set[str] = config.worker_map.combo

        self._combined_window: float = config.combined_window_seconds

        self.func_now: Callable[[], float] = config.func_now

        # Store recent source timestamps for combined logic
        self._recent_keyboard: Dict[str, float] = {}
        self._recent_mouse: Dict[str, float] = {}

        self._queue: queue.Queue[TriggerEvent] = queue.Queue()

        self._running: bool = False
        self._thread: threading.Thread | None = None

    # ------------------------------------------------------------------
    # Lifecycle
    # ------------------------------------------------------------------

    def start(self) -> None:
        if self._running:
            return

        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self) -> None:
        if not self._running:
            return

        self._running = False
        self._queue.put(TriggerEvent("__STOP__", "", 0.0))

        if self._thread:
            self._thread.join(timeout=1)

    # ------------------------------------------------------------------
    # Public API (Ingress)
    # ------------------------------------------------------------------

    def submit_keyboard_triggers(self, callbacks: list[str]) -> None:
        now = self.func_now()
        for cb in callbacks:
            self._queue.put((TriggerEvent("keyboard", cb, now)))

    def submit_mouse_triggers(self, callbacks: list[str]) -> None:
        now = self.func_now()
        for cb in callbacks:
            self._queue.put((TriggerEvent("mouse", cb, now)))

    # ------------------------------------------------------------------
    # Main loop
    # ------------------------------------------------------------------

    def _loop(self) -> None:
        """
        Blocking wait on queue.
        """

        while self._running:
            _TriggerEvent = self._queue.get()

            if _TriggerEvent.source == "__STOP__":
                break

            try:
                self._handle_trigger(_TriggerEvent)
            except Exception:
                logging.exception(f"[ShortcutWorker] Error handling trigger: {_TriggerEvent}")

    # ------------------------------------------------------------------
    # Trigger dispatcher
    # ------------------------------------------------------------------

    def _handle_trigger(self, _TriggerEvent: TriggerEvent) -> None:

        # -----------------------------
        # Keyboard-only
        # -----------------------------
        if _TriggerEvent.callback in self._keyboard_only:
            if _TriggerEvent.source == "keyboard":
                self._evaluate_and_publish(_TriggerEvent)
            return

        # -----------------------------
        # Mouse-only
        # -----------------------------
        elif _TriggerEvent.callback in self._mouse_only:
            if _TriggerEvent.source == "mouse":
                self._evaluate_and_publish(_TriggerEvent)
            return

        # -----------------------------
        # Combined
        # -----------------------------
        elif _TriggerEvent.callback in self._combined:
            self._handle_combined(_TriggerEvent)

    # ------------------------------------------------------------------
    # Combined coordination
    # ------------------------------------------------------------------

    def _handle_combined(self, _TriggerEvent: TriggerEvent) -> None:

        self._prune_old(_TriggerEvent.timestamp)

        if _TriggerEvent.source == "keyboard":
            self._recent_keyboard[_TriggerEvent.callback] = _TriggerEvent.timestamp

            if _TriggerEvent.callback in self._recent_mouse:
                self._try_emit_combined(_TriggerEvent)

        elif _TriggerEvent.source == "mouse":
            self._recent_mouse[_TriggerEvent.callback] = _TriggerEvent.timestamp

            if _TriggerEvent.callback in self._recent_keyboard:
                self._try_emit_combined(_TriggerEvent)

    def _try_emit_combined(self, _TriggerEvent: TriggerEvent) -> None:
        """
        Emit if policy allows, then clear state.
        """

        self._clear_combined(_TriggerEvent.callback)

        self._evaluate_and_publish(_TriggerEvent)

    def _clear_combined(self, callback: str) -> None:
        self._recent_keyboard.pop(callback, None)
        self._recent_mouse.pop(callback, None)

    def _prune_old(self, now: float) -> None:
        """
        Remove expired combined timestamps.
        """

        threshold = now - self._combined_window

        for store in (self._recent_keyboard, self._recent_mouse):
            expired = [cb for cb, ts in store.items() if ts < threshold]
            for cb in expired:
                del store[cb]

    # ------------------------------------------------------------------
    # Policy + Publish
    # ------------------------------------------------------------------

    def _evaluate_and_publish(self, _TriggerEvent: TriggerEvent) -> None:
        """
        Ask policy engine before publishing.
        """

        if self._policy_engine.evaluate(_TriggerEvent):
            self._publish_action(ActionEvent(_TriggerEvent.callback, _TriggerEvent.timestamp))
