"""
main.py  —  Full System Demo
All parts working together: devices, sensors, automation, users,
notifications, energy monitoring, and persistence.
"""

from src.devices.device_factory          import DeviceFactory
from src.sensors.motion_sensor           import MotionSensor
from src.sensors.temperature_sensor      import TemperatureSensor
from src.sensors.smoke_sensor            import SmokeSensor
from src.sensors.door_sensor             import DoorSensor
from src.automation.automation_rule      import AutomationRule
from src.automation.automation_engine    import AutomationEngine
from src.automation.event_bus            import EventBus
from src.users.user                      import Owner, Guest, Technician, Permission
from src.notifications.notification_service import NotificationService
from src.energy.energy_monitor           import EnergyMonitor
from src.energy.energy_strategy          import EnergyManager
from src.persistence.json_persistence    import JsonPersistence
from src.house.logger                    import Logger
from src.rooms.room                      import Room
from src.house.house                     import House


def setup_house():
    """Build and return a fully configured smart home."""
    home    = House("The Johnson Smart Home", "42 Maple Avenue")
    hallway = Room("room_001", "Hallway",      "other")
    kitchen = Room("room_002", "Kitchen",      "kitchen")
    bedroom = Room("room_003", "Bedroom",      "bedroom")
    garage  = Room("room_004", "Garage",       "garage")

    home.add_room(hallway)
    home.add_room(kitchen)
    home.add_room(bedroom)
    home.add_room(garage)

    # Create devices via factory
    hall_light  = DeviceFactory.create("LIGHT",     "dev_001", "Hallway Light",   "Hallway")
    bed_light   = DeviceFactory.create("LIGHT",     "dev_002", "Bedroom Light",   "Bedroom")
    thermo      = DeviceFactory.create("THERMOSTAT","dev_003", "Main Thermostat", "Kitchen")
    front_lock  = DeviceFactory.create("DOOR_LOCK", "dev_004", "Front Door Lock", "Hallway", pin="1234")
    garage_lock = DeviceFactory.create("DOOR_LOCK", "dev_005", "Garage Lock",     "Garage",  pin="1234")
    cam         = DeviceFactory.create("CAMERA",    "dev_006", "Hallway Camera",  "Hallway")
    speaker     = DeviceFactory.create("SPEAKER",   "dev_007", "Kitchen Speaker", "Kitchen")

    hallway.add_device(hall_light)
    hallway.add_device(front_lock)
    hallway.add_device(cam)
    kitchen.add_device(thermo)
    kitchen.add_device(speaker)
    bedroom.add_device(bed_light)
    garage.add_device(garage_lock)

    # Start devices
    for dev in home.get_all_devices():
        dev.turn_on()

    return home


def setup_automation(home):
    """Register all automation rules and return the engine."""
    notif_service = NotificationService()
    engine        = AutomationEngine(home, notif_service)
    bus           = EventBus()

    # Rule 1: motion in hallway → turn on hallway light + camera records
    rule1 = AutomationRule(
        rule_id="rule_001", name="Hallway Motion → Light On",
        trigger_event="motion_detected",
        conditions=[{"field": "room", "operator": "equals", "value": "Hallway"}],
        actions=[
            {"type": "turn_on", "device_id": "dev_001"},
            {"type": "start_recording", "device_id": "dev_006"},
            {"type": "notify", "message": "Motion in hallway", "priority": "normal"},
        ]
    )

    # Rule 2: no motion → lights off
    rule2 = AutomationRule(
        rule_id="rule_002", name="No Motion → Lights Off",
        trigger_event="motion_cleared",
        actions=[
            {"type": "turn_off", "device_id": "dev_001"},
            {"type": "notify", "message": "Hallway clear — lights off", "priority": "low"},
        ]
    )

    # Rule 3: smoke alarm → unlock all doors
    rule3 = AutomationRule(
        rule_id="rule_003", name="Fire Alarm → Unlock Doors",
        trigger_event="alarm_triggered",
        actions=[
            {"type": "unlock", "device_id": "dev_004", "pin": "1234"},
            {"type": "unlock", "device_id": "dev_005", "pin": "1234"},
            {"type": "notify", "message": "FIRE! All doors unlocked for evacuation",
             "priority": "critical"},
        ]
    )

    # Rule 4: temperature too low → thermostat heats up
    rule4 = AutomationRule(
        rule_id="rule_004", name="Cold Alert → Heat Up",
        trigger_event="temperature_too_low",
        actions=[
            {"type": "set_temperature", "device_id": "dev_003", "value": 23.0},
            {"type": "notify", "message": "Temperature too low — thermostat adjusted",
             "priority": "high"},
        ]
    )

    engine.add_rule(rule1)
    engine.add_rule(rule2)
    engine.add_rule(rule3)
    engine.add_rule(rule4)

    return engine, notif_service


