# 100/100

import logging
from typing import Callable, Optional

from ...config import KeyboardConfig
from ...models.inputs import KeyboardEvent

from ...models.keyboard import GestureKeyboardCondition
from ...models.event import EventData_keyboard
from .pipeline import KeyboardGesturePipeline
from ...utils.key_normalizer import KeyUtils
from ..event_buffer import EventBuffer


class KeyboardApp:
    """
    Event-driven keyboard gesture processor.

    Responsibilities:
    - Receive raw keyboard events
    - Maintain a time-windowed buffer of pressed keys
    - Dispatch relevant gestures based on starting key
    - Emit triggered callbacks
    """

    def __init__(self, config: KeyboardConfig) -> None:
        """
        Args:
            config: Keyboard configuration containing gesture definitions and runtime settings.
            on_trigger: Callback executed when a gesture is successfully recognized.
        """
        self._event_id: int = 0  # incremental id

        # External callback to notify when a gesture is triggered
        self._emit_callback: Callable[[list[str]], None] = config.on_trigger

        # Configuration
        self._gesture_definitions: list[GestureKeyboardCondition] = config.gestures

        # Time-windowed key buffer
        self._event_buffer = EventBuffer(config.BufferWindowSeconds) # Time window for gesture detection

        # Gesture pipeline (responsible for matching logic)
        # Internally builds an index by starting key
        self._gesture_pipeline = KeyboardGesturePipeline(
            gestures=self._gesture_definitions
        )

    # ------------------------------------------------------------------
    # Validator
    # ------------------------------------------------------------------
    def _validator(self, event: KeyboardEvent) -> Optional[EventData_keyboard]:
        """
        Generate EventData_keyboard private model.
        """

        key_name = KeyUtils.parse_key(key=event.key, output_type="str")
        if not key_name:
            logging.debug("Ignored unsupported key name: %s", event.key)
            return

        valid_event = EventData_keyboard(id=self._event_id, key=key_name, press=event.press)
        self._event_id += 1
        return valid_event

    # ------------------------------------------------------------------
    # Internal Event Handlers
    # ------------------------------------------------------------------

    def _handle_key_press(self, event: EventData_keyboard) -> None:
        """
        Process key press events.
        Adds key to buffer and evaluates relevant gestures.
        """

        # Store key inside sliding window buffer
        self._event_buffer.add(event)

        # Evaluate only gestures that start with this key
        self._evaluate_gestures(trigger_key=event.key)

    def _handle_key_release(self, event: EventData_keyboard) -> None:
        """
        Process key release events.
        Currently not used in gesture evaluation.
        """

        pass

    # ------------------------------------------------------------------
    # Gesture Evaluation
    # ------------------------------------------------------------------

    def _evaluate_gestures(self, trigger_key: str) -> None:
        """
        Evaluate gestures relevant to the given trigger key.

        NOTE:
        - Snapshot is intentionally preserved to prevent mutation-related
          side effects during evaluation.
        - Pipeline internally uses trigger-key indexing for efficiency.
        """

        # Take snapshot to ensure consistency across multi-stage processing
        current_sequence = self._event_buffer.snapshot()

        # Process only gestures mapped to this starting key
        matched_callbacks = self._gesture_pipeline.process_for_trigger(
            trigger_key=trigger_key,
            event_sequence=current_sequence,
        )

        # Emit callbacks
        self._emit_callback(matched_callbacks)


    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #
    def HandleEvens(self, event: KeyboardEvent) -> None:
        """
        Main entry point for incoming keyboard events.
        Normalizes and routes events to appropriate handlers.
        """

        valid_event = self._validator(event)
        if valid_event is None:
            return

        if event.press:
            self._handle_key_press(valid_event)
        else:
            self._handle_key_release(valid_event)
