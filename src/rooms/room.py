"""
room.py
-------
Represents a physical room in the house.

Key OOP Concepts used here:
- Composition : A Room "has" devices — if the room is deleted, its devices go with it
- Encapsulation: The device list is private; we control how devices are added/removed
"""

from typing import List, Optional, TYPE_CHECKING

# TYPE_CHECKING trick: avoids circular imports at runtime while still
# letting type hints work in IDEs
if TYPE_CHECKING:
    from src.devices.smart_device import SmartDevice


class Room:
    """
    A room in the house that contains smart devices.

    Examples of rooms: Kitchen, Bedroom, Living Room, Garage, Bathroom
    """

    # Valid room types — helps catch typos early
    VALID_TYPES = {
        "kitchen", "bedroom", "living_room",
        "garage", "bathroom", "hallway", "office", "other"
    }

    def __init__(self, room_id: str, name: str, room_type: str = "other"):
        """
        Parameters:
            room_id   (str): Unique ID, e.g. "room_001"
            name      (str): Display name, e.g. "Master Bedroom"
            room_type (str): Category from VALID_TYPES
        """
        self._id = room_id
        self._name = name
        self._type = room_type.lower() if room_type.lower() in self.VALID_TYPES else "other"
        self._devices: List["SmartDevice"] = []   # Composition: Room owns its devices

    # -------------------------------------------------------------------------
    # DEVICE MANAGEMENT
    # -------------------------------------------------------------------------

    def add_device(self, device: "SmartDevice") -> None:
        """
        Add a smart device to this room.
        Also updates the device's own room reference.
        """
        if device in self._devices:
            print(f"  ⚠️  {device.name} is already in {self._name}")
            return

        device.room = self._name          # Tell the device which room it's in
        self._devices.append(device)
        print(f"  ➕ {device.name} added to {self._name}")

    def remove_device(self, device_id: str) -> Optional["SmartDevice"]:
        """
        Remove a device by its ID. Returns the removed device (or None).
        """
        for device in self._devices:
            if device.id == device_id:
                self._devices.remove(device)
                device.room = None
                print(f"  ➖ {device.name} removed from {self._name}")
                return device
        print(f"  ⚠️  Device {device_id} not found in {self._name}")
        return None

    def get_device(self, device_id: str) -> Optional["SmartDevice"]:
        """Find and return a device by ID, or None if not found."""
        for device in self._devices:
            if device.id == device_id:
                return device
        return None

    def get_all_devices(self) -> List["SmartDevice"]:
        """Return a copy of the device list (so external code can't modify it directly)."""
        return list(self._devices)

    def turn_all_on(self) -> None:
        """Turn on every device in this room."""
        print(f"\n  💡 Turning ALL devices ON in [{self._name}]")
        for device in self._devices:
            device.turn_on()

    def turn_all_off(self) -> None:
        """Turn off every device in this room."""
        print(f"\n  🌙 Turning ALL devices OFF in [{self._name}]")
        for device in self._devices:
            device.turn_off()

    # -------------------------------------------------------------------------
    # ENERGY
    # -------------------------------------------------------------------------

    def total_energy_consumption(self) -> float:
        """Sum up watts from all devices currently ON in this room."""
        return sum(d.energy_consumption for d in self._devices)

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return self._name

    @property
    def room_type(self) -> str:
        return self._type

    @property
    def device_count(self) -> int:
        return len(self._devices)

    # -------------------------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        return f"Room: {self._name} ({self._type}) | Devices: {len(self._devices)}"

    def __repr__(self) -> str:
        return f"<Room id={self._id!r} name={self._name!r} devices={len(self._devices)}>"
