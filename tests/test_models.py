from gestura.models.combine import GestureCombine_KM
from gestura.models.keyboard import GestureKeyboard
from gestura.models.mouse import GestureMouse

import pytest


def test_GestureCombine_sample_useage():
    m = GestureCombine_KM()
    m.mouse.add_condition(axis="x", trend="right", min_delta=444)
    m.mouse.add_condition(axis="y", trend="up", min_delta=999)
    m.keyboard.add_condition("ctrl")
    m.callback = "test"

    assert len(m.mouse.conditions) == 2
    assert len(m.keyboard.conditions) == 1
    assert m.callback == "test"


def test_GestureCombine_insert_condition_as_Iterable():
    m = GestureCombine_KM()

    data_M = [
        {"axis": "x", "trend": "left", "min_delta": 444},
        {"axis": "x", "trend": "right", "min_delta": 578},
        {"axis": "y", "trend": "up", "min_delta": 444}
        ]
    m.mouse.add_condition(data_M)
    assert len(m.mouse.conditions) == len(data_M)
    for cond in m.mouse.conditions:
        assert cond.axis in ["x", "y"]


    data_K = ("ctrl", "alt", "shift", "h")
    m.keyboard.add_condition(data_K)
    assert len(m.keyboard.conditions) == len(data_K)


def test_GestureKeyboard_insert_condition_as_Iterable():
    data = {
    "conditions": [
        "ctrl", 
        "alt"
    ]
    }
    m = GestureKeyboard.model_validate(data)
    assert len(m.conditions) == len(data["conditions"])

    one_cond = "ctrl"
    list_of_cond = ["shift", "alt"]
    m.add_condition(one_cond)
    m.extend(list_of_cond)

    assert len(m.conditions) == len(data["conditions"]) + len(list_of_cond) + 1


def test_GestureMouse_insert_condition_as_Iterable():
    data = {
    "conditions": [
        {"axis": "y", "trend": "down", "min_delta": 100},
        {"axis": "x", "trend": "right", "min_delta": 100},
    ]
    }
    m = GestureMouse.model_validate(data)
    assert len(m.conditions) == len(data["conditions"])

    for i in range(3):
        m.add_condition(axis="y", trend="down" if i // 2 == 0 else "up", min_delta=i)
    assert len(m.conditions) == len(data["conditions"]) + 3
    assert len(m.x()) == 1
    assert len(m.y()) == 4