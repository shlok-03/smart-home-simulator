"""
main.py
-------
Entry point for the Smart Home Simulator.
Updated each part to showcase new features.
"""

from src.devices.smart_light      import SmartLight
from src.devices.smart_thermostat import SmartThermostat
from src.devices.smart_door_lock  import SmartDoorLock
from src.devices.security_camera  import SecurityCamera
from src.devices.smart_speaker    import SmartSpeaker
from src.rooms.room  import Room
from src.house.house import House


def main():
    print("\n" + "="*55)
    print("   🏠  Smart Home Simulator — Part 2 Demo")
    print("="*55)

    # ----------------------------------------------------------------
    # 1. Build the house
    # ----------------------------------------------------------------
    home      = House("The Johnson Smart Home", "42 Maple Avenue")
    hallway   = Room("room_001", "Hallway",      "other")
    kitchen   = Room("room_002", "Kitchen",      "kitchen")
    bedroom   = Room("room_003", "Master Bedroom","bedroom")
    living_rm = Room("room_004", "Living Room",  "living_room")

    home.add_room(hallway)
    home.add_room(kitchen)
    home.add_room(bedroom)
    home.add_room(living_rm)

    # ----------------------------------------------------------------
    # 2. Create devices  (Inheritance — all extend SmartDevice)
    # ----------------------------------------------------------------
    hall_light  = SmartLight     ("dev_001", "Hallway Light",    "Hallway")
    thermo      = SmartThermostat("dev_002", "Main Thermostat",  "Living Room")
    front_lock  = SmartDoorLock  ("dev_003", "Front Door Lock",  "Hallway", pin="1234")
    cam         = SecurityCamera ("dev_004", "Front Camera",     "Hallway")
    speaker     = SmartSpeaker   ("dev_005", "Living Room Speaker","Living Room")

    # ----------------------------------------------------------------
    # 3. Place devices in rooms  (Composition)
    # ----------------------------------------------------------------
    hallway.add_device(hall_light)
    hallway.add_device(front_lock)
    hallway.add_device(cam)
    living_rm.add_device(thermo)
    living_rm.add_device(speaker)

    # ----------------------------------------------------------------
    # 4. Demo SmartLight
    # ----------------------------------------------------------------
    print("\n--- 💡 SMART LIGHT ---")
    hall_light.turn_on()
    hall_light.set_brightness(60)
    hall_light.set_colour("warm")
    hall_light.set_auto_shutoff(30)
    print(hall_light)

    # ----------------------------------------------------------------
    # 5. Demo SmartThermostat
    # ----------------------------------------------------------------
    print("\n--- 🌡️  THERMOSTAT ---")
    thermo.turn_on()
    thermo.update_current_temperature(16.0)
    thermo.set_target_temperature(22.0)
    thermo.enable_eco_mode()
    print(thermo)

    # ----------------------------------------------------------------
    # 6. Demo SmartDoorLock
    # ----------------------------------------------------------------
    print("\n--- 🔒 DOOR LOCK ---")
    front_lock.turn_on()
    front_lock.unlock("Alice", pin="wrong")   # should fail
    front_lock.unlock("Alice", pin="1234")    # should succeed
    front_lock.lock("system")
    front_lock.print_access_history()

    # ----------------------------------------------------------------
    # 7. Demo SecurityCamera
    # ----------------------------------------------------------------
    print("\n--- 📷 SECURITY CAMERA ---")
    cam.turn_on()
    cam.trigger_motion_alert("Hallway")
    cam.stop_recording()
    print(cam)

    # ----------------------------------------------------------------
    # 8. Demo SmartSpeaker  (method chaining)
    # ----------------------------------------------------------------
    print("\n--- 🔊 SMART SPEAKER ---")
    speaker.turn_on()
    speaker.set_volume(70).play("Morning Jazz")   # method chaining!
    speaker.voice_command("volume up")
    speaker.voice_command("pause")

    # ----------------------------------------------------------------
    # 9. Polymorphism demo: loop over mixed device list
    # ----------------------------------------------------------------
    print("\n--- 🔄 POLYMORPHISM: get_status() on every device ---")
    all_devices = home.get_all_devices()
    for device in all_devices:
        status = device.get_status()   # same call, different output per type!
        print(f"  {status['type']:<20} | power={status['power']} | energy={status['energy_w']}W")

    # ----------------------------------------------------------------
    # 10. Full house status
    # ----------------------------------------------------------------
    home.status_report()

    print("\n✅ Part 2 complete: All 5 device types working!")
    print("   Next → Part 3: Sensors 🚨\n")


if __name__ == "__main__":
    main()
