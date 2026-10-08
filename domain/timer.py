from enum import Enum, auto


class TimerState(Enum):
    STOPPED = auto()
    RUNNING = auto()
    PAUSED = auto()
    FINISHED = auto()


class PomodoroTimer:
    """Чиста бізнес-логіка таймера без залежності від Qt."""

    def __init__(self, work_minutes: int):
        self.work_time = work_minutes * 60
        self.time_left = self.work_time
        self.state = TimerState.STOPPED

    def start(self) -> None:
        if self.state == TimerState.STOPPED:
            self.state = TimerState.RUNNING

    def pause(self) -> None:
        if self.state == TimerState.RUNNING:
            self.state = TimerState.PAUSED

    def resume(self) -> None:
        if self.state == TimerState.PAUSED:
            self.state = TimerState.RUNNING

    def reset(self) -> None:
        self.state = TimerState.STOPPED
        self.time_left = self.work_time

    def tick(self) -> bool:
        """Зменшує час на секунду. Повертає True, якщо таймер завершився."""
        if self.state != TimerState.RUNNING:
            return False

        if self.time_left > 0:
            self.time_left -= 1

        if self.time_left == 0:
            self.state = TimerState.FINISHED
            return True

        return False

    def set_work_minutes(self, minutes: int) -> None:
        if minutes <= 0:
            raise ValueError("Minutes must be greater than zero.")

        self.work_time = minutes * 60
        self.reset()

    @property
    def is_running(self) -> bool:
        return self.state == TimerState.RUNNING
