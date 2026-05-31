"""
logger.py
---------
DESIGN PATTERN #2 — SINGLETON PATTERN

Problem it solves:
    A logger writes events to a file or console.
    If 10 different parts of the system each create their OWN logger,
    you get 10 separate log files, duplicate entries, or file conflicts.

    You want ONE logger shared by the whole application.

    The Singleton pattern guarantees a class can only ever have
    ONE instance. Every time you ask for it, you get the same object back.

Real-world analogy:
    A country can only have one president at a time.
    No matter how many times people "elect" one, there's still just one office.

How it works in Python:
    We override __new__ — the method Python calls BEFORE __init__
    to actually create the object in memory.
    If an instance already exists, we return that instead of making a new one.
"""

from datetime import datetime
import os


class Logger:
    """
    Application-wide logger. Only one instance ever exists.

    Usage (from anywhere in the codebase):
        log = Logger()           # first call — creates the instance
        log2 = Logger()          # second call — returns the SAME instance
        log is log2              # → True
        log.info("Hello")
    """

    # Class variable — lives on the CLASS, not on any instance.
    # Stores the single instance once created.
    _instance = None

    def __new__(cls):
        """
        __new__ runs before __init__.
        If no instance exists yet, create one and store it.
        If one already exists, return it.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialised = False   # flag so __init__ only runs once
        return cls._instance

    def __init__(self):
        """
        __init__ runs after __new__, but we only want to set up
        the logger once — not re-initialise it every time Logger() is called.
        """
        if self._initialised:
            return   # already set up — skip
        self._initialised = True

        self._logs: list  = []          # in-memory log history
        self._log_file    = None        # optional file path
        self._print_to_console = True   # echo logs to the terminal

        self.info("Logger initialised — Singleton instance created")

    # ------------------------------------------------------------------
    # LOGGING METHODS
    # ------------------------------------------------------------------

    def info(self, message: str, source: str = "system") -> None:
        """Log a routine informational message."""
        self._write("INFO", message, source)

    def warning(self, message: str, source: str = "system") -> None:
        """Log a warning — something unexpected but not critical."""
        self._write("WARNING", message, source)

    def error(self, message: str, source: str = "system") -> None:
        """Log an error — something went wrong."""
        self._write("ERROR", message, source)

    def event(self, message: str, source: str = "system") -> None:
        """Log a domain event (sensor fired, device changed state, etc.)."""
        self._write("EVENT", message, source)

    def _write(self, level: str, message: str, source: str) -> None:
        """
        Internal method — formats and stores a log entry.
        Private (leading _) — external code uses info/warning/error/event.
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        entry = {
            "timestamp": timestamp,
            "level":     level,
            "source":    source,
            "message":   message,
        }
        self._logs.append(entry)

        # Format for display
        icons = {"INFO": "ℹ️ ", "WARNING": "⚠️ ", "ERROR": "❌", "EVENT": "📡"}
        icon  = icons.get(level, "  ")
        line  = f"  {icon} [{timestamp}] [{level:<7}] [{source}] {message}"

        if self._print_to_console:
            print(line)

        if self._log_file:
            with open(self._log_file, "a") as f:
                f.write(line + "\n")

    # ------------------------------------------------------------------
    # RETRIEVAL
    # ------------------------------------------------------------------

    def get_logs(self, level: str = None, last_n: int = None) -> list:
        """
        Retrieve stored log entries, optionally filtered by level.

        Parameters:
            level  : "INFO", "WARNING", "ERROR", or "EVENT" — or None for all
            last_n : only return the most recent N entries
        """
        results = self._logs
        if level:
            results = [e for e in results if e["level"] == level.upper()]
        if last_n:
            results = results[-last_n:]
        return results

    def print_summary(self) -> None:
        """Print a count of each log level."""
        counts = {}
        for entry in self._logs:
            counts[entry["level"]] = counts.get(entry["level"], 0) + 1
        print(f"\n  📋 Log summary: {counts} | Total: {len(self._logs)}")

    def enable_file_logging(self, filepath: str) -> None:
        """Start writing all logs to a file as well as the console."""
        self._log_file = filepath
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        self.info(f"File logging enabled → {filepath}")

    def silence_console(self) -> None:
        """Stop printing to console (useful during tests)."""
        self._print_to_console = False

    def enable_console(self) -> None:
        self._print_to_console = True

    def clear(self) -> None:
        """Wipe the in-memory log. Does NOT delete any log file."""
        self._logs.clear()

    # ------------------------------------------------------------------
    # SINGLETON INTEGRITY CHECK
    # ------------------------------------------------------------------

    @classmethod
    def get_instance(cls) -> "Logger":
        """Alternative way to get the singleton — explicit and readable."""
        return cls()

    @classmethod
    def reset(cls) -> None:
        """
        Destroy the singleton instance.
        Only used in unit tests where each test needs a fresh logger.
        NEVER call this in production code.
        """
        cls._instance = None
