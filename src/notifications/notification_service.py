"""
notification_service.py
-----------------------
Generates and stores notifications for important smart home events.

Two classes here:
  Notification        — a single notification message (data class)
  NotificationService — manages sending, storing, and reading notifications
                        (Singleton — one service for the whole house)
"""

from datetime import datetime


class Notification:
    """
    A single notification message.

    Priorities:
      low      — informational (e.g. "Good morning" scene activated)
      normal   — something happened (e.g. "Front door opened")
      high     — needs attention (e.g. "Motion detected at 2 AM")
      critical — act immediately (e.g. "Smoke detected")
    """

    PRIORITY_LOW      = "low"
    PRIORITY_NORMAL   = "normal"
    PRIORITY_HIGH     = "high"
    PRIORITY_CRITICAL = "critical"

    # Keeps a running counter so each notification gets a unique ID
    _counter = 0

    def __init__(self, title: str, message: str,
                 priority: str = "normal", source: str = "system"):
        Notification._counter += 1
        self._id        = f"notif_{Notification._counter:04d}"
        self._title     = title
        self._message   = message
        self._priority  = priority
        self._source    = source
        self._timestamp = datetime.now()
        self._read      = False

    def mark_read(self) -> None:
        self._read = True

    # Properties
    @property
    def id(self)        -> str:  return self._id
    @property
    def title(self)     -> str:  return self._title
    @property
    def message(self)   -> str:  return self._message
    @property
    def priority(self)  -> str:  return self._priority
    @property
    def source(self)    -> str:  return self._source
    @property
    def timestamp(self) -> datetime: return self._timestamp
    @property
    def is_read(self)   -> bool: return self._read

    def __str__(self) -> str:
        icons = {
            "low":      "ℹ️ ",
            "normal":   "🔔",
            "high":     "⚠️ ",
            "critical": "🚨",
        }
        icon   = icons.get(self._priority, "🔔")
        status = "✓" if self._read else "●"
        time   = self._timestamp.strftime("%H:%M:%S")
        return f"  {icon} [{time}] {status} [{self._priority.upper():<8}] {self._title}: {self._message}"


# ---------------------------------------------------------------------------
# NOTIFICATION SERVICE  (Singleton)
# ---------------------------------------------------------------------------

class NotificationService:
    """
    Central service that handles sending and storing notifications.

    Singleton — there is only ONE notification inbox for the whole house.
    All components (AutomationEngine, sensors, devices) post to the same service.
    """

    _instance    = None
    _initialised = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if NotificationService._initialised:
            return
        NotificationService._initialised = True

        self._notifications = []    # full list of all notifications
        self._max_stored    = 100   # cap so memory doesn't grow forever

    # ------------------------------------------------------------------
    # SENDING
    # ------------------------------------------------------------------

    def send(self, notification: Notification) -> None:
        """
        Add a pre-built Notification object to the inbox.
        """
        self._notifications.append(notification)

        # Keep the list bounded
        if len(self._notifications) > self._max_stored:
            self._notifications.pop(0)

        # Print with visual priority indicator
        print(notification)

    def send_simple(self, title: str, message: str,
                    priority: str = "normal", source: str = "system") -> Notification:
        """
        Shortcut — build and send a notification in one call.
        Returns the Notification object in case the caller needs it.
        """
        notif = Notification(title, message, priority, source)
        self.send(notif)
        return notif

    # ------------------------------------------------------------------
    # READING
    # ------------------------------------------------------------------

    def get_all(self) -> list:
        """Return all notifications (read and unread)."""
        return list(self._notifications)

    def get_unread(self) -> list:
        """Return only notifications that haven't been read yet."""
        return [n for n in self._notifications if not n.is_read]

    def get_by_priority(self, priority: str) -> list:
        return [n for n in self._notifications
                if n.priority == priority.lower()]

    def mark_all_read(self) -> None:
        for n in self._notifications:
            n.mark_read()

    def print_all(self, unread_only: bool = False) -> None:
        """Print the notification inbox."""
        source = self._notifications if not unread_only else self.get_unread()
        label  = "Unread notifications" if unread_only else "All notifications"
        print(f"\n  📬 {label} ({len(source)}):")
        if not source:
            print("     (none)")
            return
        for n in source:
            print(str(n))

    def clear(self) -> None:
        self._notifications.clear()

    @property
    def total_count(self) -> int:
        return len(self._notifications)

    @property
    def unread_count(self) -> int:
        return len(self.get_unread())
