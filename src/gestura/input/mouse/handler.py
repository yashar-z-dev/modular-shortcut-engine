import logging
from typing import Callable, Optional

from ...models.inputs import MouseEvent, MouseMoveEvent
from ...config import MouseConfig
from ...models.event import EventData_click, MouseButtons, EventData_move
from .pipeline import MouseGesturePipeline
from ..event_buffer import EventBuffer


class MouseApp:
    """
    Event-driven mouse gesture handler.

    Design principles:
    - Time-windowed buffering (via EventBuffer)
    - Lightweight activation guard (min sample count)
    - All gesture recognition delegated to MouseGesturePipeline
    - No motion accumulation state in this layer
    """

    def __init__(self, config: MouseConfig) -> None:
        self._move_counter: int = 0    # incremental id
        self._move_event_id: int = 0   # incremental id
        self._click_event_id: int = 0  # incremental id
        self._rate_frequency: int = 1  # frequency rate filtering for low-performance

        # External callback to notify when a gesture is triggered
        self._emit_callback: Callable[[list[str]], None] = config.on_trigger

        # Pipeline handles all recognition logic
        self._pipeline = MouseGesturePipeline(
            gesture_definitions=config.gestures,
            segment_min_delta=config.min_delta
        )

        # Time-sliced event buffer
        self._buffer = EventBuffer(window=config.BufferWindowSeconds)

    # ------------------------------------------------------------------ #
    # Validator
    # ------------------------------------------------------------------ #
    def _validator(self, event: MouseEvent) -> Optional[EventData_move | EventData_click]:
        """
        Generate EventData_move | EventData_click private models.
        """

        # Filter negative coordinates
        if event.x < 0 or event.y < 0:
            # warning (most apply map for negative values, some time rate negative so hight)
            logging.debug(f"Ignored unsupported mouse negative; x={event.x}, y={event.y}")
            return

        # Detected move or click
        if isinstance(event, MouseMoveEvent):
            # Apply sampling rate
            if self.should_skip_move():
                return

            # move event: Generate EventData_move
            # Assign internal move ID
            valid_event = EventData_move(id=self._move_event_id, x=event.x, y=event.y)
            self._move_event_id += 1

        else:
            # click event: Generate EventData_click
            # Assign internal click ID
            try:
                valid_event = EventData_click(
                    id=self._click_event_id,
                    x=event.x, y=event.y,
                    position=MouseButtons(event.position),
                    press=event.press
                )
            except ValueError:
                logging.warning("Ignored unsupported mouse position button: %s", event.position)
                return

            self._click_event_id += 1

        return valid_event
    
    def should_skip_move(self) -> bool:
        """ frequency filter move """
        self._move_counter += 1
        # Apply sampling rate
        if self._move_counter % self._rate_frequency != 0:
            return True

        return False

    def _handle_move(self, event: EventData_move) -> None:
        """
        Add move event to buffer and evaluate gestures if sufficient data exists.
        """
        self._buffer.add(event)

        # Lightweight guard — prevents processing extremely small sequences
        self._evaluate_gestures()

    def _handle_click(self, event: EventData_click) -> None:
        """
        Click handling is currently not part of gesture recognition.
        Reserved for future extension.
        """

        pass

    # ------------------------------------------------------------------ #
    # Core Processing
    # ------------------------------------------------------------------ #

    def _evaluate_gestures(self):
        """
        Snapshot current buffer and delegate recognition to pipeline.
        """

        snapshot = self._buffer.snapshot()
        callbacks = self._pipeline.process_for_trigger(snapshot)

        self._emit_callback(callbacks)

    # ------------------------------------------------------------------ #
    # API
    # ------------------------------------------------------------------ #
    def HandleEvens(self, event: MouseEvent) -> None:

        valid_event = self._validator(event)
        if valid_event is None:
            return

        if valid_event.type == "move":
            self._handle_move(valid_event)
        elif valid_event.type == "click":
            self._handle_click(valid_event)
