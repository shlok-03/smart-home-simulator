"""
automation_engine.py
--------------------
The brain of the smart home.

The AutomationEngine:
  1. Subscribes to ALL events via the EventBus (wildcard *)
  2. When an event arrives, scans every registered rule
  3. Executes the actions of every rule that matches the event

This is where the Observer pattern (EventBus) and the rules system
come together. The engine is the central subscriber that makes
everything react automatically.
"""

from src.automation.event_bus      import EventBus
from src.automation.automation_rule import AutomationRule
from src.house.logger              import Logger
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.house.house import House
    from src.notifications.notification_service import NotificationService


class AutomationEngine:
    """
    Processes automation rules when events arrive.

    The engine doesn't care which sensors exist — it only listens to
    the EventBus and acts on whatever events come through.
    """

    def __init__(self, house: "House",
                 notification_service: "NotificationService" = None):
        """
        Parameters:
            house                : needed to look up devices by ID
            notification_service : optional — used for notify actions
        """
        self._house        = house
        self._rules: List[AutomationRule] = []
        self._notifications = notification_service
        self._logger        = Logger()
        self._enabled       = True

        # Subscribe to EVERY event on the bus — wildcard "*"
        EventBus().subscribe_all(self._handle_event)
        print("  🤖 AutomationEngine started — listening to all events")

    # ------------------------------------------------------------------
    # RULE MANAGEMENT
    # ------------------------------------------------------------------

    def add_rule(self, rule: AutomationRule) -> None:
        """Register a new automation rule."""
        self._rules.append(rule)
        print(f"  📌 Rule added: {rule}")

    def remove_rule(self, rule_id: str) -> bool:
        """Remove a rule by ID. Returns True if found and removed."""
        for rule in self._rules:
            if rule.id == rule_id:
                self._rules.remove(rule)
                print(f"  🗑️  Rule '{rule.name}' removed")
                return True
        return False

    def get_rule(self, rule_id: str):
        for rule in self._rules:
            if rule.id == rule_id:
                return rule
        return None

    def list_rules(self) -> None:
        """Print a summary of all registered rules."""
        print(f"\n  📋 Automation Rules ({len(self._rules)} total):")
        for rule in self._rules:
            icon = "✅" if rule.enabled else "⏸️ "
            print(f"     {icon} {rule}")

    # ------------------------------------------------------------------
    # EVENT HANDLING
    # ------------------------------------------------------------------

    def _handle_event(self, event: dict) -> None:
        """
        Called automatically by EventBus whenever any event is published.

        Loops through all rules and executes the ones that match.
        """
        if not self._enabled:
            return

        event_type = event.get("event_type", "unknown")
        matched_count = 0

        for rule in self._rules:
            if rule.matches(event):
                matched_count += 1
                print(f"\n  🤖 [{rule.name}] triggered by '{event_type}'")
                self._execute_rule(rule, event)
                rule.record_execution()

        if matched_count == 0 and event_type not in ("temperature_changed",):
            # Don't log noisy frequent events like temperature readings
            pass

    def _execute_rule(self, rule: AutomationRule, event: dict) -> None:
        """Run every action in a matched rule."""
        for action in rule.actions:
            self._execute_action(action, event)

    def _execute_action(self, action: dict, event: dict) -> None:
        """
        Execute a single action dict.

        The action type determines which device method to call.
        """
        action_type = action.get("type")
        device_id   = action.get("device_id")

        # Actions that target a specific device
        if device_id:
            device = self._house.find_device(device_id)
            if device is None:
                print(f"  ⚠️  Engine: device '{device_id}' not found")
                return

            if action_type == "turn_on":
                device.turn_on()
                self._logger.info("AutomationEngine",
                                  f"Turned ON {device.name}")

            elif action_type == "turn_off":
                device.turn_off()
                self._logger.info("AutomationEngine",
                                  f"Turned OFF {device.name}")

            elif action_type == "set_brightness":
                from src.devices.smart_light import SmartLight
                if isinstance(device, SmartLight):
                    device.set_brightness(int(action.get("value", 100)))

            elif action_type == "set_temperature":
                from src.devices.smart_thermostat import SmartThermostat
                if isinstance(device, SmartThermostat):
                    device.set_target_temperature(float(action.get("value", 21)))

            elif action_type == "lock":
                from src.devices.smart_door_lock import SmartDoorLock
                if isinstance(device, SmartDoorLock):
                    device.lock("automation_engine")

            elif action_type == "unlock":
                from src.devices.smart_door_lock import SmartDoorLock
                if isinstance(device, SmartDoorLock):
                    device.unlock("automation_engine",
                                  pin=action.get("pin", ""))

            elif action_type == "start_recording":
                from src.devices.security_camera import SecurityCamera
                if isinstance(device, SecurityCamera):
                    device.start_recording()

        # Actions that don't target a specific device
        if action_type == "notify":
            message  = action.get("message", "Smart home event occurred")
            priority = action.get("priority", "normal")

            if self._notifications:
                self._notifications.send_simple(
                    title    = "Automation Alert",
                    message  = message,
                    priority = priority,
                    source   = "AutomationEngine"
                )
            else:
                print(f"  🔔 NOTIFICATION: {message}")

            self._logger.info("AutomationEngine", f"Notification sent: {message}")

    # ------------------------------------------------------------------
    # ENGINE CONTROL
    # ------------------------------------------------------------------

    def pause(self) -> None:
        """Stop processing all events (rules stay registered)."""
        self._enabled = False
        print("  ⏸️  AutomationEngine PAUSED")

    def resume(self) -> None:
        """Resume processing events."""
        self._enabled = True
        print("  ▶️   AutomationEngine RESUMED")

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def rule_count(self) -> int:
        return len(self._rules)

    @property
    def enabled(self) -> bool:
        return self._enabled
