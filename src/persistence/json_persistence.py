"""
json_persistence.py
-------------------
Saves and loads the full house state to/from a JSON file.

Why JSON?
  - Human-readable: you can open the file in any text editor
  - Easy to debug: if something breaks, you can inspect the save file
  - Lightweight: no database needed

What gets saved:
  - House name and address
  - All rooms (id, name, type)
  - All devices (type, id, name, power state, type-specific settings)
  - All users (id, name, role, email)
  - Automation rules (id, name, trigger, conditions, actions, enabled state)

What gets reconstructed on load:
  - Same house structure — rooms contain the right devices
  - Devices are recreated with their saved state
"""

import json
import os
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.house.house import House


class JsonPersistence:
    """
    Saves and loads a House object to/from a JSON file.

    Usage:
        repo = JsonPersistence("data/my_home.json")
        repo.save(house)

        loaded_house = repo.load()
    """

    def __init__(self, filepath: str = "data/smart_home_save.json"):
        self._filepath = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)

    # ------------------------------------------------------------------
    # SAVE
    # ------------------------------------------------------------------

    def save(self, house: "House") -> bool:
        """
        Serialise the house to JSON and write it to disk.
        Returns True on success, False on failure.
        """
        try:
            data = self._serialise_house(house)
            data["saved_at"] = datetime.now().isoformat()

            with open(self._filepath, "w") as f:
                json.dump(data, f, indent=2)

            print(f"  💾 Saved house state to '{self._filepath}'")
            return True

        except Exception as err:
            print(f"  ❌ Save failed: {err}")
            return False

    def _serialise_house(self, house: "House") -> dict:
        """Convert a House object into a plain dictionary."""
        from src.devices.smart_light      import SmartLight
        from src.devices.smart_thermostat import SmartThermostat
        from src.devices.smart_door_lock  import SmartDoorLock
        from src.devices.security_camera  import SecurityCamera
        from src.devices.smart_speaker    import SmartSpeaker

        rooms_data = []
        for room in house.get_all_rooms():
            devices_data = []

            for device in room.get_all_devices():
                # Common fields every device has
                d = {
                    "id":          device.id,
                    "name":        device.name,
                    "power_state": device.power_state,
                }

                # Type-specific fields
                if isinstance(device, SmartLight):
                    d["device_type"]  = "LIGHT"
                    d["brightness"]   = device.brightness
                    d["colour_mode"]  = device.colour_mode

                elif isinstance(device, SmartThermostat):
                    d["device_type"]     = "THERMOSTAT"
                    d["target_temp"]     = device.target_temperature
                    d["current_temp"]    = device.current_temperature
                    d["eco_mode"]        = device.eco_mode

                elif isinstance(device, SmartDoorLock):
                    d["device_type"]     = "DOOR_LOCK"
                    d["is_locked"]       = device.is_locked
                    d["security_level"]  = device.security_level

                elif isinstance(device, SecurityCamera):
                    d["device_type"]     = "CAMERA"
                    d["motion_detect"]   = device.motion_detection

                elif isinstance(device, SmartSpeaker):
                    d["device_type"]     = "SPEAKER"
                    d["volume"]          = device.volume

                devices_data.append(d)

            rooms_data.append({
                "id":      room.id,
                "name":    room.name,
                "type":    room.room_type,
                "devices": devices_data,
            })

        return {
            "house": {
                "name":    house.name,
                "address": house.address,
                "rooms":   rooms_data,
            }
        }

    # ------------------------------------------------------------------
    # LOAD
    # ------------------------------------------------------------------

    def load(self) -> "House":
        """
        Read the JSON file and reconstruct a House object.
        Returns None if the file doesn't exist or is corrupt.
        """
        if not os.path.exists(self._filepath):
            print(f"  ⚠️  No save file found at '{self._filepath}'")
            return None

        try:
            with open(self._filepath, "r") as f:
                data = json.load(f)

            house = self._deserialise_house(data)
            print(f"  📂 Loaded house state from '{self._filepath}'")
            return house

        except Exception as err:
            print(f"  ❌ Load failed: {err}")
            return None

    def _deserialise_house(self, data: dict) -> "House":
        """Reconstruct a House from a dictionary."""
        from src.house.house          import House
        from src.rooms.room           import Room
        from src.devices.device_factory import DeviceFactory

        house_data = data["house"]
        house = House(house_data["name"], house_data.get("address", ""))

        for room_data in house_data.get("rooms", []):
            room = Room(room_data["id"], room_data["name"], room_data["type"])

            for d in room_data.get("devices", []):
                device_type = d.get("device_type")
                if not device_type:
                    continue

                # Use the factory to recreate the right device class
                kwargs = {}
                if device_type == "DOOR_LOCK":
                    kwargs["pin"] = d.get("pin", "0000")

                device = DeviceFactory.create(
                    device_type, d["id"], d["name"], room.name, **kwargs
                )

                # Restore power state
                if d.get("power_state"):
                    device.turn_on()

                # Restore type-specific state
                from src.devices.smart_light      import SmartLight
                from src.devices.smart_thermostat import SmartThermostat
                from src.devices.smart_speaker    import SmartSpeaker

                if isinstance(device, SmartLight):
                    device.set_brightness(d.get("brightness", 100))

                elif isinstance(device, SmartThermostat):
                    device.set_target_temperature(d.get("target_temp", 21))

                elif isinstance(device, SmartSpeaker):
                    device.set_volume(d.get("volume", 50))

                room.add_device(device)

            house.add_room(room)

        return house

    def file_exists(self) -> bool:
        return os.path.exists(self._filepath)

    def delete_save(self) -> None:
        if self.file_exists():
            os.remove(self._filepath)
            print(f"  🗑️  Save file '{self._filepath}' deleted")
