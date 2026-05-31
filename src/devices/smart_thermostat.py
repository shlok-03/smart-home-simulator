"""
smart_thermostat.py
-------------------
A smart thermostat that controls room temperature.

New OOP Concept introduced here:
- State management : the thermostat tracks current vs target temperature
                     and changes its BEHAVIOUR based on that state
                     (heating / cooling / idle)
"""

from src.devices.smart_device import SmartDevice


class SmartThermostat(SmartDevice):
    """
    Smart thermostat with heating, cooling, and eco mode.

    The thermostat decides its own operating mode (heating/cooling/idle)
    based on the gap between current and target temperature.
    """

    BASE_ENERGY_WATTS = 150.0    # watts when actively heating or cooling

    # Operating mode constants — avoids "magic strings" scattered in code
    MODE_IDLE    = "idle"
    MODE_HEATING = "heating"
    MODE_COOLING = "cooling"
    MODE_ECO     = "eco"

    def __init__(self, device_id: str, name: str, room: str = None):
        super().__init__(device_id, name, room)

        self._target_temperature: float = 21.0    # °C — what the user wants
        self._current_temperature: float = 18.0   # °C — what the sensor reads
        self._mode: str = self.MODE_IDLE
        self._eco_mode: bool = False
        self._min_temp: float = 10.0
        self._max_temp: float = 35.0

    # -------------------------------------------------------------------------
    # OVERRIDE
    # -------------------------------------------------------------------------

    def turn_on(self):
        super().turn_on()
        self._update_mode()   # decide immediately whether to heat or cool

    def turn_off(self):
        super().turn_off()
        self._mode = self.MODE_IDLE

    def get_status(self) -> dict:
        return {
            "id":          self._id,
            "name":        self._name,
            "type":        "SmartThermostat",
            "power":       self._power_state,
            "target_temp": self._target_temperature,
            "current_temp":self._current_temperature,
            "mode":        self._mode,
            "eco_mode":    self._eco_mode,
            "energy_w":    self._energy_consumption,
            "room":        self._room,
        }

    # -------------------------------------------------------------------------
    # THERMOSTAT-SPECIFIC METHODS
    # -------------------------------------------------------------------------

    def set_target_temperature(self, temp: float) -> None:
        """Change target temperature and update operating mode."""
        if not self._min_temp <= temp <= self._max_temp:
            print(f"  ⚠️  Temperature must be {self._min_temp}–{self._max_temp}°C")
            return

        # Eco mode caps the target to save energy
        if self._eco_mode and temp > 23.0:
            print(f"  🌿 Eco mode active — capping target at 23°C")
            temp = 23.0

        self._target_temperature = temp
        print(f"  🌡️  [{self._name}] target temperature set to {temp}°C")
        if self._power_state:
            self._update_mode()

    def update_current_temperature(self, temp: float) -> None:
        """
        Called by a temperature sensor when it reads a new value.
        This is how sensors and devices communicate (more in Part 3).
        """
        self._current_temperature = temp
        print(f"  📡 [{self._name}] current temperature updated to {temp}°C")
        if self._power_state:
            self._update_mode()

    def enable_eco_mode(self) -> None:
        """Eco mode limits heating to save energy."""
        self._eco_mode = True
        print(f"  🌿 [{self._name}] eco mode ENABLED")
        # Enforce cap immediately
        if self._target_temperature > 23.0:
            self.set_target_temperature(23.0)

    def disable_eco_mode(self) -> None:
        self._eco_mode = False
        print(f"  🌿 [{self._name}] eco mode DISABLED")

    # -------------------------------------------------------------------------
    # PRIVATE HELPER — internal logic, not meant for outside use
    # The leading _ is a signal: "this method is internal only"
    # -------------------------------------------------------------------------

    def _update_mode(self) -> None:
        """
        Decide whether to heat, cool, or idle.

        This is PRIVATE (note the _) — it's an implementation detail.
        Outside code calls set_target_temperature() or update_current_temperature()
        and this runs automatically.
        """
        diff = self._target_temperature - self._current_temperature

        if abs(diff) <= 0.5:      # within half a degree → nothing to do
            self._mode = self.MODE_IDLE
            self._energy_consumption = 0.0
        elif diff > 0:            # target is warmer than current → heat up
            self._mode = self.MODE_HEATING
            self._energy_consumption = self.BASE_ENERGY_WATTS
        else:                     # target is cooler than current → cool down
            self._mode = self.MODE_COOLING
            self._energy_consumption = self.BASE_ENERGY_WATTS * 1.2   # AC uses more

        emoji = {"idle": "😴", "heating": "🔥", "cooling": "❄️", "eco": "🌿"}
        print(f"  {emoji.get(self._mode, '')} [{self._name}] mode: {self._mode.upper()}"
              f"  ({self._current_temperature}°C → {self._target_temperature}°C)")

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def target_temperature(self) -> float:
        return self._target_temperature

    @property
    def current_temperature(self) -> float:
        return self._current_temperature

    @property
    def mode(self) -> str:
        return self._mode

    @property
    def eco_mode(self) -> bool:
        return self._eco_mode
