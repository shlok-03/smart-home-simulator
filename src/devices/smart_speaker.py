"""
smart_speaker.py
----------------
A smart speaker with volume control, music playback, and voice commands.

New OOP Concept introduced here:
- Method chaining opportunity: methods return self so you can chain calls
  speaker.set_volume(50).play("Jazz Playlist")  ← fluent interface style
"""

from src.devices.smart_device import SmartDevice


class SmartSpeaker(SmartDevice):
    """
    Smart speaker that plays music and responds to voice commands.

    Playback states:
      stopped  — nothing playing
      playing  — actively playing audio
      paused   — paused mid-track
    """

    BASE_ENERGY_WATTS  = 5.0     # standby
    PLAY_ENERGY_WATTS  = 20.0    # actively playing (scales with volume)

    STATE_STOPPED = "stopped"
    STATE_PLAYING = "playing"
    STATE_PAUSED  = "paused"

    # Supported voice commands → what they do
    VOICE_COMMANDS = {
        "play":         "start playback",
        "pause":        "pause playback",
        "stop":         "stop playback",
        "volume up":    "increase volume by 10",
        "volume down":  "decrease volume by 10",
        "mute":         "set volume to 0",
    }

    def __init__(self, device_id: str, name: str, room: str = None):
        super().__init__(device_id, name, room)

        self._volume: int = 50              # 0–100
        self._playback_state: str = self.STATE_STOPPED
        self._current_track: str = None
        self._playlist: list = []           # queue of tracks
        self._muted: bool = False
        self._previous_volume: int = 50     # remembered before mute

    # -------------------------------------------------------------------------
    # OVERRIDE
    # -------------------------------------------------------------------------

    def turn_on(self):
        super().turn_on()
        self._energy_consumption = self.BASE_ENERGY_WATTS

    def turn_off(self):
        self.stop()     # stop playback before shutting off
        super().turn_off()

    def get_status(self) -> dict:
        return {
            "id":             self._id,
            "name":           self._name,
            "type":           "SmartSpeaker",
            "power":          self._power_state,
            "volume":         self._volume,
            "muted":          self._muted,
            "playback_state": self._playback_state,
            "current_track":  self._current_track,
            "queue_length":   len(self._playlist),
            "energy_w":       self._energy_consumption,
            "room":           self._room,
        }

    # -------------------------------------------------------------------------
    # VOLUME
    # -------------------------------------------------------------------------

    def set_volume(self, level: int) -> "SmartSpeaker":
        """
        Set volume 0–100.
        Returns self — allows method chaining:
            speaker.set_volume(70).play("Chill Vibes")
        """
        if not 0 <= level <= 100:
            print(f"  ⚠️  Volume must be 0–100, got {level}")
            return self
        self._volume = level
        self._muted = (level == 0)
        if self._power_state:
            self._energy_consumption = self.BASE_ENERGY_WATTS + (self.PLAY_ENERGY_WATTS * level / 100)
        print(f"  🔊 [{self._name}] volume set to {level}")
        return self

    def mute(self) -> None:
        """Mute — remembers previous volume so unmute restores it."""
        if not self._muted:
            self._previous_volume = self._volume
            self._volume = 0
            self._muted = True
            print(f"  🔇 [{self._name}] MUTED")

    def unmute(self) -> None:
        """Restore volume to what it was before mute."""
        if self._muted:
            self._volume = self._previous_volume
            self._muted = False
            print(f"  🔊 [{self._name}] UNMUTED (volume restored to {self._volume})")

    # -------------------------------------------------------------------------
    # PLAYBACK
    # -------------------------------------------------------------------------

    def play(self, track: str = None) -> "SmartSpeaker":
        """
        Start playing a track (or resume if paused).
        Returns self for method chaining.
        """
        if not self._power_state:
            print(f"  ⚠️  [{self._name}] is OFF")
            return self

        if track:
            self._current_track = track
            self._playlist.insert(0, track)   # jump to front of queue

        if not self._current_track:
            print(f"  ⚠️  No track specified")
            return self

        self._playback_state = self.STATE_PLAYING
        self._energy_consumption = self.PLAY_ENERGY_WATTS + (self._volume * 0.1)
        print(f"  ▶️  [{self._name}] NOW PLAYING: {self._current_track}")
        return self

    def pause(self) -> None:
        """Pause without losing track position."""
        if self._playback_state != self.STATE_PLAYING:
            return
        self._playback_state = self.STATE_PAUSED
        self._energy_consumption = self.BASE_ENERGY_WATTS
        print(f"  ⏸️  [{self._name}] PAUSED: {self._current_track}")

    def stop(self) -> None:
        """Stop playback and clear current track."""
        self._playback_state = self.STATE_STOPPED
        self._current_track = None
        self._energy_consumption = self.BASE_ENERGY_WATTS if self._power_state else 0.0
        print(f"  ⏹️  [{self._name}] STOPPED")

    # -------------------------------------------------------------------------
    # VOICE COMMANDS
    # -------------------------------------------------------------------------

    def voice_command(self, command: str) -> None:
        """
        Process a voice command string.
        Demonstrates simple command dispatch using a dictionary lookup.
        """
        cmd = command.lower().strip()
        print(f"  🎙️  [{self._name}] heard: '{command}'")

        if cmd == "play":
            self.play()
        elif cmd == "pause":
            self.pause()
        elif cmd == "stop":
            self.stop()
        elif cmd == "volume up":
            self.set_volume(min(100, self._volume + 10))
        elif cmd == "volume down":
            self.set_volume(max(0, self._volume - 10))
        elif cmd == "mute":
            self.mute()
        else:
            print(f"  ❓ Unknown command '{command}'. "
                  f"Try: {', '.join(self.VOICE_COMMANDS.keys())}")

    # -------------------------------------------------------------------------
    # PROPERTIES
    # -------------------------------------------------------------------------

    @property
    def volume(self) -> int:
        return self._volume

    @property
    def playback_state(self) -> str:
        return self._playback_state

    @property
    def current_track(self) -> str:
        return self._current_track
