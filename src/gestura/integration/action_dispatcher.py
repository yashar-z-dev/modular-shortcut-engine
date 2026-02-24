import logging
import inspect

from typing import Any, Optional, Type, Callable
from .models import LogicResult, CallbackConfig, LogicProtocol, ActionProtocol, T, C

# ==============================
# Registry with helper and introspection
# ==============================
class ActionDispatcher:
    """
    Central registry for callbacks.
    Uses introspection to dynamically instantiate Logic/Action
    without manually specifying dependencies.
    """

    def __init__(
            self,
            dependency_mapping: dict[str, object],
            dispatcher_ui: Callable[[dict[str, str]], None],
            # event_overlay: Callable[[OverlayState], None]
            ):
        # Mapping of callback key -> CallbackConfig
        self._registry: dict[str, CallbackConfig[Any]] = {}

        # Mapping of dependency name -> actual object
        # This will be used by introspection to inject dependencies
        self.dependency_mapping = dependency_mapping

        # Send State to UI
        self.dispatcher_ui = dispatcher_ui
        # self.event_overlay = event_overlay

    def register(
        self,
        key: str,
        logic: Type[LogicProtocol[T]],
        action: Type[ActionProtocol[T]],
        status: bool = True,
        notification: bool = True,
    ):
        """
        Helper to register a callback in a concise way.

        Example:
            registry.register_callback("pause", LogicPause, ActionPause)
        """
        self._registry[key] = CallbackConfig(
            logic=logic,
            action=action,
            status=status,
            notification=notification,
        )

    def get(self, key: str) -> Optional[CallbackConfig[Any]]:
        return self._registry.get(key)

    # ===== Dynamic instantiation =====
    def _instantiate(self, cls: Type[C]) -> C:
        sig = inspect.signature(cls.__init__)
        param_names = [
            p.name for p in sig.parameters.values()
            if p.name != "self"
        ]
        args = [self.dependency_mapping[name] for name in param_names]
        return cls(*args)

    # ===== Callback execution =====
    def execute_callback(self, cb_key: str):
        """
        Executes a callback: instantiate Logic, run it, instantiate Action, run it,
        and optionally dispatch status/notification to UI.
        """
        config = self.get(cb_key)
        if not config:
            logging.info(f"[CallbackRegistry] Unknown callback: {cb_key}")
            return

        # Send to UI befor execute(fast feedback to UI)
        # self._emit_UI(cb_key)

        # ===== Logic =====
        logic_instance: LogicProtocol[Any] = self._instantiate(config.logic)
        result: LogicResult[Any] = logic_instance.execute()

        # ===== UI updates =====
        logging.info(f"Execute: {cb_key}, state: {result.ui_message}")
        if config.status:
            # Example: {"type": "status", "payload": "Paused state"}
            self.dispatcher_ui({"type": "status", "payload": result.ui_message})

        if config.notification:
            # Example: {"type": "notification_success", "message": "Paused state"}
            self.dispatcher_ui({"type": "notification_success", "message": result.ui_message})

        # ===== Action =====
        action_instance = self._instantiate(config.action)
        action_instance.execute(result.payload)

    # ------------------------------------------------------------------
    # Emit logic
    # ------------------------------------------------------------------

    # def _emit_UI(self, cb_key: str) -> None:
    #     logging.debug(f"Triggered: {cb_key}")

    #     # UI Update[UX] no execute.
    #     if cb_key == "pause":
    #         self.event_overlay(OverlayState.PAUSED)
    #     else:
    #         self.event_overlay(OverlayState.TRIGGERED)
