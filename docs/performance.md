# Performance Characteristics

This document explains the runtime behavior, latency model,
and computational characteristics of the engine.

The system was designed for real-time input processing
without polling or artificial delays.

---

## 1. Event-Driven Execution Model

The engine does not use polling.

Instead:

- Input listeners push normalized events into a queue
- The worker blocks on queue.get()
- Processing occurs only when new events arrive

This guarantees:

- Zero CPU usage when idle
- No interval-based latency
- Immediate reaction to input

Latency is therefore bounded only by:

- OS input dispatch
- Queue transfer time
- Worker processing time

---

## 2. Thread Model Overview

The default adapter (based on pynput) creates:

- One thread for keyboard listening
- One thread for mouse listening

The engine itself creates:

- One dedicated worker thread

So the runtime model is:

Keyboard Thread
Mouse Thread
→ Shared Queue
→ Worker Thread
→ Application callback dispatch

No additional background threads are spawned.

The worker is single-threaded by design
to preserve deterministic state progression.

---

## 3. Processing Complexity

For each incoming event:

- Gesture matching iterates through configured gestures
- Segment progression is O(1)
- State reset is constant time

Overall per-event complexity:

O(G)

Where G = number of registered gestures.

In practical usage:

- G is small
- Event processing cost is negligible
- Latency remains imperceptible to users

---

## 4. Latency Characteristics

Latency depends on:

- OS event delivery
- Python scheduling
- Queue transfer time
- Worker computation

Since:

- No polling interval exists
- No artificial batching occurs

The engine processes events immediately.

Typical reaction time is in the millisecond range
under normal system load.

Human perception threshold for UI interaction
is significantly higher than this range.

---

## 5. Memory Usage

The engine maintains:

- Gesture configuration structures
- Current segment state
- Recent delta accumulation

There is:

- No unbounded buffering
- No event history retention
- No background caching

Memory footprint scales only with:

- Number of registered gestures
- Current in-progress state

---

## 6. Why Not Parallel Gesture Evaluation?

Parallel evaluation would require:

- Shared state locking
- Coordination of time windows
- Synchronization barriers

Given that:

- Input rate is human-limited
- Processing cost is minimal

Parallelism would increase complexity
without meaningful performance benefit.

Single-threaded state evaluation ensures:

- Deterministic progression
- No race conditions
- Easier reasoning

---

## 7. Behavior Under High Event Volume

Under extreme mouse movement rates:

- Events are queued
- Worker processes sequentially

If event rate exceeds processing rate:

- Queue growth occurs temporarily
- No data loss happens
- Order is preserved

Because gesture detection is lightweight,
this situation is unlikely under normal human usage.

---

## 8. Cooldown and Policy Impact

Cooldown logic:

- Executes in constant time
- Does not affect detection latency
- Only affects emission decision

Detection and emission remain decoupled.

---

## 9. Idle Cost

When no input is occurring:

- Worker blocks
- CPU usage is effectively zero
- No timers wake the system

This makes the engine suitable for:

- Background services
- Desktop applications
- Long-running processes

---

## Performance Philosophy

The engine prioritizes:

- Immediate reaction over scheduled checks
- Determinism over speculative parallelism
- Minimal background activity
- Linear, predictable cost

It is designed to be lightweight enough
to run continuously without measurable system impact.
