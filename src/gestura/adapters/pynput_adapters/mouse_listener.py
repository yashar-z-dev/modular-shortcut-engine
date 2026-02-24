from typing import Callable, Optional
from pynput import mouse
from ...models.inputs import MouseEvent, MouseClickEvent, MouseMoveEvent


class MouseListener:
    def __init__(
            self,
            on_event: Callable[[MouseEvent], None],
        ) -> None:
        """
        Args:
            on_move: call with (x: int, y: int)
            on_click: call with (x: int, y: int, button.name: mouse.Button, press: bool)
        """

        self.on_event = on_event

        self.listener: Optional[mouse.Listener] = None

    # -------------- Mouse Move --------------
    def _on_move(self, x: int, y: int) -> None:
        self.on_event(MouseMoveEvent(x=x, y=y))

    # -------------- Mouse Click --------------
    def _on_click(self, x: int, y: int, button: mouse.Button, press: bool) -> None:
        self.on_event(MouseClickEvent(x=x, y=y,position=button.name, press=press))

    # -------------- Start Listener --------------
    def start(self) -> None:
        if self.listener is None:
            self.listener = mouse.Listener(
                on_move=self._on_move,
                on_click=self._on_click
            )
            self.listener.start()

    # -------------- Stop Listener --------------
    def stop(self) -> None:
        if self.listener is not None:
            self.listener.stop()
            self.listener.join()
            self.listener = None
