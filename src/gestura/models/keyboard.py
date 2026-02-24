# 100/100

"""
__all__ = (
    GestureKeyboard, GestureKeyboardCondition, TEST_GestureKeyboard, TEST_GestureKeyboardCondition
    )
"""

# NOTE: CPU 0.05% USE

from typing import Iterable
from pydantic import BaseModel, Field, ConfigDict


# ========== Container model ==========
class GestureKeyboard(BaseModel):
    """
    Model structure for Keyboard Gesture.

    :param conditions: List of Keyboard Keys (e.g. ["esc", "ctrl", "shift", "alt", "a", "z", "/"])

    TODO: ["f1", ..., "f12", "H", "|"] => The support for these keys is not stable enough.
    """

    model_config = ConfigDict(extra="forbid")

    conditions: list[str] = Field(default_factory=list)

    # -------- implementation --------
    def add_condition(self, data: str | list[str] | tuple[str, ...]) -> None:
        """
        version: date(2026-01-26)

        NOTE: This method was created to standardize the project, otherwise there is no need for validation in this version.
        Append without validate.
        :param data: Description
        :type data: str
        """

        if isinstance(data, list | tuple):
            self.conditions.extend(data)
            return None

        # single item
        self.conditions.append(data)
        return None

    # -------- alternative API --------
    def add(self, cond: str) -> None:
        """
        Append without validate.
        :param cond: Description
        :type cond: str
        """

        self.conditions.append(cond)

    def extend(self, conds: Iterable[str]) -> None:
        """
        Append without validate.
        :param cond: Description
        :type cond: str
        """

        self.conditions.extend(conds)
    
    # -------- helpers --------
    def empty(self) -> None:
        """
        Update and add new methods for get and filtering or sorting.        
        """

        return None


# ===== SHORTCUT JSON Keyboard =====
class GestureKeyboardCondition(GestureKeyboard):
    """
    Define keyboard gestures for the conditions required to trigger the action.

    :param callback: The name of the method to be executed when the gesture is triggered (TODO: most update for support Callable and read plugins)
    """

    callback: str = "Unknown"
