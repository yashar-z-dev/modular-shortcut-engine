# 100/100
"""
__all__ = (
    _BaseGestureMouse, Axis_X, Axis_Y, GestureMouseValidator, GestureMouseAdapter, 
    GestureMouse, GestureMouseCondition, TEST_GestureMouse, Test_GestureMouseCondition
    )
"""

# NOTE: CPU 4% USE

from typing import Literal, Union, Annotated, overload, Iterable, Any
from pydantic import BaseModel, Field, TypeAdapter, ConfigDict


# ========== Base models ==========
class _BaseGestureMouse(BaseModel):
    """
    Base Mouse Gesture

    NOTE: Valid Data: Union[Axis_X, Axis_Y].

    :param min_delta: Minimum move size(e.g. From a position of 200 pixels to 400 pixels is equal to a minimum delta of 200.)
    """

    model_config = ConfigDict(extra="forbid")

    min_delta: int


class Axis_X(_BaseGestureMouse):
    """
    :param axis: Axis of motion
    :param trend: up or down ("-" or "+")
    :param left: oprator `-`
    :param right: oprator `+`
    """
    axis: Literal["x"] = "x"
    trend: Literal["left", "right"]


class Axis_Y(_BaseGestureMouse):
    """
    :param axis: Axis of motion
    :param trend: up or down ("-" or "+")
    :param up: oprator `-`
    :param down: oprator `+`
    """
    axis: Literal["y"] = "y"
    trend: Literal["up", "down"]


# ===== Validators =====
GestureMouseValidator = Annotated[
    Union[Axis_X, Axis_Y],
    Field(discriminator="axis"),
]

GestureMouseAdapter: TypeAdapter[GestureMouseValidator] = TypeAdapter(GestureMouseValidator)
GestureMouseListAdapter = TypeAdapter(list[GestureMouseValidator])


# ========== Container model ==========
class GestureMouse(BaseModel):
    """ 
    Model structure for Mouse Gesture.
    
    :param conditions: List of GestureMouseValidator for Mouse Actions (e.g. [{axis="x", trend="left", min_delta=444}, {axis="y", trend="up", min_delta=444}])
    """

    model_config = ConfigDict(extra="forbid")

    conditions: list[GestureMouseValidator] = Field(default_factory=list)

    @overload
    def add_condition(
        self,
        *,
        axis: Literal["x"],
        trend: Literal["left", "right"],
        min_delta: int,
    ) -> Axis_X: ...

    @overload
    def add_condition(
        self,
        *,
        axis: Literal["y"],
        trend: Literal["up", "down"],
        min_delta: int,
    ) -> Axis_Y: ...

    @overload
    def add_condition(
        self,
        data: Iterable[dict[str, Any] | GestureMouseValidator] | dict[str, Any],
    ) -> list[GestureMouseValidator]: ...

    # -------- private API --------
    def _normalize_input(self, data: object) -> list[GestureMouseValidator]:
        """
        Normalize ANY supported input into list[GestureMouseValidator]
        """
        if isinstance(data, dict) and "conditions" in data:
            data = data["conditions"]

        if isinstance(data, list | tuple):
            return GestureMouseListAdapter.validate_python(data)

        # single item
        return [GestureMouseAdapter.validate_python(data)]

    # -------- implementation --------
    def add_condition(
        self,
        data: object = None,
        **kwargs: object,
    ):
        if kwargs:
            cond = GestureMouseAdapter.validate_python(kwargs)
            self.conditions.append(cond)
            return cond

        conds = self._normalize_input(data)
        self.conditions.extend(conds)
        return conds

    # -------- alternative API --------
    def add(self, cond: GestureMouseValidator) -> None:
        """Append one WITHOUT validation"""
        self.conditions.append(cond)

    def extend(self, conds: Iterable[GestureMouseValidator]) -> None:
        """Append many WITHOUT validation"""
        self.conditions.extend(conds)

    # -------- helpers --------
    def x(self) -> list[Axis_X]:
        """
        :return: filter Axis_X
        :rtype: list[GestureMouseValidator]
        """

        return [c for c in self.conditions if isinstance(c, Axis_X)]

    def y(self) -> list[Axis_Y]:
        """
        :return: filter Axis_Y
        :rtype: list[GestureMouseValidator]
        """

        return [c for c in self.conditions if isinstance(c, Axis_Y)]


# ===== SHORTCUT JSON Mouse =====
class GestureMouseCondition(GestureMouse):
    """
    Define mouse gestures for the conditions required to trigger the action.

    :param callback: The name of the method to be executed when the gesture is triggered
    """

    callback: str = "Unknown"


# ===== Validators =====
GestureMouseConditionAdapter = TypeAdapter(list[GestureMouseCondition])

def Validator_GestureMouseCondition(
        data: list[dict[str, Any]]
    ) -> list[GestureMouseCondition]:
    """
    :param data: format GestureMouseCondition.

    :return: list[GestureMouseCondition]
    """

    return GestureMouseConditionAdapter.validate_python(data)
