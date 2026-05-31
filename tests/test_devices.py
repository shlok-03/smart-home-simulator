"""
test_devices.py
---------------
Unit tests for SmartLight, SmartThermostat, SmartDoorLock,
SecurityCamera, and SmartSpeaker.

Run with:  pytest tests/test_devices.py -v
"""

import pytest
from src.devices.smart_light      import SmartLight
from src.devices.smart_thermostat import SmartThermostat
from src.devices.smart_door_lock  import SmartDoorLock
from src.devices.security_camera  import SecurityCamera
from src.devices.smart_speaker    import SmartSpeaker
from src.devices.device_factory   import DeviceFactory


# ===========================================================================
# SmartLight
# ===========================================================================

class TestSmartLight:

    def test_light_starts_off(self):
        """A new light should be powered off by default."""
        light = SmartLight("t_l1", "Test Light")
        assert light.power_state is False

    def test_turn_on_updates_power_state(self):
        light = SmartLight("t_l2", "Test Light")
        light.turn_on()
        assert light.power_state is True

    def test_turn_off_resets_energy(self):
        light = SmartLight("t_l3", "Test Light")
        light.turn_on()
        light.turn_off()
        assert light.energy_consumption == 0.0
        assert light.power_state is False

    def test_brightness_valid_range(self):
        light = SmartLight("t_l4", "Test Light")
        light.set_brightness(75)
        assert light.brightness == 75

    def test_brightness_above_100_rejected(self):
        """Setting brightness above 100 should be silently rejected."""
        light = SmartLight("t_l5", "Test Light")
        light.set_brightness(200)
        assert light.brightness == 100   # stays at default

    def test_brightness_below_0_rejected(self):
        light = SmartLight("t_l6", "Test Light")
        light.set_brightness(-10)
        assert light.brightness == 100

    def test_energy_scales_with_brightness(self):
        """Energy at 50% brightness should be half of energy at 100%."""
        light = SmartLight("t_l7", "Test Light")
        light.turn_on()
        light.set_brightness(100)
        full_energy = light.energy_consumption

        light.set_brightness(50)
        half_energy = light.energy_consumption

        assert half_energy == pytest.approx(full_energy / 2)

    def test_colour_mode_valid(self):
        light = SmartLight("t_l8", "Test Light")
        light.set_colour("warm")
        assert light.colour_mode == "warm"

    def test_colour_mode_invalid_ignored(self):
        light = SmartLight("t_l9", "Test Light")
        light.set_colour("ultraviolet")   # not a valid colour
        assert light.colour_mode == "white"   # stays at default


# ===========================================================================
# SmartThermostat
# ===========================================================================

class TestSmartThermostat:

    def test_starts_in_idle_mode(self):
        thermo = SmartThermostat("t_th1", "Test Thermo")
        # Before turning on, not in any active mode
        assert thermo.mode == SmartThermostat.MODE_IDLE

    def test_heating_mode_when_cold(self):
        """When current temp < target, thermostat should heat."""
        thermo = SmartThermostat("t_th2", "Test Thermo")
        thermo.turn_on()
        thermo.update_current_temperature(15.0)
        thermo.set_target_temperature(22.0)
        assert thermo.mode == SmartThermostat.MODE_HEATING

    def test_cooling_mode_when_hot(self):
        thermo = SmartThermostat("t_th3", "Test Thermo")
        thermo.turn_on()
        thermo.update_current_temperature(30.0)
        thermo.set_target_temperature(22.0)
        assert thermo.mode == SmartThermostat.MODE_COOLING

    def test_idle_when_at_target(self):
        thermo = SmartThermostat("t_th4", "Test Thermo")
        thermo.turn_on()
        thermo.update_current_temperature(21.0)
        thermo.set_target_temperature(21.0)
        assert thermo.mode == SmartThermostat.MODE_IDLE

    def test_eco_mode_caps_temperature(self):
        thermo = SmartThermostat("t_th5", "Test Thermo")
        thermo.turn_on()
        thermo.enable_eco_mode()
        thermo.set_target_temperature(28.0)   # should be capped at 23
        assert thermo.target_temperature <= 23.0


# ===========================================================================
# SmartDoorLock
# ===========================================================================

class TestSmartDoorLock:

    def test_starts_locked(self):
        lock = SmartDoorLock("t_dl1", "Test Lock", pin="1234")
        assert lock.is_locked is True

    def test_unlock_correct_pin(self):
        lock = SmartDoorLock("t_dl2", "Test Lock", pin="1234")
        lock.turn_on()
        result = lock.unlock("alice", pin="1234")
        assert result is True
        assert lock.is_locked is False

    def test_unlock_wrong_pin_denied(self):
        lock = SmartDoorLock("t_dl3", "Test Lock", pin="1234")
        lock.turn_on()
        result = lock.unlock("alice", pin="wrong")
        assert result is False
        assert lock.is_locked is True   # still locked

    def test_lock_always_succeeds(self):
        lock = SmartDoorLock("t_dl4", "Test Lock", pin="1234")
        lock.turn_on()
        lock.unlock("alice", pin="1234")
        result = lock.lock("system")
        assert result is True
        assert lock.is_locked is True

    def test_access_history_recorded(self):
        lock = SmartDoorLock("t_dl5", "Test Lock", pin="5678")
        lock.turn_on()
        lock.unlock("bob", pin="5678")
        lock.lock("bob")
        history = lock.get_access_history()
        assert len(history) >= 2


# ===========================================================================
# Factory
# ===========================================================================

class TestDeviceFactory:

    def test_create_light(self):
        device = DeviceFactory.create("LIGHT", "f_001", "Factory Light")
        assert isinstance(device, SmartLight)

    def test_create_thermostat(self):
        device = DeviceFactory.create("THERMOSTAT", "f_002", "Factory Thermo")
        assert isinstance(device, SmartThermostat)

    def test_unknown_type_raises_value_error(self):
        with pytest.raises(ValueError):
            DeviceFactory.create("MICROWAVE", "f_003", "Microwave")

    def test_case_insensitive(self):
        device = DeviceFactory.create("light", "f_004", "Lower Case Light")
        assert isinstance(device, SmartLight)
