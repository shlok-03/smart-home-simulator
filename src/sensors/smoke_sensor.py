"""
smoke_sensor.py
---------------
Detects smoke and carbon monoxide — the most safety-critical sensor.

Why it's special:
  When this sensor fires, the expected response is different from all others.
  A motion sensor triggers lights. A smoke sensor triggers an EMERGENCY:
    - Unlock all doors so people can escape
    - Trigger an alarm
    - Notify everyone immediately

  The sensor itself doesn't do those things — that's the automation engine's job.
  The sensor just reports what it detected and fires the event.
  This separation is called the SINGLE RESPONSIBILITY PRINCIPLE (from SOLID):
    "A class should do ONE thing."
  The sensor's one thing: detect smoke.

Events fired:
  1. "smoke_detected"    — smoke / CO in the air
  2. "smoke_cleared"     — air is clean again
  3. "alarm_triggered"   — critical level reached, alarm going off
"""

from src.sensors.sensor import Sensor


class SmokeSensor(Sensor):
    """
    Detects smoke and carbon monoxide.

    Smoke levels (0 – 100 ppm for simplicity):
      0  – 10  : clean air
      10 – 30  : warning level (might be cooking smoke)
      30 – 100 : danger level  (fire likely)
      100+     : critical      (alarm triggers)
    """

    # Class-level thresholds — easy to adjust in one place
    LEVEL_CLEAN    = 10
    LEVEL_WARNING  = 30
    LEVEL_DANGER   = 100

    def __init__(self, sensor_id: str, name: str, room: str = None):
        super().__init__(sensor_id, name, room)
        self._smoke_level    = 0       # parts per million (0–100+ scale)
        self._smoke_detected = False
        self._alarm_active   = False
        self._co_detected    = False   # carbon monoxide flag

    # ------------------------------------------------------------------
    # MAIN ACTIONS
    # ------------------------------------------------------------------

    def detect_smoke(self, level: float, carbon_monoxide: bool = False) -> dict:
        """
        Report a smoke / CO reading.

        Parameters:
            level          : smoke concentration (our simplified 0–100+ ppm scale)
            carbon_monoxide: True if CO is also detected alongside smoke
        """
        if not self._active:
            return {}

        self._smoke_level  = level
        self._co_detected  = carbon_monoxide
        self._smoke_detected = level > self.LEVEL_CLEAN

        # Pick the right severity label for the printout
        if level <= self.LEVEL_CLEAN:
            label = "✅ clear"
        elif level <= self.LEVEL_WARNING:
            label = "⚠️  warning"
        elif level <= self.LEVEL_DANGER:
            label = "🚨 DANGER"
        else:
            label = "🔥 CRITICAL"

        co_note = " (+ CO detected!)" if carbon_monoxide else ""
        print(f"  💨 [{self._name}] smoke level: {level} ppm — {label}{co_note}")

        event = self._build_event(
            event_type="smoke_detected" if self._smoke_detected else "smoke_cleared",
            data={
                "level":           level,
                "carbon_monoxide": carbon_monoxide,
                "severity":        label.strip(),
            }
        )
        self._notify_listeners(event)

        # Trigger full alarm if critical
        if level > self.LEVEL_DANGER or carbon_monoxide:
            self._trigger_alarm(level, carbon_monoxide)

        return event

    def clear_smoke(self) -> dict:
        """Mark the air as clean — typically after a vent or false alarm."""
        self._smoke_detected = False
        self._smoke_level    = 0
        self._alarm_active   = False
        self._co_detected    = False
        print(f"  ✅ [{self._name}] smoke CLEARED — air is clean")

        event = self._build_event(
            event_type="smoke_cleared",
            data={"level": 0}
        )
        self._notify_listeners(event)
        return event

    def _trigger_alarm(self, level: float, co: bool) -> None:
        """
        Fires a high-priority alarm event.
        Private — called automatically when the level is critical.
        """
        if self._alarm_active:
            return   # alarm already going, no need to fire again

        self._alarm_active = True
        co_note = " and carbon monoxide" if co else ""
        print(f"  🚨🚨 FIRE ALARM TRIGGERED by [{self._name}]! "
              f"Smoke{co_note} at critical level ({level} ppm)")

        event = self._build_event(
            event_type="alarm_triggered",
            data={
                "level":           level,
                "carbon_monoxide": co,
                "message":         "EVACUATE IMMEDIATELY",
            }
        )
        self._notify_listeners(event)

    def silence_alarm(self) -> None:
        """Reset the alarm (e.g. after the fire brigade has cleared the scene)."""
        self._alarm_active = False
        print(f"  🔕 [{self._name}] alarm silenced")

    def get_status(self) -> dict:
        return {
            "id":             self._id,
            "name":           self._name,
            "type":           "SmokeSensor",
            "active":         self._active,
            "smoke_detected": self._smoke_detected,
            "smoke_level":    self._smoke_level,
            "co_detected":    self._co_detected,
            "alarm_active":   self._alarm_active,
            "room":           self._room,
        }

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def smoke_detected(self) -> bool:
        return self._smoke_detected

    @property
    def smoke_level(self) -> float:
        return self._smoke_level

    @property
    def alarm_active(self) -> bool:
        return self._alarm_active
