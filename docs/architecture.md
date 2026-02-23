# Architecture Overview

The engine is designed as a layered, deterministic, event-driven system.

It separates detection, policy control, and execution responsibilities into distinct layers.

The core engine contains no OS-specific logic.

---

## High-Level Flow

```
OS Input
   ↓
Adapter Layer
   ↓
Event Queue (Blocking)
   ↓
Worker Thread
   ↓
Gesture State Machine
   ↓
Policy Engine
   ↓
Callback Publish
   ↓
Application Layer
```

---

## Layer Responsibilities

### 1. Adapter Layer

- Translates OS-specific events into normalized `KeyboardEvent` and `MouseEvent`
- Handles OS noise and platform quirks
- Runs in adapter-managed threads
- Pushes normalized events into the engine queue

The adapter is replaceable.  
The core engine does not depend on any specific OS or library.

---

### 2. Event Queue

- Thread-safe blocking queue
- Prevents polling
- Preserves event order
- Decouples listeners from processing logic

This ensures deterministic event sequencing.

---

### 3. Worker Thread

- Single dedicated processing thread
- Sequential event handling
- No parallel gesture evaluation
- Deterministic ordering guarantee

Why single worker?

Because gesture detection is stateful.  
Parallel processing would introduce race conditions and path inconsistency.

---

### 4. Gesture State Machine

- Maintains per-shortcut detection state
- Evaluates sequential gesture conditions
- Resets on timeout or invalidation
- Time-aware progression logic

Detailed behavior is described in `gesture-model.md`.

---

### 5. Policy Engine

- Applies cooldown
- Applies rate window limits
- Prevents spam triggers
- Isolated from detection logic

Detection determines _what happened_.
Policy determines _whether it should emit a signal_.

---

### 6. Callback Publishing

The engine does not execute user logic.

It only publishes callback keys.

Execution scheduling is fully controlled by the application layer.

---

## Architectural Principles

### Detection ≠ Execution

The engine never calls user logic internally.

### Core ≠ OS

The core engine contains only algorithmic logic.

### Sequential Determinism

Event order is preserved.
Callback publish order matches detection order.

### No Polling

The engine uses blocking queue semantics.
CPU usage scales with event volume.

---

## Why This Architecture?

Mouse gesture detection is inherently stateful and time-dependent.

To maintain:

- Predictability
- Determinism
- Testability
- Clear separation of concerns

A single-worker, layered model was chosen.

---

For detailed gesture behavior, see:

- `gesture-model.md`
- `concurrency-model.md`
- `design-decisions.md`
