"""
house.py
--------
The top-level object that holds everything together.

Key OOP Concepts used here:
- Aggregation : House "has" rooms and users — they can exist independently
- Composition : House directly manages its automation rules list
"""

from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.rooms.room import Room
    from src.devices.smart_device import SmartDevice


class House:
    """
    The Smart Home itself.

    Acts as the top-level container for:
    - Rooms (which contain devices)
    - Users
    - Automation rules (added in a later part)

    Think of this as the "blueprint" of the building.
    """

    def __init__(self, name: str, address: str = ""):
        """
        Parameters:
            name    (str): e.g. "Smith Family Home"
            address (str): e.g. "123 Main Street"
        """
        self._name = name
        self._address = address
        self._rooms: List["Room"] = []          # Aggregation: rooms can exist outside
        self._users: List = []                   # Users (expanded in Part 6)
        self._automation_rules: List = []        # Rules (expanded in Part 5)

    # -------------------------------------------------------------------------
    # ROOM MANAGEMENT
    # -------------------------------------------------------------------------

    def add_room(self, room: "Room") -> None:
        """Add a room to the house."""
        if any(r.id == room.id for r in self._rooms):
            print(f"  ⚠️  Room '{room.name}' already exists in the house")
            return
        self._rooms.append(room)
        print(f"  🏠 Room '{room.name}' added to {self._name}")

    def remove_room(self, room_id: str) -> Optional["Room"]:
        """Remove a room by ID. Returns the removed room or None."""
        for room in self._rooms:
            if room.id == room_id:
                self._rooms.remove(room)
                print(f"  🗑️  Room '{room.name}' removed from {self._name}")
                return room
        print(f"  ⚠️  Room {room_id} not found")
        return None

    def get_room(self, room_id: str) -> Optional["Room"]:
        """Find a room by ID."""
        for room in self._rooms:
            if room.id == room_id:
                return room
        return None

    def get_room_by_name(self, name: str) -> Optional["Room"]:
        """Find a room by its display name (case-insensitive)."""
        for room in self._rooms:
            if room.name.lower() == name.lower():
                return room
        return None

    def get_all_rooms(self) -> List["Room"]:
        """Return all rooms."""
        return list(self._rooms)

    # -------------------------------------------------------------------------
    # DEVICE SHORTCUTS — find any device anywhere in the house
    # -------------------------------------------------------------------------

    def get_all_devices(self) -> List["SmartDevice"]:
        """Return every device from every room."""
        devices = []
        for room in self._rooms:
            devices.extend(room.get_all_devices())
        return devices

    def find_device(self, device_id: str) -> Optional["SmartDevice"]:
        """Search all rooms for a device by ID."""
        for room in self._rooms:
            device = room.get_device(device_id)
            if device:
                return device
        return None

    # -------------------------------------------------------------------------
    # ENERGY OVERVIEW
    # -------------------------------------------------------------------------

    def total_energy_consumption(self) -> float:
        """Sum energy consumption across every room."""
        return sum(room.total_energy_consumption() for room in self._rooms)

    # -------------------------------------------------------------------------
    # STATUS REPORT
    # -------------------------------------------------------------------------

    def status_report(self) -> None:
        """Print a full overview of the house."""
        print(f"\n{'='*50}")
        print(f"  🏡 {self._name}")
        if self._address:
            print(f"  📍 {self._address}")
        print(f"  Rooms   : {len(self._rooms)}")
        print(f"  Devices : {len(self.get_all_devices())}")
        print(f"  Energy  : {self.total_energy_consumption():.1f} W")
        print(f"{'='*50}")

        for room in self._rooms:
            print(f"\n  📦 {room}")
            for device in room.get_all_devices():
                print(f"      • {device}")

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def name(self) -> str:
        return self._name

    @property
    def address(self) -> str:
        return self._address

    @property
    def rooms(self) -> List["Room"]:
        return list(self._rooms)

    # -------------------------------------------------------------------------
    # DISPLAY
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        return f"House: {self._name} | Rooms: {len(self._rooms)}"

    def __repr__(self) -> str:
        return f"<House name={self._name!r} rooms={len(self._rooms)}>"
