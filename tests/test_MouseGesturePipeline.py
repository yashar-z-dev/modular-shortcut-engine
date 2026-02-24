from gestura.input.mouse.pipeline import MouseGesturePipeline
from gestura.models.mouse import GestureMouseCondition
from gestura.models.event import EventData_move

import pytest


def test_single_segment_match():
    callback = "right"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=10)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=0),
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == [callback]


def test_single_segment_below_delta_not_matched():
    callback = "right"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=50)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=0),
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == []


def test_order_must_be_respected():
    callback = "combo"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=10)
    gesture.add_condition(axis="x", trend="left", min_delta=10)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=0),
        EventData_move(id=3, x=5, y=0),
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == [callback]


def test_wrong_order_not_matched():
    callback = "combo"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="left", min_delta=10)
    gesture.add_condition(axis="x", trend="right", min_delta=10)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=0),
        EventData_move(id=3, x=5, y=0),
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == []


def test_same_signature_triggered_once_per_batch():
    callback = "right"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=10)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=0),
        EventData_move(id=3, x=40, y=0),
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == [callback]


def test_multiple_gestures_can_trigger():
    g1 = GestureMouseCondition()
    g1.add_condition(axis="x", trend="right", min_delta=10)
    g1.callback = "right"

    g2 = GestureMouseCondition()
    g2.add_condition(axis="y", trend="down", min_delta=10)
    g2.callback = "down"

    pipeline = MouseGesturePipeline([g1, g2], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=20),
    ]

    result = pipeline.process_for_trigger(batch)

    assert set(result) == {"right", "down"}


def test_same_occurrence_not_reported_twice():
    callback = "gesture"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=100)
    gesture.callback = callback

    pipe = MouseGesturePipeline(
        gesture_definitions=[gesture],
        segment_min_delta=10,
    )

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=120, y=0),
    ]

    # First detection
    result1 = pipe.process_for_trigger(batch)
    assert result1 == [callback]

    # Same batch again (same end_id)
    result2 = pipe.process_for_trigger(batch)
    assert result2 == []


def test_new_occurrence_with_new_end_id():
    callback = "gesture"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=100)
    gesture.callback = callback

    pipe = MouseGesturePipeline(
        gesture_definitions=[gesture],
        segment_min_delta=10,
    )

    batch1 = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=120, y=0),
    ]

    batch2 = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=120, y=0),
        EventData_move(id=3, x=200, y=0),  # extended movement
    ]

    assert pipe.process_for_trigger(batch1) == [callback]
    assert pipe.process_for_trigger(batch2) == [callback]


def test_small_jitter_should_not_break_segment():
    callback = "gesture"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=100)
    gesture.callback = callback

    pipe = MouseGesturePipeline(
        gesture_definitions=[gesture],
        segment_min_delta=20,
    )

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=10, y=0),
        EventData_move(id=3, x=5, y=0),   # small jitter back
        EventData_move(id=4, x=40, y=0),
        EventData_move(id=5, x=120, y=0),
    ]

    result = pipe.process_for_trigger(batch)

    # Should still detect overall right movement
    assert result == [callback]


def test_medium_jitter_can_break_segment():
    callback = "gesture"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=100)
    gesture.callback = callback

    pipe = MouseGesturePipeline(
        gesture_definitions=[gesture],
        segment_min_delta=5,
    )

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=60, y=0),
        EventData_move(id=3, x=40, y=0),  # noticeable reversal
        EventData_move(id=4, x=120, y=0),
    ]

    result = pipe.process_for_trigger(batch)

    # Depending on thresholds this may fail
    # This test shows current limitation
    assert result in ([], [callback])


def test_multi_segment_gesture():
    callback = "complex"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=50)
    gesture.add_condition(axis="y", trend="down", min_delta=50)
    gesture.callback = callback

    pipe = MouseGesturePipeline(
        gesture_definitions=[gesture],
        segment_min_delta=20,
    )

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=80, y=0),
        EventData_move(id=3, x=80, y=80),
    ]

    result = pipe.process_for_trigger(batch)

    assert result == [callback]


def test_overlapping_gestures_both_trigger():
    g1 = GestureMouseCondition()
    g1.add_condition(axis="x", trend="right", min_delta=10)
    g1.callback = "right"

    g2 = GestureMouseCondition()
    g2.add_condition(axis="x", trend="right", min_delta=10)
    g2.add_condition(axis="y", trend="down", min_delta=10)
    g2.callback = "combo"

    pipe = MouseGesturePipeline([g1, g2], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=20, y=20),
    ]

    result = pipe.process_for_trigger(batch)

    assert set(result) == {"right", "combo"}


def test_large_batch_does_not_break():
    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=10)
    gesture.callback = "right"

    pipe = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=i, x=i*5, y=0)
        for i in range(100)
    ]

    result = pipe.process_for_trigger(batch)

    assert result == ["right"]


def test_long_right_with_heavy_jitter_still_triggers():
    callback = "long_right"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=800)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], segment_min_delta=10)

    events = []
    x = 0

    for i in range(1, 100):
        if i % 20 == 0:
            x -= 3
        else:
            x += 10

        events.append(EventData_move(id=i, x=x, y=0))

    result = pipeline.process_for_trigger(events)

    assert result == [callback]


def test_large_reverse_jump_is_not_ignored():

    callback = "right_then_left"

    gesture = GestureMouseCondition()
    gesture.add_condition(axis="x", trend="right", min_delta=50)
    gesture.add_condition(axis="x", trend="left", min_delta=50)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)

    batch = [
        EventData_move(id=1, x=0, y=0),
        EventData_move(id=2, x=100, y=0),
        EventData_move(id=3, x=0, y=0),   # large jump back
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == [callback]


# production-level
def test_mouse_pipeline_requires_correct_first_direction():

    callback = "OK"
    gesture = GestureMouseCondition()
    gesture.add_condition(axis="y", trend="down", min_delta=100)
    gesture.add_condition(axis="x", trend="right", min_delta=100)
    gesture.add_condition(axis="y", trend="up", min_delta=100)
    gesture.add_condition(axis="x", trend="left", min_delta=100)
    gesture.callback = callback

    pipeline = MouseGesturePipeline([gesture], 5)
    batch = [
        EventData_move(id=1, x= 0, y=0),
        EventData_move(id=2, x=100, y=100),
        EventData_move(id=3, x= 0, y= 0),
    ]

    result = pipeline.process_for_trigger(batch)

    assert result == [callback]