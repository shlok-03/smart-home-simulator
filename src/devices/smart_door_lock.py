"""
smart_door_lock.py
------------------
A smart door lock with access history and security alerts.

New OOP Concept introduced here:
- Aggregation : The lock maintains a LOG (list of dicts).
                The log entries exist independently — they outlive any single lock/unlock event.
"""

from src.devices.smart_device import SmartDevice
from datetime import datetime


class SmartDoorLock(SmartDevice):
    """
    Smart door lock that records who locked/unlocked it and when.

    Security levels:
    - LOW    : anyone can unlock remotely
    - MEDIUM : PIN required
    - HIGH   : PIN + alert sent on every unlock
    """

    BASE_ENERGY_WATTS = 2.0    # locks use very little energy

    SECURITY_LOW    = "low"
    SECURITY_MEDIUM = "medium"
    SECURITY_HIGH   = "high"

    def __init__(self, device_id: str, name: str, room: str = None,
                 pin: str = "0000"):
        super().__init__(device_id, name, room)

        self._is_locked: bool = True               # locked by default (safe)
        self._pin: str = pin                       # 4-digit PIN
        self._security_level: str = self.SECURITY_MEDIUM
        self._access_history: list = []            # log of all lock/unlock events
        self._max_history: int = 50                # keep last 50 entries

    # -------------------------------------------------------------------------
    # OVERRIDE
    # -------------------------------------------------------------------------

    def turn_on(self):
        """'Turning on' a lock means making it active / online."""
        super().turn_on()
        self._energy_consumption = self.BASE_ENERGY_WATTS

    def get_status(self) -> dict:
        return {
            "id":             self._id,
            "name":           self._name,
            "type":           "SmartDoorLock",
            "power":          self._power_state,
            "locked":         self._is_locked,
            "security_level": self._security_level,
            "energy_w":       self._energy_consumption,
            "room":           self._room,
            "history_count":  len(self._access_history),
        }

    # -------------------------------------------------------------------------
    # LOCK / UNLOCK
    # -------------------------------------------------------------------------

    def lock(self, user: str = "system") -> bool:
        """Lock the door. Always succeeds (no PIN needed to lock)."""
        self._is_locked = True
        self._log_event("LOCKED", user, success=True)
        print(f"  🔒 [{self._name}] LOCKED by {user}")
        return True

    def unlock(self, user: str = "system", pin: str = None) -> bool:
        """
        Unlock the door.

        For MEDIUM/HIGH security, the correct PIN is required.
        Returns True if unlocked, False if denied.
        """
        # Check security level
        if self._security_level in (self.SECURITY_MEDIUM, self.SECURITY_HIGH):
            if pin != self._pin:
                self._log_event("UNLOCK_DENIED", user, success=False)
                print(f"  🚨 [{self._name}] UNLOCK DENIED for {user} — wrong PIN")
                return False

        self._is_locked = False
        self._log_event("UNLOCKED", user, success=True)
        print(f"  🔓 [{self._name}] UNLOCKED by {user}")

        if self._security_level == self.SECURITY_HIGH:
            print(f"  🔔 SECURITY ALERT: {self._name} was unlocked by {user}")

        return True

    def change_pin(self, old_pin: str, new_pin: str) -> bool:
        """Change the PIN. Must provide the current PIN first."""
        if old_pin != self._pin:
            print(f"  ❌ Cannot change PIN — old PIN incorrect")
            return False
        if len(new_pin) != 4 or not new_pin.isdigit():
            print(f"  ❌ New PIN must be exactly 4 digits")
            return False
        self._pin = new_pin
        print(f"  ✅ [{self._name}] PIN changed successfully")
        return True

    def set_security_level(self, level: str) -> None:
        """Adjust security level: low, medium, or high."""
        if level not in (self.SECURITY_LOW, self.SECURITY_MEDIUM, self.SECURITY_HIGH):
            print(f"  ⚠️  Invalid security level '{level}'")
            return
        self._security_level = level
        print(f"  🛡️  [{self._name}] security level set to {level.upper()}")

    # -------------------------------------------------------------------------
    # ACCESS HISTORY
    # -------------------------------------------------------------------------

    def _log_event(self, action: str, user: str, success: bool) -> None:
        """
        Add an entry to the access history log.
        Private — only called internally by lock() and unlock().
        """
        entry = {
            "timestamp": datetime.now().isoformat(),
            "action":    action,
            "user":      user,
            "success":   success,
        }
        self._access_history.append(entry)
        # Keep list from growing forever
        if len(self._access_history) > self._max_history:
            self._access_history.pop(0)   # remove oldest entry

    def get_access_history(self, last_n: int = 10) -> list:
        """Return the most recent N log entries."""
        return self._access_history[-last_n:]

    def print_access_history(self) -> None:
        """Pretty-print the access log."""
        print(f"\n  📋 Access history for [{self._name}]:")
        if not self._access_history:
            print("     (no entries)")
            return
        for entry in self._access_history[-10:]:
            symbol = "✅" if entry["success"] else "❌"
            print(f"     {symbol} {entry['timestamp']}  |  "
                  f"{entry['action']:<15}  |  {entry['user']}")

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def is_locked(self) -> bool:
        return self._is_locked

    @property
    def security_level(self) -> str:
        return self._security_level