def wire_sensors(home, sensors):
    """Connect every sensor to the EventBus so the engine receives events."""
    bus = EventBus()
    def publish(event):
        bus.publish(event["event_type"], event)
    for sensor in sensors:
        sensor.add_listener(publish)


def main():
    print("\n" + "="*55)
    print("   🏠  Smart Home Simulator — Full System Demo")
    print("="*55)

    # ----------------------------------------------------------------
    # BUILD HOUSE + AUTOMATION
    # ----------------------------------------------------------------
    home              = setup_house()
    engine, notifs    = setup_automation(home)

    # ----------------------------------------------------------------
    # USERS
    # ----------------------------------------------------------------
    print("\n--- 👤 USER SYSTEM ---")
    alice  = Owner     ("u_001", "Alice",  "alice@home.com")
    bob    = Guest     ("u_002", "Bob",    "bob@guest.com")
    carlos = Technician("u_003", "Carlos", "carlos@tech.com")

    bob.assign_device("dev_007")   # Bob can only use the kitchen speaker

    print(f"  {alice}")
    print(f"  {bob}")
    print(f"  {carlos}")

    # Permission check
    print(f"\n  Alice can manage devices : {alice.can_perform(Permission.MANAGE_DEVICES)}")
    print(f"  Bob   can manage devices : {bob.can_perform(Permission.MANAGE_DEVICES)}")
    print(f"  Bob   can use dev_007    : {bob.can_use_device('dev_007')}")
    print(f"  Carlos can run diagnostics: {carlos.can_perform(Permission.RUN_DIAGNOSTICS)}")

    # Technician diagnostic
    camera = home.find_device("dev_006")
    carlos.run_diagnostic(camera)

    # ----------------------------------------------------------------
    # SENSORS + SCENARIOS
    # ----------------------------------------------------------------
    print("\n--- 🚦 SETTING UP SENSORS ---")
    motion_sen = MotionSensor      ("sen_001", "Hallway Motion", "Hallway")
    temp_sen   = TemperatureSensor ("sen_002", "Kitchen Temp",   "Kitchen")
    smoke_sen  = SmokeSensor       ("sen_003", "Kitchen Smoke",  "Kitchen")
    door_sen   = DoorSensor        ("sen_004", "Front Door",     "Hallway")

    wire_sensors(home, [motion_sen, temp_sen, smoke_sen, door_sen])
    engine.list_rules()

    print("\n--- 🏃 SCENARIO 1: Motion in hallway ---")
    motion_sen.detect_motion("Hallway")

    print("\n--- 🕊️  SCENARIO 2: Hallway clears ---")
    motion_sen.clear_motion()

    print("\n--- 🌡️  SCENARIO 3: Kitchen gets cold ---")
    temp_sen.read_temperature(12.0)

    print("\n--- 💨 SCENARIO 4: Fire alarm ---")
    smoke_sen.detect_smoke(150.0, carbon_monoxide=True)

    # ----------------------------------------------------------------
    # NOTIFICATIONS INBOX
    # ----------------------------------------------------------------
    print()
    notifs.print_all()

    # ----------------------------------------------------------------
    # ENERGY REPORT
    # ----------------------------------------------------------------
    monitor = EnergyMonitor(home)
    monitor.generate_report()

    # ----------------------------------------------------------------
    # ENERGY STRATEGY
    # ----------------------------------------------------------------
    print("\n--- ⚡ SWITCHING TO ECO MODE ---")
    mgr = EnergyManager()
    mgr.set_strategy("eco")
    mgr.apply(home.get_all_devices())

    # ----------------------------------------------------------------
    # PERSISTENCE
    # ----------------------------------------------------------------
    print("\n--- 💾 SAVING AND RELOADING HOUSE ---")
    repo = JsonPersistence("data/smart_home_save.json")
    repo.save(home)

    loaded = repo.load()
    if loaded:
        print(f"  Reloaded: {loaded.name} "
              f"| {len(loaded.get_all_rooms())} rooms "
              f"| {len(loaded.get_all_devices())} devices")

    # ----------------------------------------------------------------
    # FINAL LOG
    # ----------------------------------------------------------------
    print("\n--- 📋 LOG SNAPSHOT ---")
    Logger().print_recent(8)

    print("\n✅ Full system demo complete!\n")
    print("   Run tests with:  pytest tests/ -v\n")


if __name__ == "__main__":
    main()
