# Adapter Layer Design (v2.0)

This document defines the exact contract an adapter must satisfy
when emitting events to the engine.

Unlike many systems that use generic dictionaries,
this engine requires strict dataclass-based events.

In v2.0, the internal ListenerManager layer was removed.
Multiplexing and shared listener management are now external concerns.

---

# 1. Required Event Types

Adapters MUST construct and emit the following immutable dataclasses.

## KeyboardEvent

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class KeyboardEvent:
    key: str
    press: bool
```

- `key` → normalized key identifier (e.g. "ctrl", "a")
- `press` → True for key down, False for key up

---

## MouseEvent

```python
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
```

- `x` → absolute cursor X coordinate
- `y` → absolute cursor Y coordinate
- `position` → semantic region (e.g. "left")
- `press` → button state (True/False)

Important:

`x` and `y` represent absolute cursor position,
NOT delta from previous movement.

---

# 2. Listener Contract (Factory Interface)

The engine does NOT depend on concrete listener implementations.

It only requires a factory with this minimal contract:

```python
class Listener(Protocol):
    def start(self) -> None: ...
    def stop(self) -> None: ...


class KeyboardListenerType(Protocol):
    def __call__(
        self,
        on_event: Callable[[KeyboardEvent], None],
    ) -> Listener: ...


class MouseListenerType(Protocol):
    def __call__(
        self,
        on_event: Callable[[MouseEvent], None],
    ) -> Listener: ...
```

The engine will:

- Call the factory
- Receive a listener instance
- Call `start()` on engine start
- Call `stop()` on engine stop

The engine does NOT manage multiple handlers internally.

---

# 3. Why Absolute Coordinates?

The engine is responsible for:

- Calculating deltas
- Accumulating perceptual movement
- Determining dominant axis
- Detecting trend (left/right/up/down)
- Building segments
- Evaluating gesture progression

Example input sequence received by the engine:

```
(x=444, y=144)
(x=445, y=144)
(x=447, y=144)
...
(x=544, y=144)
```

Although many small movements occur,
the engine interprets them as:

```
min_delta=100
axis="x"
trend="right"
```

No segment is created for Y,
because Y did not meaningfully change.

This transformation from raw micro-movements
to semantic segments
is entirely the engine’s responsibility.

The adapter must NOT attempt to compute deltas
or detect gestures.

---

# 4. Mouse Click & Scroll Behavior (Current Version)

In the current version:

- Mouse click handling is optional
- Scroll events are not integrated into gesture logic
- Adapters may ignore scroll entirely

Future versions may extend `MouseEvent`
to integrate scroll-based gestures,
but this is not part of the current contract.

---

# 5. Ordering Guarantees

Adapters must ensure:

- Events are emitted in chronological order
- No reordering occurs
- Events are not mutated after creation

The engine assumes ordered event delivery.

---

# 6. Thread Ownership

Adapter:

- Owns OS interaction
- Owns listener threads
- Constructs dataclass instances
- Pushes them into the engine callback

Engine:

- Owns worker thread
- Computes deltas
- Builds segments
- Evaluates gestures
- Applies policy
- Emits callbacks

There is no shared mutable state between adapter and engine.

---

# 7. Shared Listener Pattern (Advanced Usage)

Since v2.0, the engine no longer includes an internal manager
for multiplexing multiple handlers.

If an application needs a shared OS listener
that forwards events to multiple consumers,
it must implement this externally.

Example:

```python
class SharedKeyboardHub:
    """
    Multiplexes keyboard events to multiple handlers.
    """

    def __init__(self):
        self._handlers: list[Callable[[KeyboardEvent], None]] = []

    def register(self, handler):
        self._handlers.append(handler)
        return handler  # token

    def unregister(self, handler):
        self._handlers.remove(handler)

    def dispatch(self, event: KeyboardEvent):
        for h in list(self._handlers):
            h(event)


class SharedKeyboardAdapter:
    """
    Engine-compatible adapter that connects
    the engine to a shared hub.
    """

    def __init__(self, hub: SharedKeyboardHub, handler):
        self._hub = hub
        self._handler = handler
        self._token = None

    def start(self):
        self._token = self._hub.register(self._handler)

    def stop(self):
        if self._token is not None:
            self._hub.unregister(self._token)
            self._token = None


shared_keyboard = SharedKeyboardHub()

def shared_keyboard_factory(on_event):
    return SharedKeyboardAdapter(shared_keyboard, on_event)


engine = GesturaEngine(
    config,
    publish_action,
    keyboard_listener_factory=shared_keyboard_factory,
)
```

Important:

- The shared hub owns the OS listener lifecycle.
- The engine only registers/unregisters its handler.
- The engine does not control the shared listener's start/stop.

---

# 8. Adapter Responsibilities Summary

The adapter is responsible only for:

- Capturing OS input
- Normalizing key names
- Providing absolute mouse coordinates
- Constructing immutable event objects
- Forwarding them to the engine

The adapter must NOT:

- Compute deltas
- Accumulate movement
- Detect direction
- Apply cooldown logic
- Evaluate gestures
- Perform policy decisions

All behavioral intelligence belongs to the engine.

---

# 9. Design Philosophy

Core = interpretation
Adapter = translation

The adapter translates raw OS events into
strict immutable data structures.

The engine interprets those structures
into meaningful human gestures.

Separation is deliberate and strict.
