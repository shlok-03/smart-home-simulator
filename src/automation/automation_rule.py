"""
automation_rule.py
------------------
A single automation rule: IF (trigger + conditions) THEN (actions).

Think of a rule like a smart home recipe:
  IF  smoke is detected in Kitchen
  AND level is above 30 ppm
  THEN turn off the thermostat
       unlock the front door
       send a critical notification
"""

from datetime import datetime


class AutomationRule:
    """
    Represents one automation rule.

    A rule has three parts:
      1. trigger_event  - which event type activates this rule
      2. conditions     - optional extra checks on the event data
      3. actions        - what to do when the rule fires
    """

    def __init__(self, rule_id: str, name: str, trigger_event: str,
                 actions: list, conditions: list = None, enabled: bool = True):
        """
        Parameters:
            rule_id       : unique id, e.g. "rule_001"
            name          : human label, e.g. "Hallway Motion Light"
            trigger_event : event_type string to watch for, e.g. "motion_detected"
            actions       : list of action dicts (what to DO when rule fires)
            conditions    : list of condition dicts (extra filters, optional)
            enabled       : whether this rule is active

        Action dict shape:
            {"type": "turn_on",  "device_id": "dev_001"}
            {"type": "turn_off", "device_id": "dev_001"}
            {"type": "set_brightness", "device_id": "dev_001", "value": 80}
            {"type": "set_temperature","device_id": "dev_002", "value": 22}
            {"type": "unlock",   "device_id": "dev_003", "pin": "1234"}
            {"type": "lock",     "device_id": "dev_003"}
            {"type": "notify",   "message": "Motion detected!", "priority": "normal"}
            {"type": "start_recording", "device_id": "dev_004"}

        Condition dict shape:
            {"field": "room",  "operator": "equals",       "value": "Hallway"}
            {"field": "level", "operator": "greater_than",  "value": 30}
            {"field": "level", "operator": "less_than",     "value": 10}
        """
        self._id              = rule_id
        self._name            = name
        self._trigger_event   = trigger_event
        self._conditions      = conditions or []
        self._actions         = actions
        self._enabled         = enabled
        self._execution_count = 0
        self._last_executed   = None

    # ------------------------------------------------------------------
    # MATCHING
    # ------------------------------------------------------------------

    def matches(self, event: dict) -> bool:
        """
        Return True if this rule should fire for the given event.

        Steps:
          1. Rule must be enabled
          2. Event type must match the trigger
          3. All conditions must pass
        """
        if not self._enabled:
            return False

        if event.get("event_type") != self._trigger_event:
            return False

        for condition in self._conditions:
            if not self._check_condition(condition, event):
                return False

        return True

    def _check_condition(self, condition: dict, event: dict) -> bool:
        """
        Evaluate a single condition against the event data.

        Operators supported:
          equals       - exact match (case-insensitive for strings)
          greater_than - numeric comparison
          less_than    - numeric comparison
          contains     - substring check
        """
        field    = condition.get("field")
        operator = condition.get("operator", "equals")
        expected = condition.get("value")

        actual = event.get(field)
        if actual is None:
            return False

        try:
            if operator == "equals":
                return str(actual).lower() == str(expected).lower()
            elif operator == "greater_than":
                return float(actual) > float(expected)
            elif operator == "less_than":
                return float(actual) < float(expected)
            elif operator == "contains":
                return str(expected).lower() in str(actual).lower()
        except (ValueError, TypeError):
            return False

        return False

    # ------------------------------------------------------------------
    # EXECUTION TRACKING
    # ------------------------------------------------------------------

    def record_execution(self) -> None:
        """Called by the engine after this rule's actions are run."""
        self._execution_count += 1
        self._last_executed = datetime.now()

    # ------------------------------------------------------------------
    # ENABLE / DISABLE
    # ------------------------------------------------------------------

    def enable(self) -> None:
        self._enabled = True
        print(f"  ✅ Rule '{self._name}' ENABLED")

    def disable(self) -> None:
        self._enabled = False
        print(f"  ⏸️  Rule '{self._name}' DISABLED")

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def trigger_event(self) -> str:
        return self._trigger_event

    @property
    def actions(self) -> list:
        return list(self._actions)

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def execution_count(self) -> int:
        return self._execution_count

    def __str__(self) -> str:
        state = "ON" if self._enabled else "OFF"
        return (f"Rule[{self._id}] '{self._name}' | "
                f"trigger={self._trigger_event} | "
                f"actions={len(self._actions)} | {state}")

    def __repr__(self) -> str:
        return f"<AutomationRule id={self._id!r} trigger={self._trigger_event!r}>"
