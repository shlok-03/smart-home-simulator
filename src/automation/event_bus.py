"""
event_bus.py
------------
DESIGN PATTERN #3 — OBSERVER PATTERN (formal implementation)

In Part 3, we used a simple list of callback functions on each sensor.
That works, but it has a limit: each sensor manages its own listeners
separately. If you want one listener to hear from ALL sensors, you'd
have to register it on every single sensor one by one.

The EventBus (also called EventDispatcher or PubSub) solves this:
  - Anyone can PUBLISH an event with a topic name
  - Anyone can SUBSCRIBE to a topic name
  - The bus routes events to the right subscribers automatically

Real-world analogy:
  A radio station.
  - The station (publisher) broadcasts on frequency 99.1 FM.
  - Any radio (subscriber) tuned to 99.1 FM receives it.
  - The station has no idea how many radios are listening.
  - Radios can tune in or out without the station knowing.

Terms:
  Publisher  -- fires events (sensors, devices)
  Subscriber -- listens for events (automation engine, logger, notifications)
  Topic      -- the "channel" name, e.g. "motion_detected", "smoke_detected"
"""

from typing import Callable, Dict, List


class EventBus:
    """
    Central event routing system.

    This is ALSO a Singleton — there should only ever be ONE event bus
    in the system. All publishers and subscribers share the same bus.
    """

    _instance    = None
    _initialised = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if EventBus._initialised:
            return
        EventBus._initialised = True

        # Dictionary: topic_name -> list of subscriber functions
        self._subscribers: Dict[str, List[Callable]] = {}
        self._event_history: list = []
        self._max_history = 200

    # ------------------------------------------------------------------
    # SUBSCRIBE
    # ------------------------------------------------------------------

    def subscribe(self, topic: str, callback: Callable) -> None:
        """
        Register a function to be called whenever 'topic' is published.

        Parameters:
            topic    : event name, e.g. "motion_detected"
            callback : a function that accepts one argument (the event dict)
        """
        if topic not in self._subscribers:
            self._subscribers[topic] = []

        if callback not in self._subscribers[topic]:
            self._subscribers[topic].append(callback)
            print(f"  📡 EventBus: '{callback.__name__}' subscribed to '{topic}'")

    def unsubscribe(self, topic: str, callback: Callable) -> None:
        """Remove a subscriber from a topic."""
        if topic in self._subscribers:
            if callback in self._subscribers[topic]:
                self._subscribers[topic].remove(callback)

    def subscribe_all(self, callback: Callable) -> None:
        """
        Subscribe to EVERY topic.
        The special key "*" means "catch all events".
        Useful for the logger, which wants to record everything.
        """
        self.subscribe("*", callback)

    # ------------------------------------------------------------------
    # PUBLISH
    # ------------------------------------------------------------------

    def publish(self, topic: str, event: dict) -> int:
        """
        Broadcast an event to all subscribers of that topic.
        Returns how many subscribers received the event.
        """
        event["event_type"] = topic

        self._event_history.append(event)
        if len(self._event_history) > self._max_history:
            self._event_history.pop(0)

        notified = 0

        # Notify specific-topic subscribers
        for callback in self._subscribers.get(topic, []):
            try:
                callback(event)
                notified += 1
            except Exception as err:
                print(f"  EventBus error in '{callback.__name__}': {err}")

        # Notify wildcard subscribers (they hear everything)
        for callback in self._subscribers.get("*", []):
            try:
                callback(event)
                notified += 1
            except Exception as err:
                print(f"  EventBus wildcard error: {err}")

        return notified

    # ------------------------------------------------------------------
    # INSPECTION
    # ------------------------------------------------------------------

    def get_topics(self) -> list:
        return [t for t, subs in self._subscribers.items() if subs]

    def get_history(self, last_n: int = 10) -> list:
        return self._event_history[-last_n:]

    def subscriber_count(self, topic: str) -> int:
        return len(self._subscribers.get(topic, []))

    def clear_history(self) -> None:
        self._event_history.clear()
