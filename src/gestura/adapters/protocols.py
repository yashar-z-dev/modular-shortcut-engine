from typing import Protocol, Callable
from ..models.inputs import MouseEvent, KeyboardEvent

# --------------------------------------------------
# Base Listener
# --------------------------------------------------

class Listener(Protocol):
    """Minimal event source abstraction."""

    def start(self) -> None: ...
    def stop(self) -> None: ...


# --------------------------------------------------
# Keyboard Listener Type
# --------------------------------------------------

class KeyboardListenerType(Protocol):
    """
    Creates a keyboard listener that forwards
    key events to the provided callback.
    """

    def __call__(
        self,
        on_event: Callable[[KeyboardEvent], None],
    ) -> Listener: ...


# --------------------------------------------------
# Mouse Listener Type
# --------------------------------------------------

class MouseListenerType(Protocol):
    """
    Creates a mouse listener that forwards
    move/click events to the provided callbacks.
    """

    def __call__(
        self,
        on_event: Callable[[MouseEvent], None],
    ) -> Listener: ...
