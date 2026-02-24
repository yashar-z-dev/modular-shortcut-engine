# 91/100

"""
tests:
    test_MouseGesturePipeline.py
"""

import logging
from typing import Any, Tuple, Optional

from ...models.mouse import GestureMouseCondition
from ...models.event import EventData_move


class MouseGestureDetector:
    """
    Pure gesture detector.
    No deduplication. No filtering.
    Returns raw occurrences.
    """

    def __init__(
        self,
        gesture_definitions: list[GestureMouseCondition],
        segment_min_delta: float,
        jitter_max_delta: Optional[float] = None,
        lookahead: int = 2,
    ):
        self.gesture_definitions = gesture_definitions
        self.segment_min_delta = segment_min_delta
        self.jitter_max_delta = jitter_max_delta or segment_min_delta
        self.lookahead = lookahead

        self._first_condition_index: dict[Tuple[str, str], list[GestureMouseCondition]] = {}
        self._build_first_condition_index()

    # ============================================================
    # INDEX
    # ============================================================

    def _build_first_condition_index(self) -> None:
        for gesture in self.gesture_definitions:
            first = gesture.conditions[0]
            key = (first.axis, first.trend)
            self._first_condition_index.setdefault(key, []).append(gesture)

    # ============================================================
    # SEGMENT EXTRACTION
    # ============================================================

    def _movement_trend(self, axis: str, delta: float) -> Optional[str]:
        if delta == 0:
            return None
        if axis == "x":
            return "right" if delta > 0 else "left"
        return "down" if delta > 0 else "up"

    def extract_segments(self, events: list[EventData_move]) -> list[dict[str, Any]]:
        segments: list[dict[str, Any]] = []
        segments += self._build_axis_segments(events, "x")
        segments += self._build_axis_segments(events, "y")

        segments.sort(key=lambda s: s["start_id"])

        logging.debug(
            "[Segments] %s",
            [
                f"{s['axis']}:{s['trend']} Δ{s['delta']} ({s['start_id']}→{s['end_id']})"
                for s in segments
            ]
        )

        return segments

    def _build_axis_segments(
        self,
        events: list[EventData_move],
        axis: str,
    ) -> list[dict[str, Any]]:

        segments: list[dict[str, Any]] = []

        start_index = 0
        start_value = getattr(events[0], axis)
        current_trend: Optional[str] = None

        for i in range(1, len(events)):

            prev = events[i - 1]
            curr = events[i]

            delta = getattr(curr, axis) - getattr(prev, axis)
            new_trend = self._movement_trend(axis, delta)

            if not new_trend:
                continue

            if current_trend is None:
                current_trend = new_trend
                continue

            if new_trend != current_trend:

                logging.debug(
                    "[TrendChange] axis=%s id=%s %s→%s",
                    axis,
                    curr.id,
                    current_trend,
                    new_trend,
                )

                # decide if real reversal
                if not self._is_real_reversal(
                    events,
                    axis,
                    i,
                    current_trend,
                    delta,
                ):
                    continue  # jitter → ignore completely

                # REAL reversal → close segment
                delta_total = abs(getattr(prev, axis) - start_value)

                if delta_total >= self.segment_min_delta:
                    segments.append({
                        "start_id": events[start_index].id,
                        "end_id": prev.id,
                        "axis": axis,
                        "trend": current_trend,
                        "delta": int(delta_total),
                    })

                start_index = i - 1
                start_value = getattr(prev, axis)
                current_trend = new_trend

        # finalize
        if current_trend:
            delta_total = abs(getattr(events[-1], axis) - start_value)

            if delta_total >= self.segment_min_delta:
                segments.append({
                    "start_id": events[start_index].id,
                    "end_id": events[-1].id,
                    "axis": axis,
                    "trend": current_trend,
                    "delta": int(delta_total),
                })

        return segments

    def _is_real_reversal(
        self,
        events: list[EventData_move],
        axis: str,
        index: int,
        current_trend: str,
        delta: float,
    ) -> bool:
        """
        Decide if trend change is real or jitter.
        """

        # 1️⃣ Large jump → always real
        if abs(delta) >= self.jitter_max_delta:
            logging.debug(
                "[Reversal] Large jump axis=%s id=%s Δ=%s → REAL",
                axis,
                events[index].id,
                delta,
            )
            return True

        # 2️⃣ Small movement → lookahead confirmation
        opposite_trend = self._movement_trend(axis, delta)
        confirm = 0

        max_check = min(len(events), index + self.lookahead + 1)

        for j in range(index + 1, max_check):
            d = getattr(events[j], axis) - getattr(events[j - 1], axis)
            trend = self._movement_trend(axis, d)

            if trend == opposite_trend:
                confirm += 1
            elif trend == current_trend:
                logging.debug(
                    "[Reversal] JITTER axis=%s id=%s → ignored",
                    axis,
                    events[index].id,
                )
                return False

        if confirm >= self.lookahead:
            logging.debug(
                "[Reversal] Confirmed axis=%s id=%s → REAL",
                axis,
                events[index].id,
            )
            return True

        logging.debug(
            "[Reversal] Not enough confirmation axis=%s id=%s → JITTER",
            axis,
            events[index].id,
        )
        return False

    # ============================================================
    # MATCHING
    # ============================================================

    def _match_gesture(
        self,
        segments: list[dict[str, Any]],
        gesture: GestureMouseCondition,
        start_segment: dict[str, Any],
    ) -> Optional[int]:

        last_end_id = start_segment["end_id"]

        for cond in gesture.conditions[1:]:

            found = False

            for seg in segments:
                if seg["end_id"] < last_end_id:
                    continue

                if (
                    seg["axis"] == cond.axis
                    and seg["trend"] == cond.trend
                    and seg["delta"] >= cond.min_delta
                ):
                    last_end_id = seg["end_id"]
                    found = True
                    break

            if not found:
                logging.debug(
                    "[MatchFail] %s failed at condition %s",
                    gesture.callback,
                    cond
                )
                return None

        logging.debug(
            "[MatchSuccess] %s ending at id=%s",
            gesture.callback,
            last_end_id
        )

        return last_end_id

    # ============================================================
    # PUBLIC
    # ============================================================

    def detect(self, events: list[EventData_move]) -> list[Tuple[str, int]]:
        """
        Returns raw (callback, occurrence_end_id)
        """

        occurrences: list[Tuple[str, int]] = []

        segments = self.extract_segments(events)
        if not segments:
            return occurrences

        for seg in segments:

            key = (seg["axis"], seg["trend"])
            candidates = self._first_condition_index.get(key, [])

            for gesture in candidates:

                first = gesture.conditions[0]

                if seg["delta"] < first.min_delta:
                    continue

                end_id = self._match_gesture(segments, gesture, seg)

                if end_id is not None:
                    occurrences.append((gesture.callback, end_id))

        return occurrences


class MouseGestureOccurrenceFilter:
    """
    Filters raw occurrences.
    Prevents duplicate triggering.
    """

    def __init__(self):
        self._last_occurrence_end_id: dict[str, int] = {}

    def filter(
        self,
        occurrences: list[Tuple[str, int]]
    ) -> list[str]:

        triggered: list[str] = []

        for callback, end_id in occurrences:

            last = self._last_occurrence_end_id.get(callback)

            logging.debug(
                "[OccurrenceCheck] %s last=%s new=%s",
                callback,
                last,
                end_id
            )

            if last is None or end_id > last:
                triggered.append(callback)
                self._last_occurrence_end_id[callback] = end_id

        return triggered


class MouseGesturePipeline:

    def __init__(self, gesture_definitions: list[GestureMouseCondition], segment_min_delta: float):
        self.detector = MouseGestureDetector(
            gesture_definitions=gesture_definitions,
            segment_min_delta=segment_min_delta,
        )
        self.filter = MouseGestureOccurrenceFilter()

    def process_for_trigger(self, events: list[EventData_move]):
        raw = self.detector.detect(events)
        return self.filter.filter(raw)
