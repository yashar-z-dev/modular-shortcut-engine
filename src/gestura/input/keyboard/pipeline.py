import logging
from typing import Dict, List, Optional

from ...models.keyboard import GestureKeyboardCondition
from ...models.event import EventData_keyboard


class KeyboardGesturePipeline:
    """
    Keyboard gesture detection pipeline (contiguous, completion-based).

    Design:
    - Indexed by LAST key (completion trigger)
    - Strict contiguous matching
    - No gap support
    - Prevent duplicate reporting
    """

    def __init__(
        self,
        gestures: List[GestureKeyboardCondition],
    ) -> None:

        self._gestures = gestures

        # last_key -> gestures
        self._trigger_index: Dict[str, List[GestureKeyboardCondition]] = {}

        # callback -> last reported end_id
        self._last_occurrence_end_id: Dict[str, int] = {}

        self._build_trigger_index()

    # ------------------------------------------------------------
    # Index Building
    # ------------------------------------------------------------

    def _build_trigger_index(self) -> None:
        for gesture in self._gestures:
            last_key = gesture.conditions[-1]
            self._trigger_index.setdefault(last_key, []).append(gesture)

    # ------------------------------------------------------------
    # Internal Matching
    # ------------------------------------------------------------

    def _sequence_end_id(
        self,
        sequence: List[str],
        events: List[EventData_keyboard],
    ) -> Optional[int]:
        """
        Strict contiguous tail match.
        Returns end_id if sequence matches the last events exactly.
        """

        seq_len = len(sequence)

        if len(events) < seq_len:
            return None

        tail = events[-seq_len:]

        for i in range(seq_len):
            if tail[i].key != sequence[i]:
                return None

        return tail[-1].id

    # ------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------

    def process_for_trigger(
        self,
        trigger_key: str,
        event_sequence: List[EventData_keyboard],
    ) -> List[str]:

        matched_callbacks: List[str] = []

        relevant_gestures = self._trigger_index.get(trigger_key)
        if not relevant_gestures:
            return matched_callbacks

        logging.debug(
            f"[KeyboardPipeline] Evaluating {len(relevant_gestures)} "
            f"gestures for trigger '{trigger_key}'"
        )

        for gesture in relevant_gestures:

            end_id = self._sequence_end_id(
                sequence=gesture.conditions,
                events=event_sequence,
            )

            if end_id is None:
                continue

            last_end_id = self._last_occurrence_end_id.get(gesture.callback)

            # Prevent duplicate reporting of same occurrence
            if last_end_id == end_id:
                continue

            self._last_occurrence_end_id[gesture.callback] = end_id
            matched_callbacks.append(gesture.callback)

        return matched_callbacks
