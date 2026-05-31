"""
motion_sensor.py
----------------
Detects movement in a room and reports occupancy.

Real-world behaviour modelled here:
  - PIR (passive infrared) sensors detect body heat moving across a room.
  - They fire when motion starts, and again when the room goes quiet
    after a "cooldown" period with no new movement.

Events this sensor fires:
  1. "motion_detected"  — something moved
  2. "motion_cleared"   — no movement for a while (room probably empty)
"""

from src.sensors.sensor import Sensor


class MotionSensor(Sensor):
    """
    Detects movement in a room.

    Keeps track of:
      - whether motion is currently detected
      - how many times motion has been detected (count)
      - a cooldown value — seconds before declaring the room empty
    """

    def __init__(self, sensor_id: str, name: str, room: str = None,
                 cooldown_seconds: int = 900):
        """
        Parameters:
            cooldown_seconds : how long with no motion before firing
                               "motion_cleared". Default = 15 minutes (900s).
        """
        super().__init__(sensor_id, name, room)
        self._motion_detected  = False
        self._detection_count  = 0        # total times motion was seen
        self._cooldown_seconds = cooldown_seconds
        self._sensitivity      = "medium" # low / medium / high

    # ------------------------------------------------------------------
    # MAIN ACTION
    # ------------------------------------------------------------------

    def detect_motion(self, location_detail: str = None) -> dict:
        """
        Call this to simulate motion being detected.

        Returns the event dictionary so callers can inspect what fired.
        """
        if not self._active:
            print(f"  ⚠️  [{self._name}] is deactivated — ignoring motion")
            return {}

        self._motion_detected = True
        self._detection_count += 1

        where = location_detail or self._room or "unknown"
        print(f"  🏃 [{self._name}] MOTION DETECTED in {where}")

        # Build a standardised event and tell all listeners about it
        event = self._build_event(
            event_type="motion_detected",
            data={
                "location":        where,
                "detection_count": self._detection_count,
                "sensitivity":     self._sensitivity,
            }
        )
        self._notify_listeners(event)   # <- this is the Observer pattern in action
        return event

    def clear_motion(self) -> dict:
        """
        Call this when the cooldown expires and the room is quiet.
        In a real system a timer would trigger this automatically.
        """
        if not self._motion_detected:
            return {}

        self._motion_detected = False
        print(f"  🕊️  [{self._name}] motion CLEARED — room appears empty")

        event = self._build_event(
            event_type="motion_cleared",
            data={"cooldown_seconds": self._cooldown_seconds}
        )
        self._notify_listeners(event)
        return event

    def set_sensitivity(self, level: str) -> None:
        """
        Adjust how sensitive the sensor is.
        'low'    — only reacts to large movements (person walking)
        'medium' — standard sensitivity
        'high'   — reacts to small movements (a hand wave)
        """
        if level not in ("low", "medium", "high"):
            print(f"  ⚠️  Sensitivity must be low / medium / high")
            return
        self._sensitivity = level
        print(f"  🎚️  [{self._name}] sensitivity set to {level}")

    def get_status(self) -> dict:
        return {
            "id":              self._id,
            "name":            self._name,
            "type":            "MotionSensor",
            "active":          self._active,
            "motion_detected": self._motion_detected,
            "detection_count": self._detection_count,
            "sensitivity":     self._sensitivity,
            "room":            self._room,
        }

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def motion_detected(self) -> bool:
        return self._motion_detected

    @property
    def detection_count(self) -> int:
        return self._detection_count
