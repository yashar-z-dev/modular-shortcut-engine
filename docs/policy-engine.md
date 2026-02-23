# Policy Engine

The Policy Engine is responsible for controlling _when_ a detected gesture
is allowed to emit a callback.

It is intentionally isolated from gesture detection logic.

Detection answers:

> "Did this gesture happen?"

Policy answers:

> "Should we emit a signal for it right now?"

---

## Why Separate Policy From Detection?

Gesture detection determines structural correctness.

Policy determines behavioral constraints.

If combined, the system would:

- Mix time-window logic with cooldown logic
- Become harder to test
- Become harder to reason about
- Risk subtle timing bugs

By separating them:

- Detection remains deterministic
- Policy remains configurable
- Each layer has a single responsibility

---

## Supported Policy Controls

Each shortcut can define its own policy:

```python
{
    "cooldown_seconds": 1.0,
    "max_triggers": 1,
    "rate_window_seconds": 5.0
}
```

---

## 1. Cooldown

After a callback is emitted:

- The shortcut enters a cooldown period
- Additional detections are ignored
- Cooldown is measured using the engine's time source

This prevents rapid re-triggering.

---

## 2. Rate Window

Defines a sliding time window.

Example:

- `rate_window_seconds = 5`
- `max_triggers = 1`

Within any 5-second window,
only one trigger is allowed.

Additional detections are suppressed.

---

## 3. Max Triggers

Controls how many times a shortcut may fire within a rate window.

Example:

- `max_triggers = 3`
- `rate_window_seconds = 10`

Up to 3 emissions are allowed within 10 seconds.

After that, further detections are blocked until the window advances.

---

## Policy Evaluation Flow

When a gesture completes:

1. Detection layer signals completion
2. Policy engine evaluates:
   - Is cooldown active?
   - Is rate limit exceeded?

3. If allowed:
   - Callback key is published

4. If blocked:
   - Detection result is discarded silently

Policy does not modify gesture state.

It only decides whether emission is permitted.

---

## Deterministic Behavior

Policy evaluation uses:

- Injected time source
- Stored emission timestamps
- Predictable window arithmetic

Given identical input and time values,
policy decisions are deterministic.

---

## Interaction With Gesture Time Window

Important distinction:

- Gesture time window controls _detection validity_
- Policy cooldown controls _emission frequency_

They operate independently.

A gesture may be detected multiple times,
but policy may suppress emission.

---

## Why Not Auto-Reset On Cooldown?

The engine does not alter detection logic based on cooldown.

Cooldown only blocks emission,
not detection progression.

This keeps detection logic pure and predictable.

---

## Testing

Because time is injectable:

- Cooldown logic can be simulated
- Rate windows can be tested deterministically
- No reliance on real system clock is required

---

## Design Summary

The Policy Engine exists to:

- Prevent spam
- Provide behavioral throttling
- Keep gesture detection clean
- Maintain architectural separation

Detection determines structure.
Policy determines frequency.
