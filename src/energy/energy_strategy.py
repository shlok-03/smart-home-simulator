"""
energy_strategy.py
------------------
DESIGN PATTERN #4 — STRATEGY PATTERN

The problem this pattern solves:
  The smart home needs to manage energy differently depending on the
  situation: Normal, Eco, Away, and Night mode all behave differently.

  Without Strategy, you need a giant if/elif chain that grows every
  time you add a new mode, and it gets messy fast.

  With Strategy, each mode is its OWN class. Swapping modes means
  swapping ONE object. No if/elif chains needed anywhere.

Real-world analogy:
  A GPS app can route you by fastest, shortest, or toll-free path.
  You pick the strategy. The app applies it without changing its
  core navigation logic. Same road network, different algorithm.

Structure:
  EnergyStrategy       (abstract base — the shared interface)
      NormalStrategy   (full power, no restrictions)
      EcoStrategy      (dim lights, lower thermostat)
      AwayStrategy     (minimal power, security only)
      NightStrategy    (cameras on, lights off, temp reduced)
"""

from abc import ABC, abstractmethod
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.devices.smart_device import SmartDevice


class EnergyStrategy(ABC):
    """Abstract base — every strategy must implement these three methods."""

    @abstractmethod
    def apply(self, devices: List["SmartDevice"]) -> None:
        """Apply this strategy to the given list of devices."""
        pass

    @abstractmethod
    def name(self) -> str:
        pass

    @abstractmethod
    def description(self) -> str:
        pass


class NormalStrategy(EnergyStrategy):
    """No restrictions — devices run at whatever the user last set."""

    def apply(self, devices):
        print(f"\n  ⚡ NORMAL strategy applied — no changes made")

    def name(self):        return "normal"
    def description(self): return "No restrictions. Devices run at user settings."


class EcoStrategy(EnergyStrategy):
    """
    Reduce energy without being too disruptive.
    Dims lights to 50% and lowers the thermostat to 20 C.
    """

    def apply(self, devices):
        from src.devices.smart_light      import SmartLight
        from src.devices.smart_thermostat import SmartThermostat

        print(f"\n  🌿 ECO strategy applied")
        for device in devices:
            if isinstance(device, SmartLight) and device.power_state:
                device.set_brightness(50)
            elif isinstance(device, SmartThermostat) and device.power_state:
                device.enable_eco_mode()
                device.set_target_temperature(20.0)

    def name(self):        return "eco"
    def description(self): return "Dims lights to 50%, lowers thermostat to 20C."


class AwayStrategy(EnergyStrategy):
    """
    Nobody home — maximise savings.
    Lights and speakers off. Cameras stay on. Thermostat at 16 C.
    """

    def apply(self, devices):
        from src.devices.smart_light      import SmartLight
        from src.devices.smart_thermostat import SmartThermostat
        from src.devices.smart_speaker    import SmartSpeaker
        from src.devices.security_camera  import SecurityCamera

        print(f"\n  🏠 AWAY strategy applied")
        for device in devices:
            if isinstance(device, SmartLight):
                device.turn_off()
            elif isinstance(device, SmartSpeaker):
                device.turn_off()
            elif isinstance(device, SmartThermostat) and device.power_state:
                device.set_target_temperature(16.0)
            elif isinstance(device, SecurityCamera) and not device.power_state:
                device.turn_on()   # ensure cameras are ON when away

    def name(self):        return "away"
    def description(self): return "Lights/speakers off, cameras on, thermostat at 16C."


class NightStrategy(EnergyStrategy):
    """
    Sleeping hours.
    Hallway lights dim to 10%, others off. Thermostat 18 C. Cameras on.
    """

    def apply(self, devices):
        from src.devices.smart_light      import SmartLight
        from src.devices.smart_thermostat import SmartThermostat
        from src.devices.smart_speaker    import SmartSpeaker
        from src.devices.security_camera  import SecurityCamera

        print(f"\n  🌙 NIGHT strategy applied")
        for device in devices:
            if isinstance(device, SmartLight) and device.power_state:
                if device.room and "hallway" in device.room.lower():
                    device.set_brightness(10)   # dim nightlight in hallway
                else:
                    device.turn_off()
            elif isinstance(device, SmartThermostat) and device.power_state:
                device.set_target_temperature(18.0)
            elif isinstance(device, SmartSpeaker) and device.power_state:
                device.turn_off()
            elif isinstance(device, SecurityCamera) and not device.power_state:
                device.turn_on()

    def name(self):        return "night"
    def description(self): return "Lights off, cameras on, thermostat at 18C."


# ---------------------------------------------------------------------------
# EnergyManager — the "context" object that holds the current strategy
# ---------------------------------------------------------------------------

class EnergyManager:
    """
    Holds the active energy strategy and applies it on demand.

    The key benefit: the rest of the system calls energy_manager.apply(devices)
    without knowing or caring WHICH strategy is active.
    Changing strategies is one line: manager.set_strategy("eco").
    """

    STRATEGIES = {
        "normal": NormalStrategy(),
        "eco":    EcoStrategy(),
        "away":   AwayStrategy(),
        "night":  NightStrategy(),
    }

    def __init__(self):
        self._current: EnergyStrategy = self.STRATEGIES["normal"]

    def set_strategy(self, strategy_name: str) -> None:
        """Switch to a named strategy."""
        key = strategy_name.lower()
        if key not in self.STRATEGIES:
            options = ", ".join(self.STRATEGIES.keys())
            print(f"  ⚠️  Unknown strategy '{strategy_name}'. Options: {options}")
            return
        self._current = self.STRATEGIES[key]
        print(f"  ⚡ Energy strategy → {self._current.name().upper()}: "
              f"{self._current.description()}")

    def apply(self, devices: list) -> None:
        """Run the current strategy against the provided device list."""
        self._current.apply(devices)

    @property
    def current_strategy(self) -> str:
        return self._current.name()
