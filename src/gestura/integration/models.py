from dataclasses import dataclass
from typing import Protocol, TypeVar, Generic, Type

# ==============================
# Type Variables
# ==============================

# T_co: covariant type produced by Logic (Logic → payload)
T_co = TypeVar("T_co", covariant=True)
# T_contra: contravariant type consumed by Action (Action ← payload)
T_contra = TypeVar("T_contra", contravariant=True)
T = TypeVar("T")
C = TypeVar("C")

# ==============================
# LogicResult: wrapper for Logic output
# ==============================

@dataclass(frozen=True, slots=True)
class LogicResult(Generic[T_co]):
    """
    The result of a Logic execution.

    Attributes:
        ui_message: message to show in UI
        payload: data to pass to Action
    """
    ui_message: str
    payload: T_co

# ==============================
# Protocols
# ==============================

class LogicProtocol(Protocol[T_co]):
    """
    Logic is a pure computation unit.
    All dependencies should be injected in __init__.
    execute() should NOT take parameters.
    """
    def execute(self) -> LogicResult[T_co]:
        ...

class ActionProtocol(Protocol[T_contra]):
    """
    Action consumes Logic output (payload) and performs side-effects.
    execute() MUST take payload as input.
    """
    def execute(self, payload: T_contra) -> None:
        ...

# ==============================
# Callback Configuration
# ==============================
@dataclass(frozen=True, slots=True)
class CallbackConfig(Generic[T]):
    """
    Defines a callback pairing Logic and Action.

    Attributes:
        logic: class implementing LogicProtocol
        action: class implementing ActionProtocol
        status: whether to show status in UI
        notification: whether to trigger notification
    """
    logic: Type[LogicProtocol[T]]
    action: Type[ActionProtocol[T]]
    status: bool = True
    notification: bool = True
