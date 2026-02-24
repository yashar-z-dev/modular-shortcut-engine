import threading
import queue

from ..models.policy import ActionEvent


class ActionBus:
    def __init__(self, maxsize: int = 1000):
        self._queue: queue.Queue[str] = queue.Queue(maxsize=maxsize)
        self._lock = threading.Lock()

    def publish(self, action: ActionEvent) -> None:
        with self._lock:
            if self._queue.full():
                try:
                    self._queue.get_nowait() # drop oldest
                except queue.Empty:
                    pass
            self._queue.put_nowait(action.callback) # str

    def drain(self) -> list[str]:
        actions: list[str] = []
        while True:
            try:
                actions.append(self._queue.get_nowait())
            except queue.Empty:
                break
        return actions
