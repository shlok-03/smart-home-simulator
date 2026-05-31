"""
security_camera.py
------------------
A smart security camera with motion detection and recording.

New OOP Concept introduced here:
- The camera has an INTERNAL STATE (idle / recording / alert) and
  behaves differently depending on what state it's in.
  This foreshadows the State design pattern (covered in optional patterns).
"""

from src.devices.smart_device import SmartDevice
from datetime import datetime


class SecurityCamera(SmartDevice):
    """
    Smart security camera.

    States:
      idle      — on but not recording
      recording — actively capturing footage
      alert     — motion detected, alert sent
    """

    BASE_ENERGY_WATTS  = 8.0    # idle
    RECORD_ENERGY_WATTS = 15.0  # recording uses more

    STATE_IDLE      = "idle"
    STATE_RECORDING = "recording"
    STATE_ALERT     = "alert"

    def __init__(self, device_id: str, name: str, room: str = None):
        super().__init__(device_id, name, room)

        self._state: str = self.STATE_IDLE
        self._motion_detection: bool = True    # enabled by default
        self._recording: bool = False
        self._alerts: list = []                # list of alert messages
        self._recording_start: datetime = None

    # -------------------------------------------------------------------------
    # OVERRIDE
    # -------------------------------------------------------------------------

    def turn_on(self):
        super().turn_on()
        self._state = self.STATE_IDLE
        self._energy_consumption = self.BASE_ENERGY_WATTS

    def turn_off(self):
        if self._recording:
            self.stop_recording()
        super().turn_off()
        self._state = self.STATE_IDLE

    def get_status(self) -> dict:
        return {
            "id":               self._id,
            "name":             self._name,
            "type":             "SecurityCamera",
            "power":            self._power_state,
            "state":            self._state,
            "recording":        self._recording,
            "motion_detection": self._motion_detection,
            "alert_count":      len(self._alerts),
            "energy_w":         self._energy_consumption,
            "room":             self._room,
        }

    # -------------------------------------------------------------------------
    # CAMERA-SPECIFIC METHODS
    # -------------------------------------------------------------------------

    def start_recording(self) -> None:
        """Begin recording footage."""
        if not self._power_state:
            print(f"  ⚠️  [{self._name}] is OFF — can't record")
            return
        if self._recording:
            print(f"  ⚠️  [{self._name}] already recording")
            return
        self._recording = True
        self._state = self.STATE_RECORDING
        self._recording_start = datetime.now()
        self._energy_consumption = self.RECORD_ENERGY_WATTS
        print(f"  🎥 [{self._name}] RECORDING started")

    def stop_recording(self) -> None:
        """Stop recording footage."""
        if not self._recording:
            return
        duration = (datetime.now() - self._recording_start).seconds
        self._recording = False
        self._state = self.STATE_IDLE
        self._energy_consumption = self.BASE_ENERGY_WATTS
        print(f"  ⏹️  [{self._name}] RECORDING stopped — {duration}s captured")

    def trigger_motion_alert(self, location: str = None) -> str:
        """
        Called by a motion sensor when movement is detected.
        Automatically starts recording and logs an alert.
        Returns the alert message.
        """
        if not self._power_state:
            return ""

        where = location or self._room or "unknown location"
        alert_msg = f"⚠️  MOTION DETECTED by [{self._name}] in {where} at {datetime.now().strftime('%H:%M:%S')}"

        self._alerts.append({
            "message":   alert_msg,
            "timestamp": datetime.now().isoformat(),
            "location":  where,
        })
        self._state = self.STATE_ALERT
        print(f"  {alert_msg}")

        # Automatically start recording on motion
        if not self._recording:
            self.start_recording()

        return alert_msg

    def enable_motion_detection(self) -> None:
        self._motion_detection = True
        print(f"  👁️  [{self._name}] motion detection ENABLED")

    def disable_motion_detection(self) -> None:
        self._motion_detection = False
        print(f"  🙈 [{self._name}] motion detection DISABLED")

    def get_alerts(self, last_n: int = 5) -> list:
        """Return the most recent N alerts."""
        return self._alerts[-last_n:]

    def clear_alerts(self) -> None:
        self._alerts.clear()
        print(f"  🗑️  [{self._name}] alerts cleared")

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def is_recording(self) -> bool:
        return self._recording

    @property
    def state(self) -> str:
        return self._state

    @property
    def motion_detection(self) -> bool:
        return self._motion_detection
