from dataclasses import dataclass


# Keyboard
@dataclass(frozen=True, slots=True, kw_only=True)
class KeyboardEvent:
    key: str
    press: bool

# Mouse
@dataclass(frozen=True, slots=True, kw_only=True)
class MouseMoveEvent:
    x: int
    y: int

@dataclass(frozen=True, slots=True, kw_only=True)
class MouseClickEvent:
    x: int
    y: int
    position: str
    press: bool

MouseEvent = MouseMoveEvent | MouseClickEvent
