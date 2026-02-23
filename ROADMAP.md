# Roadmap

This document outlines the long-term direction of the engine.

It is not a release schedule.
It is a technical vision.

The project aims to evolve into a robust,
cross-platform gesture and shortcut runtime.

---

# Guiding Principles

All future development must preserve:

- Deterministic behavior
- Clear separation of adapter and core
- No polling
- Single-threaded state evaluation
- OS independence of core logic

Evolution must extend the engine,
not complicate it.

---

# Short-Term Expansion

## 1. Mouse Click Integration

Current version:

- Click events are optional
- Not integrated into gesture evaluation

Planned:

- Click-based gesture segments
- Button-aware gesture matching
- Configurable press / release detection

---

## 2. Scroll Gesture Support

Planned support for:

- Scroll-based gestures
- Vertical / horizontal scroll recognition
- Scroll direction as segment input

This requires extending MouseEvent
without breaking backward compatibility.

---

## 3. Keyboard Release Semantics

Current version:

- KeyboardEvent supports press boolean
- Engine primarily reacts to press

Planned:

- Explicit release-based gestures
- Press+Release sequence patterns
- Hold detection support

---

# Mid-Term Evolution

## 4. Ordered vs Unordered Gesture Matching

Current version:

- Sequence order matters

Planned:

- Configurable ordered / unordered evaluation
- Modifier + movement style gestures
- Example:
  hold ctrl + move 20px up

This will require extending worker logic
while preserving deterministic evaluation.

---

## 5. Modifier-Aware Gesture Layer

Support composite gestures like:

- Ctrl + Move Up
- Shift + Drag
- Hold + Directional motion

Requires:

- Persistent key state tracking
- Temporal overlap detection
- Extended segment state model

---

# Adapter Ecosystem Expansion

The adapter layer is currently the most complex integration surface.

Future goals:

## 6. Official Multi-Backend Adapters

Potential adapters:

- Windows Raw Input
- Linux evdev
- macOS Quartz
- Web-based event bridge
- Headless synthetic event adapter (for testing)

Goal:
Developers should not need to research
OS-level input handling themselves.

---

## 7. Key Normalization Layer Improvements

Challenges:

- OS-specific key naming
- Keyboard layout dependence
- Language-based mapping issues (e.g. pynput)
- Right/Left modifier ambiguity

Planned direction:

- Strong internal key normalization strategy
- Layout-aware mapping layer
- Extended alias resolution
- Extensive automated test coverage

Important:
Adapters must always emit normalized str keys.
Core performs internal unification
(e.g. ctrl_r → ctrl).

---

## 8. Adapter Documentation & Recommendations

Because input libraries vary in reliability:

- Comparative documentation may be added
- Known limitations documented per OS
- Suggested best-practice adapters provided

Goal:
Reduce friction for developers integrating the engine.

---

# Long-Term Vision

## 9. Gesture Debugging & Visualization Tools

Potential additions:

- Segment trace logging
- Real-time gesture visualizer
- Development-mode debug output

This would help:

- Tuning min_delta
- Debugging false positives
- Validating gesture design

---

## 10. Performance Benchmark Suite

Although the engine is lightweight,
formal benchmarking would:

- Validate scaling behavior
- Provide regression protection
- Strengthen engineering credibility

---

## 11. Configuration Schema & Validation

Possible improvements:

- Formal config schema definition
- Static validation tools
- Linting utilities

---

# Contribution Areas

The project particularly welcomes contributions in:

- Adapter implementations
- Key normalization research
- Cross-platform testing
- Scroll and click gesture design
- Documentation improvements
- Benchmarking and profiling

---

# What This Engine Will Not Become

It will not:

- Become a GUI framework
- Own application lifecycle
- Embed UI rendering
- Implement OS hooks in core
- Become polling-based

The engine remains:

A deterministic input interpretation runtime.

---

# Closing Vision

The goal is not just to detect gestures.

The goal is to provide a predictable,
portable,
architecturally clean
input runtime
that developers can trust
across platforms.
