"""
smart_device.py
---------------
This is the FOUNDATION of the entire project.

All smart devices (lights, thermostats, cameras, etc.) will inherit from this class.

Key OOP Concepts used here:
- Abstraction   : SmartDevice is abstract — you can't create a plain "SmartDevice",
                  only specific types like SmartLight
- Encapsulation : All attributes are private (start with _), accessed via properties
- Inheritance   : Every device type will be a subclass of this
"""

from abc import ABC, abstractmethod   # ABC = Abstract Base Class tools
from datetime import datetime


class SmartDevice(ABC):
    """
    Abstract base class for every smart device in the house.

    Think of this as a "contract": any device that inherits from SmartDevice
    MUST implement the abstract methods. This guarantees every device
    behaves consistently.
    """

    def __init__(self, device_id: str, name: str, room: str = None):
        """
        Constructor — runs when a new device is created.

        Parameters:
            device_id (str): A unique identifier, e.g. "light_001"
            name      (str): A human-readable name, e.g. "Kitchen Light"
            room      (str): The room it belongs to (can be set later)
        """
        # The underscore _ means these are PRIVATE — external code should
        # use the properties below, not access these directly.
        self._id = device_id
        self._name = name
        self._power_state = False          # All devices start OFF
        self._room = room                  # Room name (string)
        self._energy_consumption = 0.0     # Watts currently consumed
        self._created_at = datetime.now()  # When the device was registered

    # -------------------------------------------------------------------------
    # ABSTRACT METHOD — every subclass MUST override this
    # -------------------------------------------------------------------------

    @abstractmethod
    def get_status(self) -> dict:
        """
        Return a dictionary describing the device's current state.

        Every device type will have different fields, so each subclass
        defines its own version of this method (polymorphism).
        """
        pass  # No body here — subclasses fill this in

    # -------------------------------------------------------------------------
    # CONCRETE METHODS — shared by ALL devices (no need to override)
    # -------------------------------------------------------------------------

    def turn_on(self):
        """Power the device on."""
        self._power_state = True
        print(f"  ✅ [{self._name}] turned ON")

    def turn_off(self):
        """Power the device off and reset energy draw to zero."""
        self._power_state = False
        self._energy_consumption = 0.0
        print(f"  🔴 [{self._name}] turned OFF")

    def toggle(self):
        """Switch between ON and OFF."""
        if self._power_state:
            self.turn_off()
        else:
            self.turn_on()

    # -------------------------------------------------------------------------
    # PROPERTIES — controlled read (and sometimes write) access to private data
    # Using @property instead of public variables gives us control:
    # we can add validation, logging, or make things read-only.
    # -------------------------------------------------------------------------

    @property
    def id(self) -> str:
        """Read-only: device's unique ID."""
        return self._id

    @property
    def name(self) -> str:
        """Read-only: device's display name."""
        return self._name

    @property
    def power_state(self) -> bool:
        """Read-only: True = ON, False = OFF."""
        return self._power_state

    @property
    def room(self) -> str:
        """The room this device is assigned to."""
        return self._room

    @room.setter
    def room(self, room_name: str):
        """Allow the room to be changed (e.g. device moved to another room)."""
        self._room = room_name

    @property
    def energy_consumption(self) -> float:
        """Current energy draw in watts."""
        return self._energy_consumption

    @property
    def created_at(self) -> datetime:
        """When this device was registered in the system."""
        return self._created_at

    # -------------------------------------------------------------------------
    # DUNDER (magic) METHODS — control how the object prints
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        """User-friendly string: used by print()."""
        status = "ON 🟢" if self._power_state else "OFF 🔴"
        room_label = self._room if self._room else "Unassigned"
        return f"{self._name} ({self.__class__.__name__}) | {status} | Room: {room_label}"

    def __repr__(self) -> str:
        """Developer-friendly string: used in logs and debugging."""
        return f"<{self.__class__.__name__} id={self._id!r} name={self._name!r}>"
