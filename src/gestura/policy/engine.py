from ..models.policy import TriggerEvent, CallbackPolicy, CallbackState


class PolicyEngine:
    """
    Central decision engine.
    Stateless externally, stateful internally.

    Args:
        cooldown_seconds:
            Minimum time that must pass between two successful executions.

        rate_window_seconds:
            Time window for rate limiting.

        max_triggers:
            Maximum number of executions allowed within the rate window.
    """

    def __init__(self, policies: dict[str, CallbackPolicy]) -> None:
        self._policies = policies
        self._states: dict[str, CallbackState] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def evaluate(self, _TriggerEvent: TriggerEvent) -> bool:
        """
        Returns True if execution is allowed.
        Updates state if allowed.
        """

        policy = self._policies.get(_TriggerEvent.callback)

        # No policy → always allow
        if policy is None:
            return True

        state = self._states.setdefault(_TriggerEvent.callback, CallbackState())

        # Cooldown check
        if not self._check_cooldown(state, policy, _TriggerEvent.timestamp):
            return False

        # Rate limit check
        if not self._check_rate_limit(state, policy, _TriggerEvent.timestamp):
            return False

        # Record execution
        self._record_execution(state, _TriggerEvent.timestamp)
        return True

    # ------------------------------------------------------------------
    # Internal checks
    # ------------------------------------------------------------------

    def _check_cooldown(
        self,
        state: CallbackState,
        policy: CallbackPolicy,
        now: float
    ) -> bool:
        """
        Ensures minimum spacing between executions.
        """

        if policy.cooldown_seconds <= 0:
            return True

        return (now - state.last_executed_at) >= policy.cooldown_seconds

    def _check_rate_limit(
        self,
        state: CallbackState,
        policy: CallbackPolicy,
        now: float
    ) -> bool:
        """
        Sliding window rate limiter.
        """

        window_start = now - policy.rate_window_seconds

        # Remove expired timestamps
        timestamps = state.execution_timestamps
        while timestamps and timestamps[0] < window_start:
            timestamps.popleft()

        # Check limit
        return len(timestamps) < policy.max_triggers

    def _record_execution(
        self,
        state: CallbackState,
        now: float,
    ) -> None:
        """
        Updates execution state.
        """

        state.last_executed_at = now
        state.execution_timestamps.append(now)

