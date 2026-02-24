def main():
    from typing import Any
    import logging
    import time
    from gestura import GesturaEngine, ActionEvent

    logging.basicConfig(level=logging.INFO)

    DEFAULT_POLICY = {
        "cooldown_seconds": 1.0,
        "max_triggers": 1,
        "rate_window_seconds": 5.0
    }
    config: list[dict[str, Any]] = [
        {
            "keyboard": {"conditions": ["esc"]},
            "mouse": {"conditions": []},
            "policy": DEFAULT_POLICY,
            "callback": "exit"
        },
        {
            "keyboard": {"conditions": []},
            "mouse": {
                "conditions": [
                    {"axis": "y", "trend": "up", "min_delta": 100},
                    {"axis": "x", "trend": "left", "min_delta": 400},
                ]
            },
            "policy": {
                **DEFAULT_POLICY,
                "cooldown_seconds": 2.0
            },
            "callback": "mouse_up_100_then_left_400"
        },
        {
            "keyboard": {"conditions": ["ctrl"]},
            "mouse": {
                "conditions": [
                    {"axis": "y", "trend": "down", "min_delta": 20}
                ]
            },
            "policy": {
                **DEFAULT_POLICY,
                "cooldown_seconds": 2.0
            },
            "callback": "ctrl_plus_mouse_down_20"
        },
    ]

    running = True

    def handle_event(event: ActionEvent):
        nonlocal running
        logging.info(f"🔥 Triggered → {event.callback}")

        if event.callback == "exit":
            running = False

    print("\nShortcut Engine Demo")
    print("-" * 30)
    print("1. Press ESC → exit")
    print("2. Move mouse UP 100px then LEFT 400px → trigger #2")
    print("3. CTRL + move mouse DOWN 20px (within 5 seconds, order doesn't matter) → trigger #3")
    print("-" * 30)
    print("Perform gestures now...\n")

    engine = GesturaEngine(config, handle_event)

    engine.start()

    while running:
        time.sleep(0.01)

    print("\nEngine stopped.")