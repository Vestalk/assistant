import os
import sys

from PyQt6.QtCore import QEasingCurve, QPoint, Qt, QVariantAnimation
from PyQt6.QtGui import QPainter
from PyQt6.QtWidgets import QVBoxLayout, QWidget
from PyQt6.QtCore import QTimer

from config import AnimationConfig, AudioConfig, TimerConfig, WindowConfig
from domain.timer import PomodoroTimer, TimerState
from services.audio_service import AudioService
from ui.face_animation import FaceAnimationController
from ui.face_painter import FacePainter
from ui.face_state import FaceState
from ui.top_panel import TopPanel


class RoboAssistant(QWidget):
    """Головний UI-компонент. Координує окремі компоненти програми."""

    def __init__(self):
        super().__init__()

        self.window_config = WindowConfig()
        self.animation_config = AnimationConfig()
        self.timer_config = TimerConfig()
        self.audio_config = AudioConfig()

        self._configure_window()
        self._create_services()
        self._create_state()
        self._create_ui()
        self._create_animations()

    def _configure_window(self):
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        
        # for MAC OS
        if sys.platform == "darwin":
            self.setAttribute(Qt.WidgetAttribute.WA_MacAlwaysShowToolWindow, True)
        
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.resize(self.window_config.width, self.window_config.height)

        screen = self.screen().geometry()
        self.move(
            (screen.width() - self.width()) // 2,
            round(20 * self.window_config.SCALE),
        )

    def _create_services(self):
        self.audio_service = AudioService(
            self.audio_config.VOLUME,
            self.audio_config.NOTIFICATION_FILE,
        )

    def _create_state(self):
        self.face_state = FaceState()
        self.timer = PomodoroTimer(self.timer_config.DEFAULT_WORK_MINUTES)

        self.drag_position = QPoint()
        self.is_dragging = False

    def _create_ui(self):
        self.main_layout = QVBoxLayout(self)
        s = self.window_config.SCALE
        self.main_layout.setContentsMargins(0, round(4*s), 0, 0)
        self.main_layout.setSpacing(round(2*s))

        self.timer_panel = TopPanel(
            self,
            s,
            self.timer_config.MIN_MINUTES,
            self.timer_config.MAX_MINUTES,
        )
        self.timer_panel.build(
            self.main_layout,
            self.timer_config.DEFAULT_WORK_MINUTES,
        )

        self.timer_panel.btn_control.clicked.connect(self.on_timer_button_click)
        self.timer_panel.btn_settings.clicked.connect(self.toggle_settings)
        self.timer_panel.btn_apply.clicked.connect(self.apply_new_time)
        self.timer_panel.input_minutes.returnPressed.connect(self.apply_new_time)

        self.update_timer_label()

    def _create_animations(self):
        self.face_painter = FacePainter(self.window_config)

        self.size_animation = QVariantAnimation(self)
        self.size_animation.setDuration(self.animation_config.SETTINGS_ANIMATION_MS)
        self.size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.size_animation.valueChanged.connect(self._on_resize_animation)

        self.face_animation = FaceAnimationController(
            self.face_state,
            self,
            self.audio_service,
            self.animation_config,
        )

        self.pomo_timer = QTimer(self)
        self.pomo_timer.timeout.connect(self._pomo_tick)

    # ---------------- TIMER ----------------

    def on_timer_button_click(self):
        self.play_sound()

        if self.timer.state == TimerState.STOPPED:
            self.start_pomo()
        elif self.timer.state == TimerState.RUNNING:
            self.pause_pomo()
        elif self.timer.state == TimerState.PAUSED:
            self.resume_pomo()
        elif self.timer.state == TimerState.FINISHED:
            self.reset_pomo()

    def start_pomo(self):
        self.timer.start()
        self.timer_panel.btn_control.setText("⏸")
        self.pomo_timer.start(1000)

    def pause_pomo(self):
        self.timer.pause()
        self.timer_panel.btn_control.setText("▶")
        self.pomo_timer.stop()

    def resume_pomo(self):
        self.timer.resume()
        self.timer_panel.btn_control.setText("⏸")
        self.pomo_timer.start(1000)

    def reset_pomo(self):
        self.timer.reset()
        self.timer_panel.btn_control.setText("▶")
        self.update_timer_label()

    def _pomo_tick(self):
        if self.timer.tick():
            self.pomo_timer.stop()
            self.timer_panel.btn_control.setText("↺")
            self.play_sound()
            self.face_animation.trigger_smile()

        self.update_timer_label()

    def apply_new_time(self):
        text = self.timer_panel.input_minutes.text().strip()
        if text.isdigit() and int(text) > 0:
            self.timer.set_work_minutes(int(text))
            self.pomo_timer.stop()
            self.update_timer_label()
            self.play_sound()

        self.toggle_settings()

    def update_timer_label(self):
        minutes = self.timer.time_left // 60
        seconds = self.timer.time_left % 60
        self.timer_panel.lbl_timer.setText(f"{minutes:02d}:{seconds:02d}")

    # ---------------- SETTINGS ----------------

    def toggle_settings(self):
        self.play_sound()

        opening = not self.timer_panel.settings_widget.isVisible()
        start_height = self.height()
        end_height = (
            self.window_config.height + self.window_config.settings_height
            if opening
            else self.window_config.height
        )

        if opening:
            self.timer_panel.settings_widget.setVisible(True)

        self.size_animation.stop()
        self.size_animation.setStartValue(start_height)
        self.size_animation.setEndValue(end_height)

        if not opening:
            try:
                self.size_animation.finished.disconnect(self._hide_settings)
            except TypeError:
                pass
            self.size_animation.finished.connect(self._hide_settings)

        self.size_animation.start()

        if opening:
            self.timer_panel.input_minutes.setFocus()
            self.timer_panel.input_minutes.selectAll()

    def _hide_settings(self):
        self.timer_panel.settings_widget.setVisible(False)
        try:
            self.size_animation.finished.disconnect(self._hide_settings)
        except TypeError:
            pass

    def _on_resize_animation(self, value):
        self.resize(self.window_config.width, int(value))

        base = self.window_config.height
        settings = self.window_config.settings_height
        progress = 0 if settings == 0 else (int(value) - base) / settings
        self.face_state.question_opacity = max(0.0, min(1.0, progress))
        self.update()

    # ---------------- SOUND ----------------

    def play_sound(self):
        self.audio_service.play_notification()

    # ---------------- PAINTING ----------------

    def paintEvent(self, event):
        painter = QPainter(self)
        self.face_painter.paint(
            painter,
            self.width(),
            self.height(),
            self.face_state,
        )

    # ---------------- MOUSE ----------------

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint()
                - self.frameGeometry().topLeft()
            )
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(
                event.globalPosition().toPoint() - self.drag_position
            )
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        if (
            event.button() == Qt.MouseButton.LeftButton
            and not self.is_dragging
        ):
            self.face_animation.trigger_smile()
