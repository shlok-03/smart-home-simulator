"""
temperature_sensor.py
---------------------
Reads room temperature and fires events when it crosses thresholds.

Real-world behaviour modelled:
  - The sensor reads a value continuously.
  - It only fires an event when the temperature crosses a meaningful
    boundary (e.g. goes above 28°C or drops below 15°C).
  - This avoids spamming the automation engine every single second.

Events this sensor fires:
  1. "temperature_changed"    — reading updated (always)
  2. "temperature_too_high"   — reading went above high threshold
  3. "temperature_too_low"    — reading went below low threshold
  4. "temperature_normal"     — returned to normal range after being out of bounds
"""

from src.sensors.sensor import Sensor


class TemperatureSensor(Sensor):
    """
    Measures room temperature and alerts when out of a safe range.
    """

    def __init__(self, sensor_id: str, name: str, room: str = None,
                 low_threshold: float  = 15.0,
                 high_threshold: float = 28.0):
        """
        Parameters:
            low_threshold  : below this → fire "temperature_too_low"
            high_threshold : above this → fire "temperature_too_high"
        """
        super().__init__(sensor_id, name, room)
        self._current_temp   = 20.0        # default starting reading
        self._low_threshold  = low_threshold
        self._high_threshold = high_threshold
        self._unit           = "C"         # Celsius
        self._out_of_range   = False       # tracks whether we're in an alert state

    # ------------------------------------------------------------------
    # MAIN ACTION
    # ------------------------------------------------------------------

    def read_temperature(self, temperature: float) -> dict:
        """
        Submit a new temperature reading.

        The sensor decides which event (if any) to fire based on how
        the new reading compares to the thresholds.
        """
        if not self._active:
            return {}

        previous = self._current_temp
        self._current_temp = temperature
        change = round(temperature - previous, 2)

        print(f"  🌡️  [{self._name}] reading: {temperature}°{self._unit} "
              f"(was {previous}°{self._unit})")

        # Always fire a general "temperature changed" event
        event = self._build_event(
            event_type="temperature_changed",
            data={
                "temperature":  temperature,
                "previous":     previous,
                "change":       change,
                "unit":         self._unit,
            }
        )
        self._notify_listeners(event)

        # Then check whether we crossed a threshold
        self._check_thresholds(temperature)

        return event

    def _check_thresholds(self, temp: float) -> None:
        """
        Private helper — fires additional events if temp is out of range.
        Keeps track of whether we were already out of range so we don't
        spam the same alert over and over.
        """
        if temp > self._high_threshold:
            if not self._out_of_range:          # only fire ONCE when crossing
                self._out_of_range = True
                print(f"  🔥 [{self._name}] TEMPERATURE TOO HIGH: {temp}°{self._unit}")
                event = self._build_event(
                    event_type="temperature_too_high",
                    data={
                        "temperature": temp,
                        "threshold":   self._high_threshold,
                    }
                )
                self._notify_listeners(event)

        elif temp < self._low_threshold:
            if not self._out_of_range:
                self._out_of_range = True
                print(f"  🥶 [{self._name}] TEMPERATURE TOO LOW: {temp}°{self._unit}")
                event = self._build_event(
                    event_type="temperature_too_low",
                    data={
                        "temperature": temp,
                        "threshold":   self._low_threshold,
                    }
                )
                self._notify_listeners(event)

        else:
            # Temperature is back in the safe range
            if self._out_of_range:
                self._out_of_range = False
                print(f"  ✅ [{self._name}] temperature back to normal: {temp}°{self._unit}")
                event = self._build_event(
                    event_type="temperature_normal",
                    data={"temperature": temp}
                )
                self._notify_listeners(event)

    def set_thresholds(self, low: float, high: float) -> None:
        """Adjust what counts as too cold or too hot."""
        if low >= high:
            print(f"  ⚠️  Low threshold must be less than high threshold")
            return
        self._low_threshold  = low
        self._high_threshold = high
        print(f"  🎚️  [{self._name}] thresholds set: {low}°–{high}°{self._unit}")

    def get_status(self) -> dict:
        return {
            "id":            self._id,
            "name":          self._name,
            "type":          "TemperatureSensor",
            "active":        self._active,
            "temperature":   self._current_temp,
            "unit":          self._unit,
            "low_threshold": self._low_threshold,
            "high_threshold":self._high_threshold,
            "out_of_range":  self._out_of_range,
            "room":          self._room,
        }

    # ------------------------------------------------------------------
    # PROPERTIES
    # ------------------------------------------------------------------

    @property
    def current_temperature(self) -> float:
        return self._current_temp

    @property
    def is_out_of_range(self) -> bool:
        return self._out_of_range
