import json
import logging
from typing import get_args

from gestura.models.mouse import GestureMouseValidator
from gestura.config.parser import parse_shortcut_config

import pytest


@pytest.fixture
def gesture_config():
    from pathlib import Path
    BASE_DIR = Path(__file__).resolve().parent
    json_path = BASE_DIR / "sample_config.json"
    logging.info(json_path)
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)


# -------------------------------------------------
# Helpers
# -------------------------------------------------

def gestures_to_canonical(mouse, keyboard):
    result = {}

    # merge mouse
    for m in mouse:
        result.setdefault(m.callback, {
            "callback": m.callback,
            "mouse": {"conditions": []},
            "keyboard": {"conditions": []},
        })
        result[m.callback]["mouse"]["conditions"] = [
            c.model_dump() for c in m.conditions
        ]

    # merge keyboard
    for k in keyboard:
        result.setdefault(k.callback, {
            "callback": k.callback,
            "mouse": {"conditions": []},
            "keyboard": {"conditions": []},
        })
        result[k.callback]["keyboard"]["conditions"] = k.conditions

    return list(result.values())


def normalize_config(config):
    return [
        {
            "callback": item["callback"],
            "mouse": {
                "conditions": item["mouse"]["conditions"],
            },
            "keyboard": {
                "conditions": item["keyboard"]["conditions"],
            },
        }
        for item in config
    ]


# -------------------------------------------------
# Tests
# -------------------------------------------------

def test_load_keyboard_mouse_roundtrip(gesture_config):
    bundle = parse_shortcut_config(gesture_config)

    canonical = gestures_to_canonical(bundle.mouse_gestures, bundle.keyboard_gestures)
    expected = normalize_config(gesture_config)

    # sort by callback for deterministic comparison
    assert sorted(canonical, key=lambda x: x["callback"]) == \
           sorted(expected, key=lambda x: x["callback"])


def test_callbacks_preserved(gesture_config):
    bundle = parse_shortcut_config(gesture_config)

    loaded_callbacks = {
        g.callback for g in bundle.mouse_gestures
    } | {
        g.callback for g in bundle.keyboard_gestures
    }

    original_callbacks = {
        item["callback"] for item in gesture_config
    }

    assert loaded_callbacks == original_callbacks


def test_mouse_conditions_structure(gesture_config):
    bundle = parse_shortcut_config(gesture_config)

    # build lookup by callback
    source_lookup = {
        item["callback"]: item["mouse"]["conditions"]
        for item in gesture_config
    }

    for m in bundle.mouse_gestures:
        src_conditions = source_lookup[m.callback]

        assert len(m.conditions) == len(src_conditions)

        for cond_obj, cond_src in zip(m.conditions, src_conditions):
            assert cond_obj.model_dump() == cond_src


def test_mouse_condition_types(gesture_config):
    bundle = parse_shortcut_config(gesture_config)

    valid_types = get_args(GestureMouseValidator)

    for m in bundle.mouse_gestures:
        for cond in m.conditions:
            assert isinstance(cond, valid_types)


def test_empty_conditions_not_created(gesture_config):
    bundle = parse_shortcut_config(gesture_config)

    # no object should exist with empty condition list
    for m in bundle.mouse_gestures:
        assert len(m.conditions) > 0

    for k in bundle.keyboard_gestures:
        assert len(k.conditions) > 0


def test_alignment_by_callback(gesture_config):
    bundle = parse_shortcut_config(gesture_config)

    mouse_callbacks = {m.callback for m in bundle.mouse_gestures}
    keyboard_callbacks = {k.callback for k in bundle.keyboard_gestures}

    config_mouse_callbacks = {
        item["callback"]
        for item in gesture_config
        if item["mouse"]["conditions"]
    }

    config_keyboard_callbacks = {
        item["callback"]
        for item in gesture_config
        if item["keyboard"]["conditions"]
    }

    assert mouse_callbacks == config_mouse_callbacks
    assert keyboard_callbacks == config_keyboard_callbacks
