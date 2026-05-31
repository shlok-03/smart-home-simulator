"""
main.py  —  Part 3 Demo
Sensors detecting events and notifying devices via listeners.
"""

from src.devices.smart_light      import SmartLight
from src.devices.smart_thermostat import SmartThermostat
from src.devices.smart_door_lock  import SmartDoorLock
from src.devices.security_camera  import SecurityCamera
from src.sensors.motion_sensor      import MotionSensor
from src.sensors.temperature_sensor import TemperatureSensor
from src.sensors.smoke_sensor       import SmokeSensor
from src.sensors.door_sensor        import DoorSensor
from src.rooms.room  import Room
from src.house.house import House


def main():
    print("\n" + "="*55)
    print("   🏠  Smart Home Simulator — Part 3 Demo")
    print("="*55)

    # ----------------------------------------------------------------
    # Build house + rooms
    # ----------------------------------------------------------------
    home    = House("The Johnson Smart Home", "42 Maple Avenue")
    hallway = Room("room_001", "Hallway",     "other")
    kitchen = Room("room_002", "Kitchen",     "kitchen")
    home.add_room(hallway)
    home.add_room(kitchen)

    # ----------------------------------------------------------------
    # Create devices
    # ----------------------------------------------------------------
    hall_light = SmartLight("dev_001", "Hallway Light")
    front_lock = SmartDoorLock("dev_002", "Front Door Lock", pin="1234")
    cam        = SecurityCamera("dev_003", "Hallway Camera")
    thermo     = SmartThermostat("dev_004", "Kitchen Thermostat")

    hallway.add_device(hall_light)
    hallway.add_device(front_lock)
    hallway.add_device(cam)
    kitchen.add_device(thermo)

    # ----------------------------------------------------------------
    # Create sensors
    # ----------------------------------------------------------------
    motion_sensor = MotionSensor("sen_001", "Hallway Motion", "Hallway")
    temp_sensor   = TemperatureSensor("sen_002", "Kitchen Temp", "Kitchen",
                                      low_threshold=15.0, high_threshold=28.0)
    smoke_sensor  = SmokeSensor("sen_003", "Kitchen Smoke", "Kitchen")
    door_sensor   = DoorSensor("sen_004",  "Front Door Sensor", "Hallway")

    # ----------------------------------------------------------------
    # OBSERVER PATTERN — wire sensors to device reactions
    #
    # Instead of the sensor knowing about the light directly,
    # we register a small "reaction" function as a listener.
    # The sensor just fires an event; the function decides what to do.
    # ----------------------------------------------------------------

    # When motion is detected → turn on the hallway light + start camera
    def on_motion(event):
        if event["event_type"] == "motion_detected":
            hall_light.turn_on()
            cam.trigger_motion_alert(event["location"])
        elif event["event_type"] == "motion_cleared":
            hall_light.turn_off()

    # When temperature changes → tell thermostat the new reading
    def on_temperature(event):
        if event["event_type"] == "temperature_changed":
            thermo.update_current_temperature(event["temperature"])

    # When smoke is detected at alarm level → unlock door for escape
    def on_smoke(event):
        if event["event_type"] == "alarm_triggered":
            print("  🚨 EMERGENCY: unlocking front door for evacuation!")
            front_lock.unlock("emergency_system", pin="1234")

    # When front door opens at night → alert
    def on_door(event):
        if event["event_type"] == "door_opened":
            print(f"  🔔 ALERT: Front door was opened by {event['opened_by']}")

    # Register the listeners
    motion_sensor.add_listener(on_motion)
    temp_sensor.add_listener(on_temperature)
    smoke_sensor.add_listener(on_smoke)
    door_sensor.add_listener(on_door)

    # ----------------------------------------------------------------
    # Turn on devices
    # ----------------------------------------------------------------
    hall_light.turn_on()
    hall_light.turn_off()   # start off — motion will turn it on
    front_lock.turn_on()
    cam.turn_on()
    thermo.turn_on()

    # ----------------------------------------------------------------
    # Simulate events
    # ----------------------------------------------------------------

    print("\n--- 🏃 SCENARIO 1: Motion in hallway ---")
    motion_sensor.detect_motion("Hallway")

    print("\n--- 🕊️  SCENARIO 2: Hallway goes quiet ---")
    motion_sensor.clear_motion()

    print("\n--- 🌡️  SCENARIO 3: Kitchen gets cold ---")
    temp_sensor.read_temperature(12.0)   # below 15°C threshold
    temp_sensor.read_temperature(18.0)   # back to normal

    print("\n--- 💨 SCENARIO 4: Smoke alarm in kitchen ---")
    smoke_sensor.detect_smoke(120.0, carbon_monoxide=True)

    print("\n--- 🚪 SCENARIO 5: Someone opens the front door ---")
    door_sensor.open("Alice")
    door_sensor.close("Alice")

    # ----------------------------------------------------------------
    # Show all sensor statuses
    # ----------------------------------------------------------------
    print("\n--- 📊 SENSOR STATUS REPORT ---")
    for sensor in [motion_sensor, temp_sensor, smoke_sensor, door_sensor]:
        status = sensor.get_status()
        print(f"  {status['type']:<22} | room: {status['room']:<12} | active: {status['active']}")

    print("\n✅ Part 3 complete: Sensors wired up with the Observer pattern!")
    print("   Next → Part 4: Design Patterns (Factory, Singleton, Strategy) 🏗️\n")


if __name__ == "__main__":
    main()
