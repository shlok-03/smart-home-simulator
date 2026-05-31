"""
test_sensors_automation_persistence.py
---------------------------------------
Unit tests for sensors, automation rules/engine, and JSON persistence.

Run with:  pytest tests/ -v
"""

import pytest
import os
from src.sensors.motion_sensor      import MotionSensor
from src.sensors.smoke_sensor       import SmokeSensor
from src.sensors.temperature_sensor import TemperatureSensor
from src.sensors.door_sensor        import DoorSensor
from src.automation.automation_rule  import AutomationRule
from src.devices.smart_light        import SmartLight
from src.devices.smart_door_lock    import SmartDoorLock
from src.rooms.room                 import Room
from src.house.house                import House
from src.house.logger               import Logger
from src.users.user                 import Owner, Guest, Technician, Permission
from src.persistence.json_persistence import JsonPersistence


# ===========================================================================
# Sensors
# ===========================================================================

class TestMotionSensor:

    def test_detect_motion_fires_event(self):
        """Listener should be called with correct event type."""
        sensor   = MotionSensor("ts_m1", "Test Motion")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.detect_motion("Hallway")
        assert len(received) == 1
        assert received[0]["event_type"] == "motion_detected"

    def test_clear_motion_fires_event(self):
        sensor   = MotionSensor("ts_m2", "Test Motion")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.detect_motion()
        sensor.clear_motion()
        event_types = [e["event_type"] for e in received]
        assert "motion_cleared" in event_types

    def test_deactivated_sensor_ignores_motion(self):
        sensor   = MotionSensor("ts_m3", "Test Motion")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.deactivate()
        sensor.detect_motion()
        assert len(received) == 0   # nothing fired

    def test_detection_count_increments(self):
        sensor = MotionSensor("ts_m4", "Test Motion")
        sensor.detect_motion()
        sensor.clear_motion()
        sensor.detect_motion()
        assert sensor.detection_count == 2


class TestSmokeSensor:

    def test_clear_air_does_not_fire_smoke_event(self):
        sensor   = SmokeSensor("ts_s1", "Test Smoke")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.detect_smoke(5.0)   # below LEVEL_CLEAN (10)
        smoke_events = [e for e in received if e["event_type"] == "smoke_detected"]
        assert len(smoke_events) == 0

    def test_high_smoke_triggers_alarm(self):
        sensor   = SmokeSensor("ts_s2", "Test Smoke")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.detect_smoke(150.0)   # above LEVEL_DANGER (100)
        alarm_events = [e for e in received if e["event_type"] == "alarm_triggered"]
        assert len(alarm_events) == 1


class TestTemperatureSensor:

    def test_low_temp_fires_too_low_event(self):
        sensor   = TemperatureSensor("ts_t1", "Test Temp", low_threshold=15.0)
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.read_temperature(10.0)
        event_types = [e["event_type"] for e in received]
        assert "temperature_too_low" in event_types

    def test_normal_temp_fires_normal_event_after_alert(self):
        sensor   = TemperatureSensor("ts_t2", "Test Temp",
                                     low_threshold=15.0, high_threshold=28.0)
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.read_temperature(10.0)   # trigger alert
        sensor.read_temperature(20.0)   # back to normal
        event_types = [e["event_type"] for e in received]
        assert "temperature_normal" in event_types


class TestDoorSensor:

    def test_open_fires_door_opened(self):
        sensor   = DoorSensor("ts_d1", "Test Door")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.open("alice")
        assert received[0]["event_type"] == "door_opened"

    def test_close_fires_door_closed(self):
        sensor   = DoorSensor("ts_d2", "Test Door")
        received = []
        sensor.add_listener(lambda e: received.append(e))

        sensor.open("alice")
        sensor.close("alice")
        event_types = [e["event_type"] for e in received]
        assert "door_closed" in event_types

    def test_open_count_tracks_opens(self):
        sensor = DoorSensor("ts_d3", "Test Door")
        sensor.open("alice")
        sensor.close("alice")
        sensor.open("bob")
        assert sensor.open_count == 2


# ===========================================================================
# Automation Rules
# ===========================================================================

