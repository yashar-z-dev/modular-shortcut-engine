# Adapter Layer Design

This document defines the exact contract an adapter must satisfy
when emitting events to the engine.

Unlike many systems that use generic dictionaries,
this engine requires strict dataclass-based events.

---

## 1. Required Event Types

Adapters MUST construct and emit the following immutable dataclasses.

### KeyboardEvent

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class KeyboardEvent:
    key: str
    press: bool
```

- `key` → normalized key identifier (e.g. "ctrl", "a")
- `press` → True for key down, False for key up

---

### MouseEvent

```python
@dataclass(frozen=True, slots=True, kw_only=True)
class MouseEvent:
    x: int
    y: int
    position: Optional[str] = None
    press: Optional[bool] = None
```

- `x` → absolute cursor X coordinate
- `y` → absolute cursor Y coordinate
- `position` → optional semantic region (if adapter provides it)
- `press` → optional button state (True/False)

Important:

x and y represent absolute cursor position,
NOT delta from previous movement.

---

## 2. Why Absolute Coordinates?

The engine is responsible for:

- Calculating deltas
- Accumulating perceptual movement
- Determining dominant axis
- Detecting trend (left/right/up/down)
- Building segments
- Evaluating gesture progression

Example input sequence received by the engine:

(x=444, y=144)
(x=445, y=144)
(x=447, y=144)
...
(x=544, y=144)

Although many small movements occur,
the engine interprets them as:

min_delta=100  
axis="x"  
trend="right"

No segment is created for Y,
because Y did not meaningfully change.

This transformation from raw micro-movements
to semantic segments
is entirely the engine’s responsibility.

The adapter must NOT attempt to compute deltas
or detect gestures.

---

## 3. Mouse Click & Scroll Behavior (Current Version)

In the current version:

- Mouse click handling is optional
- Scroll events are not integrated into gesture logic
- Adapters may ignore scroll entirely

Future versions may extend MouseEvent
to integrate scroll-based gestures,
but this is not part of the current contract.

---

## 4. Ordering Guarantees

Adapters must ensure:

- Events are emitted in chronological order
- No reordering occurs
- Events are not mutated after creation

The engine assumes ordered event delivery.

---

## 5. Thread Ownership

Adapter:

- Owns OS interaction
- Owns listener threads
- Constructs dataclass instances
- Pushes them into the engine queue

Engine:

- Owns worker thread
- Computes deltas
- Builds segments
- Evaluates gestures
- Applies policy
- Emits callbacks

There is no shared mutable state between adapter and engine.

---

## 6. Adapter Responsibilities Summary

The adapter is responsible only for:

- Capturing OS input
- Normalizing key names
- Providing absolute mouse coordinates
- Constructing immutable event objects
- Pushing them into the engine queue

The adapter must NOT:

- Compute deltas
- Accumulate movement
- Detect direction
- Apply cooldown logic
- Evaluate gestures

All behavioral intelligence belongs to the engine.

---

## 7. Design Philosophy

Core = interpretation  
Adapter = translation

The adapter translates raw OS events into
strict immutable data structures.

The engine interprets those structures
into meaningful human gestures.

Separation is deliberate and strict.
