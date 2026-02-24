# 100/100

"""
TriggerEvent  →  Policy  →  ActionEvent
"""

from dataclasses import dataclass, field
from typing import Literal, Protocol
from collections import deque


@dataclass(frozen=True, slots=True)
class TriggerEvent:
    source: Literal["__STOP__", "keyboard", "mouse"]
    callback: str
    timestamp: float


@dataclass(frozen=True, slots=True)
class ActionEvent:
    callback: str
    triggered_at: float


@dataclass(frozen=True, slots=True)
class CallbackPolicy:
    """
    Immutable policy configuration per callback.
    """

    # Minimum time between consecutive executions
    cooldown_seconds: float = 0.0

    # Maximum executions allowed inside rate_window_seconds
    max_triggers: int = 5

    # Time window for rate limiting
    rate_window_seconds: float = 1.0


@dataclass(slots=True)
class CallbackState:
    """
    Runtime state per callback.
    """

    # Last successful execution time
    last_executed_at: float = 0.0

    # Execution timestamps for sliding rate window
    execution_timestamps: deque[float] = field(default_factory=deque)


class PolicyEngineProtocol(Protocol):
    """
    Public contract required by ShortcutWorker.
    """

    def evaluate(self, _TriggerEvent: TriggerEvent) -> bool: ...
