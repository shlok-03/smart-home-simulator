"""
user.py
-------
User system with three roles: Owner, Guest, Technician.

OOP Concept: Inheritance + Polymorphism
  All three user types share a User base class.
  Each overrides can_perform() to enforce its own permission rules.

SOLID Principle: Liskov Substitution
  Anywhere the code expects a User, it can receive an Owner, Guest,
  or Technician instead — and the behaviour is still correct.
"""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List


# ---------------------------------------------------------------------------
# PERMISSION CONSTANTS
# Using constants avoids typos from "magic strings" scattered everywhere.
# ---------------------------------------------------------------------------
class Permission:
    MANAGE_DEVICES   = "manage_devices"
    VIEW_DEVICES     = "view_devices"
    CONFIGURE_AUTO   = "configure_automation"
    VIEW_LOGS        = "view_logs"
    MANAGE_USERS     = "manage_users"
    USE_ASSIGNED     = "use_assigned_devices"
    RUN_DIAGNOSTICS  = "run_diagnostics"
    VIEW_HEALTH      = "view_device_health"


# ---------------------------------------------------------------------------
# ABSTRACT BASE CLASS
# ---------------------------------------------------------------------------
class User(ABC):
    """
    Base class for all system users.
    """

    def __init__(self, user_id: str, name: str, email: str = ""):
        self._id           = user_id
        self._name         = name
        self._email        = email
        self._created_at   = datetime.now()
        self._last_login   = None
        self._active       = True

    @property
    @abstractmethod
    def role(self) -> str:
        """Return the role label for this user type."""
        pass

    @abstractmethod
    def get_permissions(self) -> List[str]:
        """Return a list of permission constants this user holds."""
        pass

    def can_perform(self, permission: str) -> bool:
        """
        Check whether this user is allowed to perform an action.

        Usage:
            if user.can_perform(Permission.MANAGE_DEVICES):
                device.turn_on()
            else:
                print("Access denied")
        """
        return permission in self.get_permissions()

    def record_login(self) -> None:
        self._last_login = datetime.now()

    def deactivate(self) -> None:
        self._active = False

    # Properties
    @property
    def id(self)        -> str:  return self._id
    @property
    def name(self)      -> str:  return self._name
    @property
    def email(self)     -> str:  return self._email
    @property
    def is_active(self) -> bool: return self._active

    def __str__(self) -> str:
        return f"{self._name} ({self.role}) | active={self._active}"

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} id={self._id!r} name={self._name!r}>"


# ---------------------------------------------------------------------------
# CONCRETE USER TYPES
# ---------------------------------------------------------------------------

class Owner(User):
    """
    The home owner — full access to everything.
    Can manage devices, configure automation, view logs, manage other users.
    """

    @property
    def role(self) -> str:
        return "owner"

    def get_permissions(self) -> List[str]:
        # Owners get ALL permissions
        return [
            Permission.MANAGE_DEVICES,
            Permission.VIEW_DEVICES,
            Permission.CONFIGURE_AUTO,
            Permission.VIEW_LOGS,
            Permission.MANAGE_USERS,
            Permission.USE_ASSIGNED,
            Permission.RUN_DIAGNOSTICS,
            Permission.VIEW_HEALTH,
        ]


class Guest(User):
    """
    A temporary visitor — can only use specifically assigned devices.
    Cannot see logs, configure automation, or manage anything.
    """

    def __init__(self, user_id: str, name: str, email: str = ""):
        super().__init__(user_id, name, email)
        self._assigned_device_ids: List[str] = []

    def assign_device(self, device_id: str) -> None:
        """Grant this guest access to a specific device."""
        if device_id not in self._assigned_device_ids:
            self._assigned_device_ids.append(device_id)
            print(f"  ➕ Device '{device_id}' assigned to guest {self._name}")

    def revoke_device(self, device_id: str) -> None:
        if device_id in self._assigned_device_ids:
            self._assigned_device_ids.remove(device_id)

    def can_use_device(self, device_id: str) -> bool:
        return device_id in self._assigned_device_ids

    @property
    def role(self) -> str:
        return "guest"

    def get_permissions(self) -> List[str]:
        return [
            Permission.USE_ASSIGNED,
            Permission.VIEW_DEVICES,
        ]

    @property
    def assigned_devices(self) -> List[str]:
        return list(self._assigned_device_ids)


class Technician(User):
    """
    A maintenance technician — can inspect and diagnose, but not control
    regular devices or change configuration.
    """

    def __init__(self, user_id: str, name: str, email: str = "",
                 company: str = ""):
        super().__init__(user_id, name, email)
        self._company = company

    def run_diagnostic(self, device) -> dict:
        """
        Run a health check on any device.
        Returns a report dict.
        """
        status = device.get_status()
        report = {
            "technician":  self._name,
            "device_id":   device.id,
            "device_name": device.name,
            "status":      status,
            "issues":      [],
            "timestamp":   datetime.now().isoformat(),
        }

        # Simple heuristic checks
        if not status.get("power"):
            report["issues"].append("Device is offline")
        if status.get("energy_w", 0) == 0 and status.get("power"):
            report["issues"].append("Device is ON but reporting zero energy draw")

        print(f"  🔧 Diagnostic for [{device.name}]: "
              f"{'OK' if not report['issues'] else ', '.join(report['issues'])}")
        return report

    @property
    def role(self) -> str:
        return "technician"

    def get_permissions(self) -> List[str]:
        return [
            Permission.VIEW_DEVICES,
            Permission.VIEW_LOGS,
            Permission.RUN_DIAGNOSTICS,
            Permission.VIEW_HEALTH,
        ]

    @property
    def company(self) -> str:
        return self._company
