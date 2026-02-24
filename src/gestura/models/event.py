# 100/100
"""
__all__ = (
    __EVENTS__,
    EventData_keyboard,
    MouseButtonName, MouseButtons,
    EventData_click, EventData_move
"""

from typing import Optional, Literal, Union, Annotated
from dataclasses import dataclass
from pydantic import Field
from enum import Enum


# ===== EventData Models =====
@dataclass(frozen=True, slots=True, kw_only=True)
class _Base_Event:
    """
    Args:
        id:   Primary key (sortable)
        time: Capture time(Optianl) (sortable)
    """
    id:   Optional[int]   = None
    time: Optional[float] = None


@dataclass(frozen=True, slots=True, kw_only=True)
class EventData_keyboard(_Base_Event):
    """
    Args:
        press: True if press else False
        key: All key in keyboard(ENG, another language not support all character)

    NOTE: support another language good, but change language need to restart program.

    TODO: write language convertor for another language.
    """

    key: str
    press: bool
    type: Literal["keyboard"] = "keyboard"


class MouseButtons(str, Enum):
    LEFT = "left"
    RIGHT = "right"
    MIDDLE = "middle"

@dataclass(frozen=True, slots=True, kw_only=True)
class EventData_click(_Base_Event):
    """
    Args:
        press: True if press else False
        position: click action name position
        x: Mouse position on the X axis on the monitor
        y: Mouse position on the Y axis on the monitor
    """

    x: int
    y: int
    position: MouseButtons
    press: bool
    type: Literal["click"] = "click"


@dataclass(frozen=True, slots=True, kw_only=True)
class EventData_move(_Base_Event):
    """
    Args:
        x: Mouse position on the X axis on the monitor
        y: Mouse position on the Y axis on the monitor
    """

    x: int
    y: int
    type: Literal["move"] = "move"


# ===== Support Models =====
__EVENTS__ = Annotated[
    Union[EventData_keyboard, EventData_click, EventData_move],
    Field(discriminator="type"),
]
