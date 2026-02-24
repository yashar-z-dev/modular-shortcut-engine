from collections import deque
import time
from typing import Deque, Any, Callable


class EventBuffer:
    def __init__(self, window: float, func_now: Callable[[], float] = time.monotonic):
        self.window = window
        self.func_now = func_now
        self._buffer: Deque[tuple[float, Any]] = deque()

    def _prune(self, now: float) -> None:
        cutoff = now - self.window
        buf = self._buffer
        while buf and buf[0][0] < cutoff:
            buf.popleft()

    def add(self, event: Any) -> None:
        now = self.func_now()
        self._prune(now)
        self._buffer.append((now, event))

    def snapshot(self) -> list[Any]:
        now = self.func_now()
        self._prune(now)
        return [e for _, e in self._buffer]

    def clear(self) -> None:
        self._buffer.clear()

    def __len__(self) -> int:
        now = self.func_now()
        self._prune(now)
        return len(self._buffer)
