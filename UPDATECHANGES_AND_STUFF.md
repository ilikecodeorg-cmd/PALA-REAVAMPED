VERSION 0.1.8
build(ai): anti-stagnation model architecture, telemetry hooks, and edge constraints

- Added anti-stagnation logic in pong_terminal.py to counter policy network freezing.
- Calibrated severe penalty functions for top/bottom edge collisions (-100.0).
- Fixed tensor gradient decay to stabilize adaptive exploration at Epsilon 0.100.
- Implemented real-time tracking for Intel Core i3-1115G4 architecture metrics.
