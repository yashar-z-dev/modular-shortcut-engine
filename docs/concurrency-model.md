# Concurrency Model

The engine uses a minimal, controlled threading model designed for:

- Determinism
- Safety
- Predictability
- Clear separation of responsibilities

It does not rely on polling.
It does not execute user logic internally.

---

## Thread Topology

Typical runtime structure:

```
Keyboard Listener Thread  ┐
                           ├─> Blocking Event Queue ──> Worker Thread ──> Callback Publish
Mouse Listener Thread     ┘
```

---

## 1. Adapter Threads

The adapter layer (e.g., a `pynput`-based implementation) runs:

- One keyboard listener thread
- One mouse listener thread

These threads:

- Normalize raw OS events
- Convert them into `KeyboardEvent` / `MouseEvent`
- Push them into the engine’s blocking queue

The core engine does not manage these threads directly.
They are adapter-controlled.

---

## 2. Blocking Event Queue

The queue:

- Is thread-safe
- Preserves event order
- Blocks when empty (no polling)
- Decouples input capture from processing

Why blocking?

Because gesture detection should scale with event volume, not CPU cycles.

No busy loops.
No interval polling.

---

## 3. Worker Thread

The engine starts a single worker thread when `engine.start()` is called.

This thread:

- Consumes events sequentially
- Runs gesture detection logic
- Applies policy checks
- Publishes callback keys

There is no parallel gesture evaluation.

Why single worker?

Because gesture detection is stateful and time-dependent.
Parallel processing would introduce race conditions and inconsistent path evaluation.

---

## 4. Deterministic Ordering Guarantee

Event order is preserved from:

Adapter → Queue → Worker → Callback Publish

Therefore:

- If Event A occurs before Event B,
- And both trigger callbacks,

Callback A will be published before Callback B.

This guarantee holds under normal operation.

---

## 5. Callback Execution Responsibility

Important:

The engine does **not** execute user callbacks inside the worker thread.

It only publishes callback identifiers.

Execution scheduling is the responsibility of the application layer.

This avoids:

- UI thread violations
- Deadlocks
- Hidden concurrency bugs
- Forced execution models

---

## 6. Why Not Multiple Workers?

Multiple workers would require:

- Locking gesture state
- Synchronizing sequence progression
- Coordinating time-window logic

This would:

- Increase complexity
- Risk race conditions
- Reduce determinism

Since gesture detection is lightweight and event-driven,
a single worker provides sufficient throughput for real-world usage.

---

## 7. Thread Safety Characteristics

- Input threads only push to queue
- Worker thread owns gesture state
- No shared mutable gesture state across threads
- Minimal locking (queue only)

This model reduces synchronization complexity.

---

## 8. Shutdown Behavior

On shutdown:

- Adapter listeners stop producing events
- Worker thread exits gracefully
- Remaining queued events may be drained (implementation-dependent)

No abrupt termination of gesture state occurs mid-processing.

---

## Design Summary

The concurrency model prioritizes:

- Deterministic behavior
- Controlled complexity
- Clear responsibility boundaries
- Predictable execution flow

It is intentionally simple.

For architectural overview, see:

- `architecture.md`
