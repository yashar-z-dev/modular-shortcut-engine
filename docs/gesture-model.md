# Gesture Detection Model

Gesture detection in this engine is stateful, sequential, and time-aware.

Unlike simple displacement-based systems, this engine evaluates movement over time using a controlled state machine.

---

## Core Concepts

Gesture detection is built around five principles:

1. Sequential progression
2. Time-constrained evaluation
3. Perceptual delta accumulation
4. Direction-aware segmentation
5. Deterministic state transitions

---

## 1. Sequential State Machine

Each configured shortcut defines an ordered list of gesture conditions.

Example:

```
[
  {"axis": "y", "trend": "up", "min_delta": 100},
  {"axis": "x", "trend": "left", "min_delta": 400}
]
```

This means:

Step 1 must complete before Step 2 begins.

The engine maintains internal state:

- Current step index
- Accumulated delta for the active step
- Time window reference

Only when the active step is satisfied does the engine move to the next step.

If all steps complete within the allowed time window, the gesture is considered detected.

---

## 2. Time Window Model

Gesture detection is constrained by a configurable time window.

Default: **4 seconds**

If the sequence is not completed within this window:

- The gesture state resets
- Partial progress is discarded

Why time matters:

Human perception of gestures is inherently time-based.
Very slow movement should not trigger gestures.
Extremely delayed continuation should not complete sequences.

The engine evaluates movement over time, not just displacement.

---

## 3. Perceptual Delta Accumulation

Operating systems generate noisy mouse movement events.
Small jitters and micro-movements are common.

The engine applies controlled accumulation logic:

- Small jitter is ignored
- Net directional movement is accumulated
- Movement is interpreted holistically

This produces behavior aligned with human perception.

Example:

If a user intends to move 200px upward, minor fluctuations do not invalidate the gesture.

However, accumulation is bounded and predictable.
It is not a loose approximation.

---

## 4. Direction-Aware Segmentation

If significant movement occurs in the opposite direction:

- The current directional segment is broken
- Accumulation may reset or split into new segments

Example:

A 200px upward movement may be interpreted as:

- One 200px upward gesture
- Or two 100px upward segments
- Depending on directional interruptions

"Significant" opposite movement is defined relative to:

- Directional dominance
- Temporal proximity
- Configured thresholds

Minor jitter does not break a segment.
Noticeable directional reversal does.

---

## 5. Slow Movement Suppression

Extremely slow motion does not trigger gestures.

Why?

Because intentional gestures are typically deliberate and time-bound.

If movement speed falls below perceptual thresholds within the time window:

- Accumulation does not complete
- The gesture will not trigger

This prevents accidental triggers from passive mouse drift.

---

## 6. Reset Conditions

A gesture state resets when:

- Time window expires
- Sequence is invalidated
- Opposite directional break exceeds threshold
- Shortcut configuration changes (if reloaded externally)

Reset is deterministic and consistent.

---

## 7. Determinism

Given the same sequence of input events and timestamps:

The engine will always produce the same detection result.

There is no randomness.
There is no parallel evaluation.

Gesture detection is fully deterministic.

---

## Why This Model?

Naive displacement-based detection leads to:

- Unpredictable behavior
- Sensitivity to OS jitter
- False positives
- Poor human alignment

This engine uses:

- Controlled state progression
- Time-aware interpretation
- Structured accumulation logic

To balance:

Predictability  
Human perception  
Configurability

---

For threading and ordering details, see:

- `concurrency-model.md`
- `architecture.md`