class TestAutomationRule:

    def test_rule_matches_correct_event(self):
        rule = AutomationRule(
            rule_id="r_001", name="Test Rule",
            trigger_event="motion_detected",
            actions=[{"type": "turn_on", "device_id": "d1"}]
        )
        event = {"event_type": "motion_detected", "room": "Hallway"}
        assert rule.matches(event) is True

    def test_rule_does_not_match_wrong_event(self):
        rule = AutomationRule(
            rule_id="r_002", name="Test Rule",
            trigger_event="motion_detected",
            actions=[]
        )
        event = {"event_type": "smoke_detected"}
        assert rule.matches(event) is False

    def test_disabled_rule_never_matches(self):
        rule = AutomationRule(
            rule_id="r_003", name="Test Rule",
            trigger_event="motion_detected",
            actions=[], enabled=False
        )
        event = {"event_type": "motion_detected"}
        assert rule.matches(event) is False

    def test_condition_room_equals(self):
        rule = AutomationRule(
            rule_id="r_004", name="Test Rule",
            trigger_event="motion_detected",
            conditions=[{"field": "room", "operator": "equals", "value": "Hallway"}],
            actions=[]
        )
        matching_event = {"event_type": "motion_detected", "room": "Hallway"}
        wrong_event    = {"event_type": "motion_detected", "room": "Kitchen"}

        assert rule.matches(matching_event) is True
        assert rule.matches(wrong_event)    is False

    def test_condition_greater_than(self):
        rule = AutomationRule(
            rule_id="r_005", name="Test Rule",
            trigger_event="smoke_detected",
            conditions=[{"field": "level", "operator": "greater_than", "value": 30}],
            actions=[]
        )
        high_smoke = {"event_type": "smoke_detected", "level": 50}
        low_smoke  = {"event_type": "smoke_detected", "level": 10}

        assert rule.matches(high_smoke) is True
        assert rule.matches(low_smoke)  is False

    def test_execution_count_increments(self):
        rule = AutomationRule("r_006", "Test Rule", "motion_detected", [])
        rule.record_execution()
        rule.record_execution()
        assert rule.execution_count == 2


# ===========================================================================
# Singleton — Logger
# ===========================================================================

class TestSingletonLogger:

    def test_logger_is_same_instance(self):
        a = Logger()
        b = Logger()
        assert a is b   # same object in memory

    def test_log_entries_shared(self):
        Logger().clear()
        Logger().info("test", "message one")
        # Access through a second reference
        count = Logger().total_entries()
        assert count >= 1


# ===========================================================================
# User Permissions
# ===========================================================================

class TestUserPermissions:

    def test_owner_can_manage_devices(self):
        owner = Owner("u_001", "Alice")
        assert owner.can_perform(Permission.MANAGE_DEVICES) is True

    def test_guest_cannot_manage_devices(self):
        guest = Guest("u_002", "Bob")
        assert guest.can_perform(Permission.MANAGE_DEVICES) is False

    def test_guest_can_use_assigned_device(self):
        guest = Guest("u_003", "Carol")
        guest.assign_device("dev_001")
        assert guest.can_use_device("dev_001") is True
        assert guest.can_use_device("dev_999") is False

    def test_technician_can_view_logs(self):
        tech = Technician("u_004", "Dave")
        assert tech.can_perform(Permission.VIEW_LOGS) is True

    def test_technician_cannot_manage_users(self):
        tech = Technician("u_005", "Eve")
        assert tech.can_perform(Permission.MANAGE_USERS) is False


# ===========================================================================
# Persistence
# ===========================================================================

class TestJsonPersistence:

    TEST_FILE = "data/test_save.json"

    def setup_method(self):
        """Run before each test — clear any leftover file."""
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)

    def teardown_method(self):
        """Run after each test — clean up."""
        if os.path.exists(self.TEST_FILE):
            os.remove(self.TEST_FILE)

    def _build_test_house(self):
        house = House("Test House", "1 Test Street")
        room  = Room("r_001", "Test Room", "other")
        light = SmartLight("d_001", "Test Light")
        light.set_brightness(75)
        light.turn_on()
        room.add_device(light)
        house.add_room(room)
        return house

    def test_save_creates_file(self):
        house = self._build_test_house()
        repo  = JsonPersistence(self.TEST_FILE)
        repo.save(house)
        assert os.path.exists(self.TEST_FILE)

    def test_load_restores_house_name(self):
        house  = self._build_test_house()
        repo   = JsonPersistence(self.TEST_FILE)
        repo.save(house)
        loaded = repo.load()
        assert loaded.name == "Test House"

    def test_load_restores_room_count(self):
        house  = self._build_test_house()
        repo   = JsonPersistence(self.TEST_FILE)
        repo.save(house)
        loaded = repo.load()
        assert len(loaded.get_all_rooms()) == 1

    def test_load_restores_device_count(self):
        house  = self._build_test_house()
        repo   = JsonPersistence(self.TEST_FILE)
        repo.save(house)
        loaded = repo.load()
        assert len(loaded.get_all_devices()) == 1

    def test_load_nonexistent_file_returns_none(self):
        repo   = JsonPersistence("data/does_not_exist.json")
        result = repo.load()
        assert result is None
