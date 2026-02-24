from gestura.input.event_buffer import EventBuffer
import pytest


class FakeClock:
    def __init__(self):
        self._time = 0.0

    def now(self):
        return self._time

    def advance(self, seconds: float):
        self._time += seconds


def test_sliding_window_basic():
    clock = FakeClock()
    buffer = EventBuffer(window=1.0, func_now=clock.now)

    buffer.add("a")  # t = 0
    assert buffer.snapshot() == ["a"]

    clock.advance(0.5)
    buffer.add("b")  # t = 0.5
    assert buffer.snapshot() == ["a", "b"]

    clock.advance(0.6)  # t = 1.1
    assert buffer.snapshot() == ["b"]

    clock.advance(1.0)
    assert buffer.snapshot() == []


def test_prune_on_add():
    clock = FakeClock()
    buffer = EventBuffer(window=1.0, func_now=clock.now)

    buffer.add("x")
    clock.advance(2.0)

    buffer.add("y")

    assert buffer.snapshot() == ["y"]


def test_empty_buffer():
    clock = FakeClock()
    buffer = EventBuffer(window=1.0, func_now=clock.now)

    assert buffer.snapshot() == []
    assert len(buffer) == 0


def test_exact_boundary():
    clock = FakeClock()
    buffer = EventBuffer(window=1.0, func_now=clock.now)

    buffer.add("a")
    clock.advance(1.0)

    assert buffer.snapshot() == ["a"]

    clock.advance(0.000001)
    assert buffer.snapshot() == []
