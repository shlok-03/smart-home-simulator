"""
sensor.py
---------
Base class for every sensor in the smart home.

A sensor is different from a device:
  - A DEVICE does something  (light turns on, lock clicks shut)
  - A SENSOR watches for something  (movement, heat, smoke, open doors)

New concept introduced here — the OBSERVER pattern (preview):
  Sensors keep a list of "listeners". When something happens,
  the sensor loops through that list and calls each listener.
  This way the sensor doesn't need to know WHO is listening —
  it just shouts the event and whoever cares will react.

Think of it like a smoke alarm:
  - The alarm doesn't know who's in the house.
  - It just beeps. People react on their own.
"""

from abc import ABC, abstractmethod
from datetime import datetime


class Sensor(ABC):
    """
    Abstract base class for all sensors.

    Every sensor can:
      - be activated / deactivated
      - hold a list of listeners (observers)
      - fire events to those listeners
    """

    def __init__(self, sensor_id: str, name: str, room: str = None):
        self._id       = sensor_id
        self._name     = name
        self._room     = room
        self._active   = True          # sensors start active by default
        self._listeners = []           # list of functions to call when event fires
        self._last_triggered = None    # timestamp of the last event

    # ------------------------------------------------------------------
    # OBSERVER PATTERN — listener management
    # ------------------------------------------------------------------

    def add_listener(self, callback) -> None:
        """
        Register a function that will be called when this sensor fires.

        'callback' is just a function. When the sensor detects something,
        it will call that function and pass it the event data.

        Example:
            def my_handler(event):
                print("Got event:", event)

            motion_sensor.add_listener(my_handler)
        """
        if callback not in self._listeners:
            self._listeners.append(callback)

    def remove_listener(self, callback) -> None:
        """Unregister a listener so it stops receiving events."""
        if callback in self._listeners:
            self._listeners.remove(callback)

    def _notify_listeners(self, event: dict) -> None:
        """
        Loop through every registered listener and call it with the event.

        This is PRIVATE (leading _) — only called internally by subclasses
        when they detect something.
        """
        for callback in self._listeners:
            callback(event)

    # ------------------------------------------------------------------
    # ABSTRACT METHOD — each sensor type must implement this
    # ------------------------------------------------------------------

    @abstractmethod
    def get_status(self) -> dict:
        """Return the current state of the sensor as a dictionary."""
        pass

    # ------------------------------------------------------------------
    # SHARED HELPERS
    # ------------------------------------------------------------------

    def _build_event(self, event_type: str, data: dict) -> dict:
        """
        Build a standardised event dictionary.

        Every event from every sensor has the same envelope:
        {
            "event_type": "motion_detected",
            "sensor_id":  "s_001",
            "sensor_name":"Hallway Motion",
            "room":       "Hallway",
            "timestamp":  "2026-05-31T19:00:00",
            ... plus any extra data the sensor adds
        }
        Having a consistent shape makes the automation engine's job easy:
        it can always look at event["event_type"] regardless of which sensor fired.
        """
        event = {
            "event_type":  event_type,
            "sensor_id":   self._id,
            "sensor_name": self._name,
            "room":        self._room,
            "timestamp":   datetime.now().isoformat(),
        }
        event.update(data)      # merge in any sensor-specific fields
        self._last_triggered = datetime.now()
        return event

    def activate(self) -> None:
        self._active = True
        print(f"  ✅ Sensor [{self._name}] ACTIVATED")

    def deactivate(self) -> None:
        self._active = False
        print(f"  ⏸️  Sensor [{self._name}] DEACTIVATED")

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
    def room(self) -> str:
        return self._room

    @room.setter
    def room(self, value: str):
        self._room = value

    @property
    def is_active(self) -> bool:
        return self._active

    @property
    def last_triggered(self):
        return self._last_triggered

    def __str__(self) -> str:
        state = "active" if self._active else "inactive"
        return f"{self._name} ({self.__class__.__name__}) | {state} | Room: {self._room}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id!r}>"
