from dataclasses import dataclass


@dataclass(frozen=True)
class WindowConfig:
    """Єдине місце для керування базовим розміром та масштабом вікна."""

    BASE_WIDTH: int = 130
    BASE_HEIGHT: int = 85

    # ЗМІНЮЙТЕ ЛИШЕ ЦЕ ЗНАЧЕННЯ ДЛЯ МАСШТАБУ ВІКНА.
    # 1.0 = 130x85, 1.5 = 195x128, 2.0 = 260x170 тощо.
    SCALE: float = 1.2

    SETTINGS_HEIGHT: int = 114

    @property
    def width(self) -> int:
        return round(self.BASE_WIDTH * self.SCALE)

    @property
    def height(self) -> int:
        return round(self.BASE_HEIGHT * self.SCALE)

    @property
    def settings_height(self) -> int:
        return round(self.SETTINGS_HEIGHT * self.SCALE)


@dataclass(frozen=True)
class AnimationConfig:
    FRAME_INTERVAL_MS: int = 16
    BLINK_INTERVAL_MS: int = 3500
    BLINK_STEP: float = 0.25
    EYE_SMOOTHING: float = 0.2
    SMILE_DURATION_MS: int = 1500
    SETTINGS_ANIMATION_MS: int = 220


@dataclass(frozen=True)
class TimerConfig:
    DEFAULT_WORK_MINUTES: int = 25
    MIN_MINUTES: int = 1
    MAX_MINUTES: int = 999


@dataclass(frozen=True)
class AudioConfig:
    VOLUME: float = 0.8
    # NOTIFICATION_FILE: str = "positive-notification.mp3"
    NOTIFICATION_FILE: str = "mixkit.wav"
