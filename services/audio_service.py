import os

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer

from resources import get_resource_path


class AudioService:
    """Ізолює роботу з Qt Multimedia від решти програми."""

    def __init__(self, volume: float, notification_file: str):
        self._audio_output = QAudioOutput()
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._audio_output)
        self._audio_output.setVolume(volume)

        sound_path = get_resource_path(notification_file)
        if os.path.exists(sound_path):
            self._player.setSource(QUrl.fromLocalFile(sound_path))

    @property
    def player(self) -> QMediaPlayer:
        return self._player

    def play_notification(self) -> None:
        if self._player.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia:
            return

        self._player.setPosition(0)
        self._player.play()

    def is_playing(self) -> bool:
        return (
            self._player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )
