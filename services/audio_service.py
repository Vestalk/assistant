import math
import os
import struct
import time
from typing import Optional

from PyQt6.QtCore import QUrl
from PyQt6.QtMultimedia import (
    QAudioBuffer,
    QAudioBufferOutput,
    QAudioFormat,
    QAudioOutput,
    QMediaPlayer,
)

from resources import get_resource_path
from services.radio_client import RadioBrowserClient


class AudioService:
    """Ізолює роботу з Qt Multimedia від решти програми."""

    def __init__(self, volume: float, notification_file: str):
        # Окремі виходи дають змогу одночасно відтворювати сповіщення й радіо.
        self._notification_audio_output = QAudioOutput()
        self._notification_audio_output.setVolume(volume)
        self._radio_audio_output = QAudioOutput()
        self._radio_audio_output.setVolume(volume)

        # Плеєр для коротких сповіщень
        self._player = QMediaPlayer()
        self._player.setAudioOutput(self._notification_audio_output)

        sound_path = get_resource_path(notification_file)
        if os.path.exists(sound_path):
            self._player.setSource(QUrl.fromLocalFile(sound_path))

        # Плеєр для онлайн-радіопотоку
        self._radio_player = QMediaPlayer()
        self._radio_player.setAudioOutput(self._radio_audio_output)
        self._radio_buffer_output = QAudioBufferOutput(self._radio_player)
        self._radio_buffer_output.audioBufferReceived.connect(
            self._on_radio_audio_buffer
        )
        self._radio_player.setAudioBufferOutput(self._radio_buffer_output)
        self._radio_level = 0.0
        self._radio_level_updated_at = 0.0
        self._radio_browser_client = RadioBrowserClient()
        stations = self._radio_browser_client.get_stations_by_country()
        print(len(stations))
        self._radio_stations = [
            station
            for station in stations
            if station.url_resolved or station.url
        ]
        self._current_index = 0 if self._radio_stations else -1

    def play_notification(self) -> None:
        """Програє файл сповіщення."""
        if self._player.mediaStatus() == QMediaPlayer.MediaStatus.NoMedia:
            return

        self._player.setPosition(0)
        self._player.play()

    def is_playing(self) -> bool:
        """Перевіряє, чи програється сповіщення."""
        return (
            self._player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )

    # --- Методи для роботи з радіо ---

    def play_radio(self, url: Optional[str] = None) -> bool:
        """Запускає відтворення переданого URL або поточного зі списку."""
        if url:
            # Якщо передано конкретний URL, оновлюємо поточний індекс
            for index, station in enumerate(self._radio_stations):
                if url in (station.url_resolved, station.url):
                    self._current_index = index
                    break
            self._radio_player.setSource(QUrl(url))
        elif self._radio_stations:
            # Якщо URL не передано, граємо станцію за поточним індексом
            if self._current_index == -1:
                self._current_index = 0
            station = self._radio_stations[self._current_index]
            current_url = station.url_resolved or station.url
            self._radio_player.setSource(QUrl(current_url))
        else:
            return False

        self._radio_level = 0.0
        self._radio_level_updated_at = 0.0
        self._radio_player.play()
        return True

    def play_next_station(self) -> Optional[str]:
        """Перемикає на наступну станцію по колу і повертає її URL."""
        if not self._radio_stations:
            return None

        self._current_index = (self._current_index + 1) % len(self._radio_stations)
        station = self._radio_stations[self._current_index]
        next_url = station.url_resolved or station.url
        self.play_radio()
        return next_url

    def play_previous_station(self) -> Optional[str]:
        """Перемикає на попередню станцію по колу і повертає її URL."""
        if not self._radio_stations:
            return None

        if self._current_index == -1:
            self._current_index = 0
        self._current_index = (self._current_index - 1) % len(self._radio_stations)
        station = self._radio_stations[self._current_index]
        prev_url = station.url_resolved or station.url
        self.play_radio()
        return prev_url

    def get_current_station_name(self) -> str:
        """Повертає назву вибраної станції."""
        if not 0 <= self._current_index < len(self._radio_stations):
            return "Станцій не знайдено"
        return self._radio_stations[self._current_index].name or "Без назви"

    def get_station_position(self) -> tuple[int, int]:
        """Повертає номер вибраної станції та кількість доступних станцій."""
        station_count = len(self._radio_stations)
        if not 0 <= self._current_index < station_count:
            return 0, station_count
        return self._current_index + 1, station_count

    def stop_radio(self) -> None:
        """Зупиняє програвання радіо."""
        self._radio_player.stop()
        self._radio_level = 0.0
        self._radio_level_updated_at = 0.0

    def get_radio_level(self) -> float:
        """Повертає згасаючий рівень гучності радіо в діапазоні 0..1."""
        if not self._radio_level_updated_at:
            return 0.0

        age = time.monotonic() - self._radio_level_updated_at
        freshness = max(0.0, 1.0 - age / 0.3)
        return self._radio_level * freshness * self._radio_audio_output.volume()

    def _on_radio_audio_buffer(self, buffer: QAudioBuffer) -> None:
        if not buffer.isValid() or buffer.sampleCount() == 0:
            return

        sample_format = buffer.format().sampleFormat()
        sample_formats = {
            QAudioFormat.SampleFormat.Float: ("=f", 1.0),
            QAudioFormat.SampleFormat.Int16: ("=h", 1 / 32768),
            QAudioFormat.SampleFormat.Int32: ("=i", 1 / 2147483648),
        }
        raw_samples = buffer.constData().asstring(buffer.byteCount())

        if sample_format == QAudioFormat.SampleFormat.UInt8:
            samples = ((sample - 128) / 128 for sample in raw_samples)
        else:
            sample_format_info = sample_formats.get(sample_format)
            if sample_format_info is None:
                return
            struct_format, scale = sample_format_info
            samples = (
                value * scale
                for (value,) in struct.iter_unpack(struct_format, raw_samples)
            )

        sum_squares = 0.0
        sample_count = 0
        for sample in samples:
            if math.isfinite(sample):
                sum_squares += sample * sample
                sample_count += 1

        if not sample_count:
            return

        rms = math.sqrt(sum_squares / sample_count)
        self._radio_level = min(1.0, max(0.0, rms - 0.01) * 4)
        self._radio_level_updated_at = time.monotonic()

    def set_radio_volume(self, volume: float) -> None:
        """Змінює гучність радіо незалежно від сповіщень."""
        self._radio_audio_output.setVolume(max(0.0, min(1.0, volume)))

    def is_radio_playing(self) -> bool:
        return (
            self._radio_player.playbackState()
            == QMediaPlayer.PlaybackState.PlayingState
        )