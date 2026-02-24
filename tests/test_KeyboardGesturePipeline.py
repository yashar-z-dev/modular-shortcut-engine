from gestura.input.keyboard.pipeline import KeyboardGesturePipeline
from gestura.models.keyboard import GestureKeyboardCondition
from gestura.models.event import EventData_keyboard

import pytest


# ------------------------------------------------------------
# Helper
# ------------------------------------------------------------

def make_gesture(sequence, callback):
    obj = GestureKeyboardCondition()
    for key in sequence:
        obj.add_condition(key)
    obj.callback = callback
    return obj


# ------------------------------------------------------------
# Basic Success
# ------------------------------------------------------------

def test_single_key_success():
    gesture = make_gesture(["esc"], "callback")

    pipeline = KeyboardGesturePipeline(gestures=[gesture])

    keys = []
    keys.append(EventData_keyboard(id=1 ,press=True, key="a"))
    keys.append(EventData_keyboard(id=2 ,press=True, key="b"))
    keys.append(EventData_keyboard(id=3 ,press=True, key="esc"))


    result = pipeline.process_for_trigger(
        trigger_key="esc",
        event_sequence=keys,
    )

    assert result == ["callback"]


# ------------------------------------------------------------
# Basic Failure
# ------------------------------------------------------------

def test_single_key_not_triggered():
    gesture = make_gesture(["esc"], "callback")

    pipeline = KeyboardGesturePipeline(gestures=[gesture])

    keys = []
    keys.append(EventData_keyboard(id=1 ,press=True, key="a"))
    keys.append(EventData_keyboard(id=2 ,press=True, key="b"))
    keys.append(EventData_keyboard(id=3 ,press=True, key="c"))

    result = pipeline.process_for_trigger(
        trigger_key="c",
        event_sequence=keys,
    )

    assert result == []


# ------------------------------------------------------------
# Ordered Sequence Success
# ------------------------------------------------------------

def test_multi_key_sequence_success():
    gesture = make_gesture(["ctrl", "k"], "callback")

    pipeline = KeyboardGesturePipeline(gestures=[gesture])

    keys = []
    keys.append(EventData_keyboard(id=1 ,press=True, key="a"))
    keys.append(EventData_keyboard(id=2 ,press=True, key="ctrl"))
    keys.append(EventData_keyboard(id=3 ,press=True, key="k"))


    result = pipeline.process_for_trigger(
        trigger_key="k",
        event_sequence=keys,
    )

    assert result == ["callback"]


# ------------------------------------------------------------
# Ordered Sequence Failure (wrong order)
# ------------------------------------------------------------

def test_multi_key_wrong_order():
    gesture = make_gesture(["ctrl", "k"], "callback")

    pipeline = KeyboardGesturePipeline(gestures=[gesture])

    keys = []
    keys.append(EventData_keyboard(id=1 ,press=True, key="k"))
    keys.append(EventData_keyboard(id=2 ,press=True, key="ctrl"))

    result = pipeline.process_for_trigger(
        trigger_key="ctrl",
        event_sequence=keys,
    )

    assert result == []


# ------------------------------------------------------------
# Multiple Gestures Same Trigger
# ------------------------------------------------------------

def test_multiple_gestures_same_trigger():
    g1 = make_gesture(["ctrl", "k"], "cb1")
    g2 = make_gesture(["ctrl", "c"], "cb2")

    pipeline = KeyboardGesturePipeline(gestures=[g1, g2])

    keys = []
    keys.append(EventData_keyboard(id=2 ,press=True, key="ctrl"))
    keys.append(EventData_keyboard(id=4 ,press=True, key="k"))

    result = pipeline.process_for_trigger(
        trigger_key="k",
        event_sequence=keys,
    )
    assert set(result) == {"cb1"}

    keys.append(EventData_keyboard(id=5 ,press=True, key="ctrl"))
    keys.append(EventData_keyboard(id=6 ,press=True, key="c"))

    result = pipeline.process_for_trigger(
        trigger_key="c",
        event_sequence=keys,
    )

    assert set(result) == {"cb2"}

# ------------------------------------------------------------
# Trigger Filtering Works
# ------------------------------------------------------------

def test_trigger_filtering_skips_unrelated():
    g1 = make_gesture(["ctrl", "k"], "cb1")
    g2 = make_gesture(["shift", "x"], "cb2")

    pipeline = KeyboardGesturePipeline(gestures=[g1, g2])

    keys = []
    keys.append(EventData_keyboard(id=1 ,press=True, key="shift"))
    keys.append(EventData_keyboard(id=3 ,press=True, key="x"))

    result = pipeline.process_for_trigger(
        trigger_key="x",
        event_sequence=keys,
    )

    assert result == ["cb2"]


# ------------------------------------------------------------
# Window Optimization Check
# ------------------------------------------------------------

def test_sequence_outside_search_window_not_detected():
    gesture = make_gesture(["a", "b", "c"], "callback")

    pipeline = KeyboardGesturePipeline(gestures=[gesture])

    # sequence is too far in history
    keys = []
    keys.append(EventData_keyboard(id=1 ,press=True, key="a"))
    keys.append(EventData_keyboard(id=2 ,press=True, key="b"))
    keys.append(EventData_keyboard(id=3 ,press=True, key="c"))
    for i in range(20):
        keys.append(EventData_keyboard(id=i+5 ,press=True, key="x"))

    result = pipeline.process_for_trigger(
        trigger_key="a",
        event_sequence=keys,
    )

    assert result == []
