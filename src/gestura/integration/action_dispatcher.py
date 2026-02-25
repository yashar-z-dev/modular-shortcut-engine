import logging
import inspect

from typing import Any, Optional, Type
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
        ):
        # Mapping of callback key -> CallbackConfig
        self._registry: dict[str, CallbackConfig[Any]] = {}

        # Mapping of dependency name -> actual object
        # This will be used by introspection to inject dependencies
        self.dependency_mapping = dependency_mapping

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
    def execute_callback(self, cb_key: str) -> dict[str, str]:
        """
        Executes a callback: instantiate Logic, run it, instantiate Action, run it,
        and optionally dispatch status/notification to UI.
        """
        config = self.get(cb_key)
        if not config:
            logging.info(f"[CallbackRegistry] Unknown callback: {cb_key}")
            return {"warning": "Unknown callback"}

        # ===== Logic =====
        logic_instance: LogicProtocol[Any] = self._instantiate(config.logic)
        result: LogicResult[Any] = logic_instance.execute()

        logging.info(f"Execute: {cb_key}, state: {result.ui_message}")

        # ===== Action =====
        action_instance = self._instantiate(config.action)
        action_instance.execute(result.payload)

        # ===== UI updates =====
        return {"ui_message": result.ui_message}
