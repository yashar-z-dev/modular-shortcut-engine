# Design Decisions

This document explains the reasoning behind major architectural choices.

The engine was not designed for minimal code size.
It was designed for clarity, determinism, and behavioral predictability.

---

## 1. Why Separate Detection From Execution?

Many shortcut libraries immediately execute callbacks upon detection.

This engine does not.

Reasons:

- UI frameworks often require main-thread execution
- Async systems require event-loop integration
- Games use custom update loops
- Background services may batch signals

By publishing callback identifiers instead of executing logic:

- The engine remains scheduling-neutral
- The application retains control
- No implicit threading assumptions are made

Detection determines _what happened_.  
The application decides _what to do about it_.

---

## 2. Why A Single Worker Thread?

Gesture detection is:

- Stateful
- Sequential
- Time-dependent

Parallel processing would require:

- Locking shared gesture state
- Synchronizing sequence progression
- Coordinating time windows

This increases complexity and risks race conditions.

A single worker:

- Guarantees deterministic ordering
- Eliminates state contention
- Keeps reasoning simple

Since detection is lightweight and event-driven,
parallelism is unnecessary for real-world usage.

---

## 3. Why Time-Aware Gesture Detection?

Human perception of motion is time-bound.

Without time constraints:

- Extremely slow movement could trigger gestures
- Partial sequences could complete long after intention
- Accidental drift could produce false positives

The engine evaluates gestures within a configurable time window
(default: 4 seconds).

Movement must be deliberate and temporally coherent.

---

## 4. Why Perceptual Delta Accumulation?

Operating systems generate noisy mouse movement data.

Naive accumulation leads to:

- Over-sensitivity to jitter
- Unstable direction changes
- Non-human-aligned behavior

The engine uses controlled accumulation logic:

- Minor jitter is ignored
- Directional dominance is respected
- Significant reversal breaks the segment

This aligns gesture detection with human visual interpretation,
while maintaining deterministic behavior.

---

## 5. Why Not Polling?

Polling-based systems:

- Waste CPU cycles
- Introduce artificial latency
- Depend on interval tuning

This engine uses:

- Blocking queue semantics
- Event-driven progression

Processing cost scales with event volume,
not with idle time.

---

## 6. Why Is Policy Separate From Detection?

Cooldown and rate limiting are behavioral constraints,
not structural properties of gestures.

Mixing them would:

- Complicate state logic
- Reduce testability
- Introduce hidden timing interactions

Separation ensures:

- Clean detection logic
- Isolated emission control
- Independent test coverage

---

## 7. Why Is The Core OS-Agnostic?

Gesture detection is purely algorithmic.

OS interaction introduces:

- Platform variability
- Testing difficulty
- External dependencies

By isolating OS concerns in adapters:

- The core remains portable
- The engine remains testable
- Alternative adapters can be implemented

The only contract is normalized event objects.

---

## 8. Why Determinism Matters

Given the same:

- Input event sequence
- Event timestamps
- Configuration

The engine will always produce the same output.

No randomness.
No race conditions.
No hidden background processing.

Determinism enables:

- Reliable unit testing
- Predictable integration
- Easier debugging

---

## 9. Why Not A Framework?

The engine does not:

- Own application lifecycle
- Force execution model
- Control threading of user logic
- Manage dependency injection internally

It intentionally avoids becoming a framework.

It is an input runtime layer,
not an application container.

---

## Design Philosophy Summary

The engine prioritizes:

- Predictability over cleverness
- Separation over convenience
- Determinism over parallelism
- Control over automation

It is intentionally minimal in scope,
but precise in behavior.
