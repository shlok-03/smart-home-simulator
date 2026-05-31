"""
door_sensor.py
--------------
Detects whether a door or window is open or closed.

These are the small magnetic sensors you often see on door frames.
When the door opens, the magnet separates and the circuit breaks.

Events fired:
  1. "door_opened"  — door just opened
  2. "door_closed"  — door just closed
  3. "door_left_open" — door has been open longer than the timeout

Why the "left open" event matters:
  If a door is open for 10+ minutes at night, that could be:
    - a security breach
    - someone forgot to close it
  The automation engine can respond by alerting the owner.
"""

from src.sensors.sensor import Sensor
from datetime import datetime


class DoorSensor(Sensor):
    """
    Magnetic contact sensor for doors and windows.

    Tracks:
      - open / closed state
      - how many times it has been opened
      - timestamp of when it last opened
      - whether it's been left open too long
    """

    def __init__(self, sensor_id: str, name: str, room: str = None,
                 open_timeout_seconds: int = 600,
                 door_type: str = "door"):
        """
        Parameters:
            open_timeout_seconds : how long before firing "door_left_open" (default 10 min)
            door_type            : "door" or "window"
        """
        super().__init__(sensor_id, name, room)
        self._is_open            = False
        self._open_count         = 0
        self._opened_at          = None    # datetime when it was last opened
        self._open_timeout       = open_timeout_seconds
        self._door_type          = door_type
        self._left_open_alerted  = False   # so we only alert once per open event

    # ------------------------------------------------------------------
    # MAIN ACTIONS
    # ------------------------------------------------------------------

    def open(self, opened_by: str = "unknown") -> dict:
        """
        The door just opened.

        Parameters:
            opened_by : who or what opened it ("Alice", "wind", "system")
        """
        if not self._active:
            return {}

        if self._is_open:
            print(f"  ⚠️  [{self._name}] was already open")
            return {}

        self._is_open           = True
        self._open_count       += 1
        self._opened_at         = datetime.now()
        self._left_open_alerted = False    # reset for this new open event

        print(f"  🚪 [{self._name}] OPENED by {opened_by} "
              f"(total opens: {self._open_count})")

        event = self._build_event(
            event_type="door_opened",
            data={
                "door_type": self._door_type,
                "opened_by": opened_by,
                "open_count":self._open_count,
            }
        )
        self._notify_listeners(event)
        return event

    def close(self, closed_by: str = "unknown") -> dict:
        """The door just closed."""
        if not self._active:
            return {}

        if not self._is_open:
            print(f"  ⚠️  [{self._name}] was already closed")
            return {}

        # Calculate how long it was open
        duration = 0
        if self._opened_at:
            duration = int((datetime.now() - self._opened_at).total_seconds())

        self._is_open   = False
        self._opened_at = None

        print(f"  🚪 [{self._name}] CLOSED by {closed_by} "
              f"(was open for {duration}s)")

        event = self._build_event(
            event_type="door_closed",
            data={
                "door_type":       self._door_type,
                "closed_by":       closed_by,
                "open_duration_s": duration,
            }
        )
        self._notify_listeners(event)
        return event

    def check_left_open(self) -> dict:
        """
        Call this periodically to check if the door has been left open
        past the timeout threshold.

        In a real system, a background timer would call this automatically.
        For the simulator we call it manually.
        """
        if not self._is_open or self._left_open_alerted:
            return {}

        if not self._opened_at:
            return {}

        elapsed = int((datetime.now() - self._opened_at).total_seconds())

        if elapsed >= self._open_timeout:
            self._left_open_alerted = True    # only alert once
            print(f"  ⚠️  [{self._name}] has been open for {elapsed}s "
                  f"— possible security issue!")

            event = self._build_event(
                event_type="door_left_open",
                data={
                    "door_type":       self._door_type,
                    "open_duration_s": elapsed,
                    "timeout":         self._open_timeout,
                }
            )
            self._notify_listeners(event)
            return event

        return {}

    def get_status(self) -> dict:
        elapsed = 0
        if self._is_open and self._opened_at:
            elapsed = int((datetime.now() - self._opened_at).total_seconds())

        return {
            "id":          self._id,
            "name":        self._name,
            "type":        "DoorSensor",
            "active":      self._active,
            "is_open":     self._is_open,
            "door_type":   self._door_type,
            "open_count":  self._open_count,
            "open_for_s":  elapsed,
            "room":        self._room,
        }

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def is_open(self) -> bool:
        return self._is_open

    @property
    def open_count(self) -> int:
        return self._open_count
