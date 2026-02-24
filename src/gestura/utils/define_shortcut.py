import time
from typing import Callable

from ..adapters.pynput_adapters.keyboard_listener import KeyboardListener
from ..utils.key_normalizer import KeyUtils
from gestura import KeyboardEvent

# ========== USEAGE ==========
class KeyCollector:
    def __init__(self, duration_seconds: float = 2.0, callback: Callable[[str], None] = lambda _: None):
        """
        Args:
            duration_seconds: listener timer
            callback: return real-time
        """

        self.duration_seconds = duration_seconds
        self.callback = callback

        self.collected_keys: list[str] = []

    # ----- Helpers -----
    def _handle_event(self, event: KeyboardEvent):
        """
        NOTE: if get error, use threading.

        def process():
        threading.Thread(target=process, daemon=True).start()
        """
        if event.press:
            raw_key = event.key
            parsed_key = KeyUtils.parse_key(key=raw_key, output_type="str")

            self.collected_keys.append(parsed_key)

            self.callback(parsed_key)

    # ----- Start -----
    def start(self) -> list[str]:
        """
        Start listening to keyboard events for a fixed duration and return the list of parsed keys.
        """

        handler = KeyboardListener(self._handle_event)
        handler.start()

        self.callback("START: PRESS ANY KEY YOU WANT.")

        time.sleep(self.duration_seconds)
        handler.stop()

        time.sleep(0.1)

        return self.collected_keys


# ----- TESTS -----
if __name__ == "__main__":
    collector = KeyCollector(duration_seconds=2.0, callback=print)
    keys = collector.start()
    print(keys)



# # ========== USEAGE ==========
# def TEST_MouseListener():
#     import time

#     def _dispatch_event(event: EventData_move | EventData_click) -> None:
#         print(event)

#     listener = MouseListener(_dispatch_event, 2)
#     listener.start()
#     print("TEST Start, move or click with your mouse. (5second)")
#     time.sleep(5)
#     listener.stop()


# # ----- TESTS -----
# if __name__ == "__main__":
#     TEST_MouseListener()



# # # 100/100
# # """
# # Docstring for API_listener.listener_mouse
# # TODO: skip negegive values
# #     we can calculate max value for X and Y and skip that.
# #     or normalized (e.g. x = -34 => 0, x = 2000 => max(monitor))

# # TODO: _event_id
# #     we can delete, trusted input is sequenses
# # """

# # from typing import Callable, Optional

# # from pynput import mouse

# # from ...models.event import EventData_click, EventData_move


# # class MouseListener:
# #     def __init__(self, on_event_callback: Callable[[EventData_click | EventData_move], None], rate: int) -> None:
# #         """
# #         on_event_callback: function called for every mouse event
# #         """

# #         self.on_event_callback = on_event_callback
# #         self.listener: Optional[mouse.Listener] = None
# #         self._event_id: int = 0  # incremental id for move events
# #         self._counter: int = 0  # keep uniq self._event_id
# #         self._rate: int = rate  # skip rate: e.g. 2 -> frame/2

# #         # -------------- Mouse Move --------------
# #     def _on_move(self, x: int, y: int) -> None:
# #         # --------- skip negegive values ---------
# #         if x < 0 or y < 0:
# #             return None

# #         # -------------- skip rate --------------
# #         self._counter += 1
# #         if self._counter % self._rate == 0:
# #             event = EventData_move(
# #                 id = self._event_id,
# #                 x = x,
# #                 y = y
# #             )
# #             self._event_id += 1
# #             self.on_event_callback(event)

# #     # -------------- Mouse Click --------------
# #     def _on_click(self, x: int, y: int, button: mouse.Button, press: bool) -> None:
# #         event = EventData_click(
# #             press = press,
# #             position = button.name,
# #             x = x,
# #             y = y
# #         )
# #         self.on_event_callback(event)

# #     # -------------- Start Listener --------------
# #     def start(self) -> None:
# #         if self.listener is None:
# #             self.listener = mouse.Listener(
# #                 on_move=self._on_move,
# #                 on_click=self._on_click
# #             )
# #             self.listener.start()

# #     # -------------- Stop Listener --------------
# #     def stop(self) -> None:
# #         if self.listener is not None:
# #             self.listener.stop()
# #             self.listener.join()
# #             self.listener = None


# # # ========== USEAGE ==========
# # def TEST_MouseListener():
# #     import time

# #     def _dispatch_event(event: EventData_move | EventData_click) -> None:
# #         print(event)

# #     listener = MouseListener(_dispatch_event, 2)
# #     listener.start()
# #     print("TEST Start, move or click with your mouse. (5second)")
# #     time.sleep(5)
# #     listener.stop()


# # # ----- TESTS -----
# # if __name__ == "__main__":
# #     TEST_MouseListener()