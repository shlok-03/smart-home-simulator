"""
main.py  —  Part 4 Demo
Demonstrating all 4 required design patterns.
"""

from src.devices.device_factory      import DeviceFactory
from src.house.logger                import Logger
from src.automation.event_bus        import EventBus
from src.energy.energy_strategy      import EnergyManager
from src.sensors.motion_sensor       import MotionSensor
from src.sensors.smoke_sensor        import SmokeSensor
from src.rooms.room  import Room
from src.house.house import House


def main():
    print("\n" + "="*55)
    print("   🏠  Smart Home Simulator — Part 4 Demo")
    print("        Design Patterns")
    print("="*55)

    # ----------------------------------------------------------------
    # PATTERN 1 — FACTORY
    # Create devices without knowing their class names
    # ----------------------------------------------------------------
    print("\n--- 🏭 PATTERN 1: FACTORY ---")

    home    = House("The Johnson Smart Home", "42 Maple Avenue")
    hallway = Room("room_001", "Hallway",     "other")
    kitchen = Room("room_002", "Kitchen",     "kitchen")
    home.add_room(hallway)
    home.add_room(kitchen)

    # The factory handles choosing the right class
    hall_light = DeviceFactory.create("LIGHT",      "dev_001", "Hallway Light", "Hallway")
    thermo     = DeviceFactory.create("THERMOSTAT", "dev_002", "Kitchen Thermostat", "Kitchen")
    front_lock = DeviceFactory.create("DOOR_LOCK",  "dev_003", "Front Door Lock", "Hallway", pin="1234")
    cam        = DeviceFactory.create("CAMERA",     "dev_004", "Hallway Camera", "Hallway")
    speaker    = DeviceFactory.create("SPEAKER",    "dev_005", "Living Room Speaker", "Hallway")

    hallway.add_device(hall_light)
    hallway.add_device(front_lock)
    hallway.add_device(cam)
    kitchen.add_device(thermo)
    kitchen.add_device(speaker)

    print(f"\n  Supported device types: {DeviceFactory.supported_types()}")

    # ----------------------------------------------------------------
    # PATTERN 2 — SINGLETON (Logger)
    # Both variables point to the exact same object
    # ----------------------------------------------------------------
    print("\n--- 📋 PATTERN 2: SINGLETON (Logger) ---")

    log_a = Logger()
    log_b = Logger()

    print(f"  log_a is log_b: {log_a is log_b}")   # must print True

    log_a.info("main",     "Smart home system started")
    log_a.info("Factory",  "Created 5 devices via DeviceFactory")
    log_b.warning("main",  "This was logged via log_b — same object as log_a")

    print(f"  Total log entries: {log_a.total_entries()}")
    log_a.print_recent(3)

    # ----------------------------------------------------------------
    # PATTERN 3 — OBSERVER (EventBus)
    # Sensors publish; handlers subscribe — they never meet directly
    # ----------------------------------------------------------------
    print("\n--- 📡 PATTERN 3: OBSERVER (EventBus) ---")

    bus           = EventBus()
    motion_sensor = MotionSensor("sen_001", "Hallway Motion", "Hallway")
    smoke_sensor  = SmokeSensor( "sen_002", "Kitchen Smoke",  "Kitchen")

    # Subscriber 1: the automation handler
    def on_motion_event(event):
        print(f"  [AutomationEngine] reacting to '{event['event_type']}'")
        if event["event_type"] == "motion_detected":
            hall_light.turn_on()

    # Subscriber 2: the logger (uses wildcard — hears everything)
    def log_all_events(event):
        Logger().info("EventBus", f"{event['event_type']} from {event.get('sensor_name','?')}")

    # Subscriber 3: emergency handler
    def on_smoke_event(event):
        if event["event_type"] == "alarm_triggered":
            print(f"  [EmergencyHandler] 🚨 Unlocking all doors!")
            front_lock.unlock("emergency_system", pin="1234")

    bus.subscribe("motion_detected", on_motion_event)
    bus.subscribe("alarm_triggered", on_smoke_event)
    bus.subscribe_all(log_all_events)   # wildcard — catches every topic

    # Wire sensors to the event bus (sensors publish, bus routes)
    def publish_sensor_event(event):
        bus.publish(event["event_type"], event)

    motion_sensor.add_listener(publish_sensor_event)
    smoke_sensor.add_listener(publish_sensor_event)

    # Trigger events — watch the bus route them automatically
    print()
    hall_light.turn_on()
    cam.turn_on()
    motion_sensor.detect_motion("Hallway")
    smoke_sensor.detect_smoke(150.0, carbon_monoxide=True)

    # ----------------------------------------------------------------
    # PATTERN 4 — STRATEGY (EnergyManager)
    # Swap the whole energy behaviour with one line
    # ----------------------------------------------------------------
    print("\n--- ⚡ PATTERN 4: STRATEGY (EnergyManager) ---")

    manager  = EnergyManager()
    all_devs = home.get_all_devices()

    # Turn everything on first so strategies have something to work with
    for d in all_devs:
        d.turn_on()

    manager.set_strategy("eco")
    manager.apply(all_devs)

    manager.set_strategy("night")
    manager.apply(all_devs)

    manager.set_strategy("away")
    manager.apply(all_devs)

    # Show final log
    print("\n--- 📋 FINAL LOG SNAPSHOT ---")
    Logger().print_recent(6)

    print(f"\n✅ Part 4 complete: All 4 design patterns demonstrated!")
    print(f"   Next → Part 5: Automation Engine 🤖\n")


if __name__ == "__main__":
    main()
