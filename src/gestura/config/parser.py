# 100/100

"""
tests:
    test_loader.py
"""

from dataclasses import dataclass
from typing import Any

from ..models.keyboard import GestureKeyboardCondition
from ..models.mouse import GestureMouseCondition
from ..models.policy import CallbackPolicy


@dataclass(frozen=True, slots=True)
class ShortcutConfigBundle:
    """
    Fully parsed shortcut configuration.
    """

    # For listeners
    keyboard_gestures: list[GestureKeyboardCondition]
    mouse_gestures: list[GestureMouseCondition]

    # For worker dispatch
    worker_map: "WorkerGestureMap"

    # For policy engine
    policies: dict[str, CallbackPolicy]


# -------------------------
# Worker Map
# -------------------------

@dataclass(frozen=True, slots=True)
class WorkerGestureMap:
    keyboard_only: set[str]
    mouse_only: set[str]
    combo: set[str]


@dataclass(frozen=True, slots=True)
class GesturesMap:
    keyboard_gestures: list[GestureKeyboardCondition]
    mouse_gestures: list[GestureMouseCondition]


def _build_worker_map(_GesturesMap: GesturesMap) -> WorkerGestureMap:
    """
    Build worker dispatch map.
    """

    keyboard_callbacks = {g.callback for g in _GesturesMap.keyboard_gestures}
    mouse_callbacks = {g.callback for g in _GesturesMap.mouse_gestures}

    combo = keyboard_callbacks & mouse_callbacks
    keyboard_only = keyboard_callbacks - combo
    mouse_only = mouse_callbacks - combo

    return WorkerGestureMap(
        keyboard_only=keyboard_only,
        mouse_only=mouse_only,
        combo=combo
    )


# -------------------------
# Policy Builder
# -------------------------

def _build_policy_map(config: list[dict[str, Any]]) -> dict[str, CallbackPolicy]:
    """
    Build callback → policy mapping.
    """

    policy_map: dict[str, CallbackPolicy] = {}

    for item in config:
        callback = item["callback"]

        policy_cfg = item.get("policy", {})

        policy_map[callback] = CallbackPolicy(
            cooldown_seconds=policy_cfg.get("cooldown_seconds", 0.0),
            rate_window_seconds=policy_cfg.get("rate_window_seconds", 1.0),
            max_triggers=policy_cfg.get("max_triggers", 1)
        )

    return policy_map


# -------------------------
# Public Parser
# -------------------------
def _buil_gesters_map(config: list[dict[str, Any]]) -> GesturesMap:
    """
    Parse full shortcut config and return structured bundle.
    """

    keyboard_list: list[GestureKeyboardCondition] = []
    mouse_list: list[GestureMouseCondition] = []

    for item in config:
        callback = item["callback"]

        keyboard_conditions = item.get("keyboard", {}).get("conditions", [])
        mouse_conditions = item.get("mouse", {}).get("conditions", [])

        if keyboard_conditions:
            keyboard_list.append(
                GestureKeyboardCondition(
                    conditions=keyboard_conditions,
                    callback=callback
                )
            )

        if mouse_conditions:
            mouse_list.append(
                GestureMouseCondition(
                    conditions=mouse_conditions,
                    callback=callback
                )
            )

    return GesturesMap(
        keyboard_gestures=keyboard_list,
        mouse_gestures=mouse_list
    )


def parse_shortcut_config(config: list[dict[str, Any]]) -> ShortcutConfigBundle:
    """
    Parse full shortcut config and return structured bundle.
    """

    _gesters_map = _buil_gesters_map(config)
    worker_map = _build_worker_map(_gesters_map)

    policy_map = _build_policy_map(config)

    return ShortcutConfigBundle(
        keyboard_gestures=_gesters_map.keyboard_gestures,
        mouse_gestures=_gesters_map.mouse_gestures,
        worker_map=worker_map,
        policies=policy_map
    )
