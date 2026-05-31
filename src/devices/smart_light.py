"""
smart_light.py
--------------
A smart light bulb that can be dimmed and change colour.

OOP Concepts demonstrated:
- Inheritance   : SmartLight extends SmartDevice
- Polymorphism  : overrides turn_on(), turn_off(), get_status()
- Encapsulation : brightness/colour are private, exposed via properties
"""

from src.devices.smart_device import SmartDevice


class SmartLight(SmartDevice):
    """
    A dimmable, colour-changeable smart light.

    Inherits everything from SmartDevice and adds:
    - brightness (0–100 %)
    - colour mode (white / warm / red / green / blue / …)
    - auto shutoff after N minutes
    """

    # Class-level constant — shared by ALL SmartLight instances
    BASE_ENERGY_WATTS = 10.0   # watts when on at 100 % brightness

    def __init__(self, device_id: str, name: str, room: str = None):
        # Call the PARENT constructor first — super() means SmartDevice.__init__
        super().__init__(device_id, name, room)

        # Light-specific private attributes
        self._brightness: int = 100      # percentage 0–100
        self._colour_mode: str = "white"
        self._auto_shutoff_minutes: int = 0   # 0 = disabled

    # -------------------------------------------------------------------------
    # OVERRIDE parent methods  (Polymorphism)
    # -------------------------------------------------------------------------

    def turn_on(self):
        """Turn on and update energy consumption based on brightness."""
        super().turn_on()   # run the parent's turn_on() first
        # Energy scales with brightness: 100% brightness = 10W, 50% = 5W, etc.
        self._energy_consumption = self.BASE_ENERGY_WATTS * (self._brightness / 100)

    def turn_off(self):
        """Turn off (energy resets to 0 inside parent's turn_off)."""
        super().turn_off()

    def get_status(self) -> dict:
        """
        Return a dictionary with the light's full state.
        Every device type returns DIFFERENT fields here — that's polymorphism.
        """
        return {
            "id":           self._id,
            "name":         self._name,
            "type":         "SmartLight",
            "power":        self._power_state,
            "brightness":   self._brightness,
            "colour":       self._colour_mode,
            "energy_w":     self._energy_consumption,
            "room":         self._room,
            "auto_shutoff": self._auto_shutoff_minutes,
        }

    # -------------------------------------------------------------------------
    # LIGHT-SPECIFIC METHODS
    # -------------------------------------------------------------------------

    def set_brightness(self, level: int) -> None:
        """
        Set brightness 0–100.
        Validates input before accepting — this is encapsulation at work:
        the outside world can't just set any value; we check it first.
        """
        if not 0 <= level <= 100:
            print(f"  ⚠️  Brightness must be 0–100, got {level}")
            return
        self._brightness = level
        # Update energy draw if the light is on
        if self._power_state:
            self._energy_consumption = self.BASE_ENERGY_WATTS * (level / 100)
        print(f"  💡 [{self._name}] brightness set to {level}%")

    def set_colour(self, colour: str) -> None:
        """Change the colour mode."""
        allowed = {"white", "warm", "red", "green", "blue", "purple", "yellow"}
        if colour.lower() not in allowed:
            print(f"  ⚠️  Unknown colour '{colour}'. Choose from: {allowed}")
            return
        self._colour_mode = colour.lower()
        print(f"  🎨 [{self._name}] colour set to {colour}")

    def set_auto_shutoff(self, minutes: int) -> None:
        """Set auto-shutoff timer (0 = disabled)."""
        self._auto_shutoff_minutes = max(0, minutes)
        if minutes > 0:
            print(f"  ⏱️  [{self._name}] will auto-shutoff in {minutes} min")
        else:
            print(f"  ⏱️  [{self._name}] auto-shutoff disabled")

    # -------------------------------------------------------------------------
    # PROPERTIES (read access to private data)
    # -------------------------------------------------------------------------

    @property
    def brightness(self) -> int:
        return self._brightness

    @property
    def colour_mode(self) -> str:
        return self._colour_mode
