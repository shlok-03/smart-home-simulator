"""
device_factory.py
-----------------
DESIGN PATTERN #1 — FACTORY PATTERN

The problem this pattern solves:
  Imagine you have 10 different device types. Every time you want
  to create one, you need to import its class, remember its constructor
  arguments, and write the full class name.

  The Factory pattern wraps all of that behind ONE simple call:
      DeviceFactory.create("LIGHT", "dev_001", "Kitchen Light")

  The caller doesn't need to know which class to import.
  The factory handles all of that internally.

Real-world analogy:
  You go to a restaurant and say "I'll have the pasta."
  You don't go into the kitchen, find the pasta, boil the water,
  drain it, add sauce... The kitchen (factory) handles all of that.
  You just place the order.

Benefits:
  - Easy to add new device types later (just add one entry to the map)
  - The rest of the codebase doesn't need to change
  - Centralises object creation in one place
"""

from src.devices.smart_light      import SmartLight
from src.devices.smart_thermostat import SmartThermostat
from src.devices.smart_door_lock  import SmartDoorLock
from src.devices.security_camera  import SecurityCamera
from src.devices.smart_speaker    import SmartSpeaker


class DeviceFactory:
    """
    Static factory class for creating SmartDevice instances.

    'Static' means you never create a DeviceFactory object.
    You just call DeviceFactory.create(...) directly.
    """

    # This dictionary maps a simple string key to the actual class.
    # Adding a new device type means adding ONE line here.
    # Nothing else needs to change anywhere.
    _device_map = {
        "LIGHT":       SmartLight,
        "THERMOSTAT":  SmartThermostat,
        "DOOR_LOCK":   SmartDoorLock,
        "CAMERA":      SecurityCamera,
        "SPEAKER":     SmartSpeaker,
    }

    @staticmethod
    def create(device_type: str, device_id: str, name: str,
               room: str = None, **kwargs):
        """
        Create and return a SmartDevice of the requested type.

        Parameters:
            device_type : one of the keys in _device_map (case-insensitive)
            device_id   : unique identifier, e.g. "dev_001"
            name        : human-readable name, e.g. "Kitchen Light"
            room        : room name (optional, can be set later)
            **kwargs    : any extra arguments the specific device needs
                          e.g. pin="1234" for a SmartDoorLock

        Returns:
            A SmartDevice subclass instance.

        Raises:
            ValueError if the device_type string is not recognised.

        Example:
            light = DeviceFactory.create("LIGHT", "dev_001", "Hall Light")
            lock  = DeviceFactory.create("DOOR_LOCK", "dev_002", "Front Lock", pin="9999")
        """
        key = device_type.upper().strip()

        if key not in DeviceFactory._device_map:
            supported = ", ".join(DeviceFactory._device_map.keys())
            raise ValueError(
                f"Unknown device type '{device_type}'. "
                f"Supported types: {supported}"
            )

        # Look up the class and call its constructor
        device_class = DeviceFactory._device_map[key]
        device = device_class(device_id, name, room, **kwargs)

        print(f"  🏭 Factory created: {device}")
        return device

    @staticmethod
    def supported_types() -> list:
        """Return a list of all device type strings the factory understands."""
        return list(DeviceFactory._device_map.keys())

    @staticmethod
    def register(type_key: str, device_class) -> None:
        """
        Register a brand-new device type at runtime.

        This is the open/closed principle from SOLID:
          "Open for extension, closed for modification."
        You can add new device types WITHOUT editing this file.

        Example:
            from src.devices.smart_fridge import SmartFridge
            DeviceFactory.register("FRIDGE", SmartFridge)
            fridge = DeviceFactory.create("FRIDGE", "dev_010", "Kitchen Fridge")
        """
        DeviceFactory._device_map[type_key.upper()] = device_class
        print(f"  🏭 Factory: registered new device type '{type_key.upper()}'")
