"""
logger.py
---------
DESIGN PATTERN #2 — SINGLETON PATTERN

The problem this pattern solves:
  A logger writes to a file. If you accidentally create TWO loggers,
  they might both try to write to the file at the same time, or you
  end up with two separate logs that don't have the full picture.

  The Singleton pattern guarantees that NO MATTER HOW MANY TIMES
  you call Logger(), you always get back the SAME object.

Real-world analogy:
  A country can only have one official president at a time.
  No matter who asks "who's the president?", the answer points
  to the same person. There isn't a separate president for each
  person who asks.

How it works in Python:
  We override __new__ (the method that actually creates objects).
  The first time Logger() is called, it creates the object normally
  and saves a reference to it in a class variable (_instance).
  Every call after that returns that same saved reference.
"""

from datetime import datetime
import os


class Logger:
    """
    Singleton logger that records all smart home events to memory and disk.

    Usage:
        log = Logger()          # first call — creates the logger
        log2 = Logger()         # second call — returns the SAME object
        assert log is log2      # True — they are literally the same object
    """

    _instance = None      # class-level variable — shared across all instances
    _initialised = False  # prevents __init__ from running twice

    def __new__(cls):
        """
        __new__ runs BEFORE __init__ and actually allocates the object.
        We intercept it here to enforce the singleton rule.
        """
        if cls._instance is None:
            # First time: create the real object the normal way
            cls._instance = super().__new__(cls)
            print("  📋 Logger: singleton instance created")
        # Every time (including first): return the single stored instance
        return cls._instance

    def __init__(self):
        """
        __init__ would normally run every time Logger() is called.
        The _initialised flag stops us from resetting the log on
        every call after the first.
        """
        if Logger._initialised:
            return   # already set up — do nothing

        Logger._initialised = True
        self._log_entries = []            # in-memory list of log dicts
        self._log_file    = "data/smart_home.log"
        self._max_entries = 500           # keep memory use bounded

        # Make sure the data/ folder exists
        os.makedirs("data", exist_ok=True)

    # ------------------------------------------------------------------
    # LOGGING METHODS
    # ------------------------------------------------------------------

    def log(self, level: str, source: str, message: str) -> None:
        """
        Write a log entry.

        Parameters:
            level   : "INFO", "WARNING", "ERROR", "CRITICAL"
            source  : which class/component is logging, e.g. "MotionSensor"
            message : what happened
        """
        entry = {
            "timestamp": datetime.now().isoformat(timespec="seconds"),
            "level":     level.upper(),
            "source":    source,
            "message":   message,
        }

        self._log_entries.append(entry)

        # Keep in-memory list from growing forever
        if len(self._log_entries) > self._max_entries:
            self._log_entries.pop(0)

        # Also write to disk so logs survive a restart
        line = (f"[{entry['timestamp']}] "
                f"{entry['level']:<8} | "
                f"{entry['source']:<25} | "
                f"{entry['message']}\n")

        with open(self._log_file, "a") as f:
            f.write(line)

    # Convenience wrappers so callers don't have to type the level string
    def info(self, source: str, message: str)     -> None:
        self.log("INFO",     source, message)

    def warning(self, source: str, message: str)  -> None:
        self.log("WARNING",  source, message)

    def error(self, source: str, message: str)    -> None:
        self.log("ERROR",    source, message)

    def critical(self, source: str, message: str) -> None:
        self.log("CRITICAL", source, message)

    # ------------------------------------------------------------------
    # READING LOGS
    # ------------------------------------------------------------------

    def get_recent(self, count: int = 10) -> list:
        """Return the most recent N log entries."""
        return self._log_entries[-count:]

    def get_by_level(self, level: str) -> list:
        """Return all entries matching a specific level."""
        return [e for e in self._log_entries if e["level"] == level.upper()]

    def get_by_source(self, source: str) -> list:
        """Return all entries from a specific source."""
        return [e for e in self._log_entries
                if source.lower() in e["source"].lower()]

    def print_recent(self, count: int = 10) -> None:
        """Pretty-print the most recent log entries."""
        entries = self.get_recent(count)
        print(f"\n  📋 Last {len(entries)} log entries:")
        for e in entries:
            icons = {"INFO": "ℹ️ ", "WARNING": "⚠️ ", "ERROR": "❌", "CRITICAL": "🚨"}
            icon = icons.get(e["level"], "  ")
            print(f"     {icon} [{e['timestamp']}] {e['source']}: {e['message']}")

    def clear(self) -> None:
        """Wipe the in-memory log (the file on disk is kept)."""
        self._log_entries.clear()
        print("  🗑️  Logger: in-memory log cleared")

    def total_entries(self) -> int:
        return len(self._log_entries)
