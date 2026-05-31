"""
main.py
-------
Entry point for the Smart Home Simulator.

Run this file to see the system in action.
Each part of the project will add more features here.
"""

from src.devices.smart_device import SmartDevice   # Abstract base (can't instantiate directly)
from src.rooms.room import Room
from src.house.house import House


# ---------------------------------------------------------------------------
# PART 1 DEMO
# We can't create a SmartDevice directly (it's abstract), but we CAN create
# Rooms and a House. Device types come in Part 2.
# ---------------------------------------------------------------------------

def main():
    print("\n" + "="*50)
    print("   🏠  Smart Home Simulator — Part 1 Demo")
    print("="*50)

    # 1. Create a house
    home = House(name="The Johnson Smart Home", address="42 Maple Avenue")

    # 2. Create some rooms
    kitchen   = Room(room_id="room_001", name="Kitchen",     room_type="kitchen")
    bedroom   = Room(room_id="room_002", name="Master Bedroom", room_type="bedroom")
    living_rm = Room(room_id="room_003", name="Living Room", room_type="living_room")
    garage    = Room(room_id="room_004", name="Garage",      room_type="garage")

    # 3. Add rooms to house
    home.add_room(kitchen)
    home.add_room(bedroom)
    home.add_room(living_rm)
    home.add_room(garage)

    # 4. Print house status
    home.status_report()

    print("\n✅ Part 1 complete: House structure is ready!")
    print("   Next up → Part 2: Smart Device types\n")


if __name__ == "__main__":
    main()
