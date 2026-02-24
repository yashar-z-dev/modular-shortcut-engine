# 100/100

from typing import Callable
from dataclasses import dataclass, field
import time

from ..models.keyboard import GestureKeyboardCondition
from ..models.mouse import GestureMouseCondition
from ..models.policy import PolicyEngineProtocol, ActionEvent
from ..config.parser import WorkerGestureMap


# ===== Models =====
@dataclass(frozen=True, slots=True)
class KeyboardConfig:
    """
    Configuration container for KeyboardAppMain.

    Attributes:
        gestures (list[GestureKeyboardCondition]): # edit(2026-01-27)
            A list of gesture definitions where each gesture is a dictionary
            containing:
                - 'conditions': a list of keys that define the gesture (e.g., ["ctrl", "space"])
                - 'callback': a str returned when the gesture triggers.
            Example:
                [{"conditions": ["ctrl", "a"], "callback": "some_name"}]

    ===== Usage Example =====:
        config = KeyboardConfig(
            gestures=[
                {"conditions": ["alt", "space", "space"], 
                 "callback": "Alt+Space+Space triggered"}
            ],
            on_trigger = print
        )
    """

    gestures: list[GestureKeyboardCondition] = field(default_factory=list)
    on_trigger: Callable[[list[str]], None] = lambda _: None
    BufferWindowSeconds: float = 1.5


@dataclass(frozen=True, slots=True)
class MouseConfig:
    """
    Configuration container for MouseAppMain.

    Attributes:
        gestures (List[Dict[str, Any]]):
            A list of gesture definitions where each gesture is a dictionary
            containing:
                - 'conditions': a list of directional or segment conditions
                - 'callback': a str returned when the gesture triggers.
            Example:
                [{"conditions": ["up", "right", "down"], "callback": "some_name"}]

        min_delta (float):
            minimum delta to keep a segment (final filter)

    ===== Usage Example =====:
        config = MouseConfig(
            gestures=[
                {"conditions": [
                    {"axis": "y", "trend": "up", "min_delta": 900}
                    {"axis": "y", "trend": "left", "min_delta": 50}
                    ],
                 "callback": "Mouse gesture triggered"}
            ],
            on_trigger=print
        )
    """
    gestures: list[GestureMouseCondition] = field(default_factory=list)
    on_trigger: Callable[[list[str]], None] = lambda _: None
    BufferWindowSeconds: float = 4.0
    min_delta: float = 10.0


@dataclass(frozen=True, slots=True)
class ShortcutConfig:
    policy_engine: PolicyEngineProtocol
    publish_action: Callable[[ActionEvent], None]
    worker_map: WorkerGestureMap
    combined_window_seconds: float = 4.0
    func_now: Callable[[], float] = time.monotonic
