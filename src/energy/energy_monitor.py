"""
energy_monitor.py
-----------------
Tracks energy usage across the whole house and generates reports.

This is not a pattern on its own — it demonstrates:
  - Aggregation  : the monitor reads data FROM the house/rooms/devices,
                   it doesn't own them
  - Single Responsibility : energy monitoring is one focused job
"""

from datetime import datetime
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from src.house.house import House


class EnergyMonitor:
    """
    Reads energy data from every device in the house and reports on it.

    Nothing here modifies devices — it only reads their current state.
    """

    # kWh price in dollars — used for cost estimates
    PRICE_PER_KWH = 0.12

    def __init__(self, house: "House"):
        self._house    = house
        self._readings = []    # history of snapshot readings

    # ------------------------------------------------------------------
    # SNAPSHOT
    # ------------------------------------------------------------------

    def take_snapshot(self) -> dict:
        """
        Capture current energy state of the whole house.
        Stores it in history for trend analysis later.
        """
        snapshot = {
            "timestamp":   datetime.now().isoformat(),
            "total_watts": self._house.total_energy_consumption(),
            "rooms":       {},
        }

        for room in self._house.get_all_rooms():
            room_data = {
                "watts":   room.total_energy_consumption(),
                "devices": {}
            }
            for device in room.get_all_devices():
                room_data["devices"][device.id] = {
                    "name":  device.name,
                    "watts": device.energy_consumption,
                    "on":    device.power_state,
                }
            snapshot["rooms"][room.name] = room_data

        self._readings.append(snapshot)
        return snapshot

    # ------------------------------------------------------------------
    # REPORTS
    # ------------------------------------------------------------------

    def generate_report(self) -> None:
        """Print a full energy report to the console."""
        snapshot = self.take_snapshot()
        total_w  = snapshot["total_watts"]
        # Convert watts to kilowatts for the hourly cost estimate
        hourly_cost = (total_w / 1000) * self.PRICE_PER_KWH

        print("\n" + "="*48)
        print(f"  ⚡ ENERGY REPORT  —  "
              f"{datetime.now().strftime('%Y-%m-%d %H:%M')}")
        print("="*48)
        print(f"  Total consumption : {total_w:.1f} W")
        print(f"  Estimated cost    : ${hourly_cost:.4f} / hr")
        print()

        # Per-room breakdown
        print("  By room:")
        for room_name, data in snapshot["rooms"].items():
            bar = self._bar(data["watts"], total_w)
            print(f"    {room_name:<20} {data['watts']:>6.1f} W  {bar}")

        # Top energy consumers
        print()
        top = self.get_top_consumers(5)
        print("  Top consumers:")
        for rank, (name, watts) in enumerate(top, 1):
            print(f"    {rank}. {name:<25} {watts:.1f} W")

        # Eco tip
        active_off = self.get_devices_on_but_idle()
        if active_off:
            print(f"\n  💡 Eco tip: {len(active_off)} device(s) are on but idle:")
            for name in active_off:
                print(f"     • {name}")

        print("="*48)

    def get_top_consumers(self, n: int = 3) -> List[tuple]:
        """
        Return the N highest-energy devices as (name, watts) tuples,
        sorted highest first.
        """
        all_devices = self._house.get_all_devices()
        pairs = [(d.name, d.energy_consumption) for d in all_devices]
        pairs.sort(key=lambda pair: pair[1], reverse=True)
        return pairs[:n]

    def get_devices_on_but_idle(self) -> List[str]:
        """
        Return names of devices that are ON but consuming 0 W.
        These are likely left on by mistake.
        """
        result = []
        for device in self._house.get_all_devices():
            if device.power_state and device.energy_consumption == 0.0:
                result.append(device.name)
        return result

    def total_watts(self) -> float:
        return self._house.total_energy_consumption()

    def get_history(self) -> list:
        """Return all stored snapshots."""
        return list(self._readings)

    # ------------------------------------------------------------------
    # PRIVATE HELPER
    # ------------------------------------------------------------------

    @staticmethod
    def _bar(value: float, total: float, width: int = 12) -> str:
        """
        Generate a tiny ASCII progress bar to make the report visual.
        E.g.  ████░░░░░░░░
        """
        if total == 0:
            return "░" * width
        filled = int((value / total) * width)
        return "█" * filled + "░" * (width - filled)
