import math
import os
import sys

# Приховуємо службові попередження Qt та FFmpeg
os.environ["QT_LOGGING_RULES"] = (
    "qt.multimedia.ffmpeg=false;qt.accessibility.atspi=false"
)

from PyQt6.QtCore import (
    QEasingCurve,
    QPoint,
    QRectF,
    Qt,
    QTimer,
    QUrl,
    QVariantAnimation,
)
from PyQt6.QtGui import QColor, QCursor, QFont, QIntValidator, QPainter, QPainterPath, QPen
from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
from PyQt6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


def get_resource_path(relative_path):
    """Отримує шлях до ресурсів для звичайного запуску та PyInstaller"""
    if hasattr(sys, "_MEIPASS"):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


class RoboAssistant(QWidget):

    def __init__(self):
        super().__init__()

        # --- НАЛАШТУВАННЯ ВІКНА ---
        self.setWindowFlags(
            Qt.WindowType.FramelessWindowHint
            | Qt.WindowType.WindowStaysOnTopHint
            | Qt.WindowType.Tool
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.base_width = 130
        self.base_height = 85
        self.settings_height = 30
        self.resize(self.base_width, self.base_height)

        screen = QApplication.primaryScreen().geometry()
        self.move((screen.width() - self.width()) // 2, 20)

        # --- ЗВУКОВИЙ ПЛЕЄР ТА СТАН РОТА ---
        self.audio_output = QAudioOutput(self)
        self.media_player = QMediaPlayer(self)
        self.media_player.setAudioOutput(self.audio_output)

        sound_path = get_resource_path("positive-notification.mp3")
        if os.path.exists(sound_path):
            self.media_player.setSource(QUrl.fromLocalFile(sound_path))
        self.audio_output.setVolume(0.8)

        # Прапорець відкриття рота під час відтворення звуку
        self.is_talking = False
        self.media_player.mediaStatusChanged.connect(self.on_media_status_changed)

        # --- СТАН ОЧЕЙ ТА ІНТЕРФЕЙСУ ---
        self.blink_state = 0.0
        self.blink_direction = 0
        self.is_smiling = False

        self.drag_position = QPoint()
        self.is_dragging = False

        self.eye_offset_x = 0.0
        self.eye_offset_y = 0.0

        # Прозорість знака питання
        self.question_opacity = 0.0

        # --- СТАН POMODORO ТАЙМЕРА ---
        self.WORK_TIME = 25 * 60
        self.time_left = self.WORK_TIME
        self.timer_state = "STOPPED"

        # --- ІНТЕРФЕЙС ТАЙМЕРА ТА НАЛАШТУВАНЬ ---
        self.init_ui()

        # --- АНІМАЦІЯ РОЗГОРТАННЯ ВІКНА ---
        self.size_animation = QVariantAnimation(self)
        self.size_animation.setDuration(220)
        self.size_animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.size_animation.valueChanged.connect(self.on_anim_resize)

        # --- АНІМАЦІЙНІ ТАЙМЕРИ ---
        self.anim_timer = QTimer(self)
        self.anim_timer.timeout.connect(self.update_animation)
        self.anim_timer.start(16)

        self.blink_timer = QTimer(self)
        self.blink_timer.timeout.connect(self.trigger_blink)
        self.blink_timer.start(3500)

        self.smile_reset_timer = QTimer(self)
        self.smile_reset_timer.setSingleShot(True)
        self.smile_reset_timer.timeout.connect(self.reset_smile)

        self.pomo_timer = QTimer(self)
        self.pomo_timer.timeout.connect(self.pomo_tick)

    def on_media_status_changed(self, status):
        """Вмикає або вимикає анімацію рота залежно від того, чи грає звук"""
        if status == QMediaPlayer.MediaStatus.BufferedMedia or status == QMediaPlayer.MediaStatus.LoadedMedia:
            if self.media_player.playbackState() == QMediaPlayer.PlaybackState.PlayingState:
                self.is_talking = True
            else:
                self.is_talking = False
        elif status == QMediaPlayer.MediaStatus.EndOfMedia:
            self.is_talking = False
        self.update()

    def init_ui(self):
        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(0, 4, 0, 0)
        self.main_layout.setSpacing(2)

        # 1. Верхній ряд: [ Кнопка Старт ] [ Таймер ] [ Шестерня ]
        timer_layout = QHBoxLayout()
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(4)
        timer_layout.addStretch()

        self.btn_control = QPushButton("▶", self)
        self.btn_control.setFixedSize(18, 18)
        self.btn_control.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_control.clicked.connect(self.on_timer_button_click)
        self.btn_control.setStyleSheet("""
            QPushButton {
                background-color: #0f172a;
                color: #00f0ff;
                border: 1px solid #00f0ff;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
                padding-bottom: 1px;
            }
            QPushButton:hover {
                background-color: #00f0ff;
                color: #0a0c10;
            }
        """)

        self.lbl_timer = QLabel("25:00", self)
        self.lbl_timer.setFont(QFont("Consolas", 11, QFont.Weight.Bold))
        self.lbl_timer.setStyleSheet("color: #00f0ff; background: transparent;")
        self.lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_settings = QPushButton("⚙", self)
        self.btn_settings.setFixedSize(18, 18)
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.clicked.connect(self.toggle_settings)
        self.btn_settings.setStyleSheet("""
            QPushButton {
                background-color: #0f172a;
                color: #00f0ff;
                border: 1px solid #00f0ff;
                border-radius: 4px;
                font-size: 11px;
                padding-bottom: 2px;
            }
            QPushButton:hover {
                background-color: #00f0ff;
                color: #0a0c10;
            }
        """)

        timer_layout.addWidget(self.btn_control)
        timer_layout.addWidget(self.lbl_timer)
        timer_layout.addWidget(self.btn_settings)
        timer_layout.addStretch()

        self.main_layout.addLayout(timer_layout)

        # 2. Висувна панель введення часу
        self.settings_widget = QWidget(self)
        settings_layout = QHBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(10, 2, 10, 2)
        settings_layout.setSpacing(4)

        self.input_minutes = QLineEdit(self.settings_widget)
        self.input_minutes.setPlaceholderText("хв")
        self.input_minutes.setText("25")
        self.input_minutes.setFixedHeight(22)
        self.input_minutes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Валідатор лише для додатних цілих чисел
        self.input_minutes.setValidator(QIntValidator(1, 999, self))
        self.input_minutes.returnPressed.connect(self.apply_new_time)

        self.input_minutes.setStyleSheet("""
            QLineEdit {
                background-color: #0f172a;
                color: #00f0ff;
                border: 1px solid #00f0ff;
                border-radius: 4px;
                font-size: 11px;
                font-weight: bold;
            }
        """)

        self.btn_apply = QPushButton("OK", self.settings_widget)
        self.btn_apply.setFixedSize(28, 22)
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.clicked.connect(self.apply_new_time)
        self.btn_apply.setStyleSheet("""
            QPushButton {
                background-color: #00f0ff;
                color: #0a0c10;
                border-radius: 4px;
                font-size: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #80f8ff;
            }
        """)

        settings_layout.addWidget(self.input_minutes)
        settings_layout.addWidget(self.btn_apply)

        self.settings_widget.setVisible(False)
        self.main_layout.addWidget(self.settings_widget)

        self.main_layout.addStretch()

    def toggle_settings(self):
        self.play_sound()

        opening = not self.settings_widget.isVisible()

        start_h = self.height()
        end_h = (
            self.base_height + self.settings_height
            if opening
            else self.base_height
        )

        if opening:
            self.settings_widget.setVisible(True)

        self.size_animation.stop()
        self.size_animation.setStartValue(start_h)
        self.size_animation.setEndValue(end_h)

        if not opening:
            self.size_animation.finished.connect(self._hide_settings_callback)

        self.size_animation.start()

        if opening:
            self.input_minutes.setFocus()
            self.input_minutes.selectAll()

    def _hide_settings_callback(self):
        self.settings_widget.setVisible(False)
        try:
            self.size_animation.finished.disconnect(self._hide_settings_callback)
        except TypeError:
            pass

    def on_anim_resize(self, value):
        self.resize(self.base_width, int(value))

        progress = (int(value) - self.base_height) / float(self.settings_height)
        self.question_opacity = max(0.0, min(1.0, progress))

        self.update()

    def apply_new_time(self):
        text = self.input_minutes.text().strip()
        if text.isdigit() and int(text) > 0:
            mins = int(text)
            self.WORK_TIME = mins * 60
            
            # Зупиняємо таймер та скидаємо відлік
            self.pomo_timer.stop()
            self.reset_pomo()
            self.play_sound()

        self.toggle_settings()

    def play_sound(self):
        if self.media_player.mediaStatus() != QMediaPlayer.MediaStatus.NoMedia:
            self.is_talking = True
            self.media_player.setPosition(0)
            self.media_player.play()

    def on_timer_button_click(self):
        self.play_sound()

        if self.timer_state == "STOPPED":
            self.start_pomo()
        elif self.timer_state == "RUNNING":
            self.pause_pomo()
        elif self.timer_state == "PAUSED":
            self.resume_pomo()
        elif self.timer_state == "FINISHED":
            self.reset_pomo()

    def start_pomo(self):
        self.timer_state = "RUNNING"
        self.btn_control.setText("⏸")
        self.pomo_timer.start(1000)

    def pause_pomo(self):
        self.timer_state = "PAUSED"
        self.btn_control.setText("▶")
        self.pomo_timer.stop()

    def resume_pomo(self):
        self.timer_state = "RUNNING"
        self.btn_control.setText("⏸")
        self.pomo_timer.start(1000)

    def reset_pomo(self):
        self.timer_state = "STOPPED"
        self.time_left = self.WORK_TIME
        self.update_timer_label()
        self.btn_control.setText("▶")

    def pomo_tick(self):
        if self.time_left > 0:
            self.time_left -= 1
            self.update_timer_label()
        else:
            self.pomo_timer.stop()
            self.timer_state = "FINISHED"
            self.btn_control.setText("↺")
            self.play_sound()
            self.trigger_smile()

    def update_timer_label(self):
        mins = self.time_left // 60
        secs = self.time_left % 60
        self.lbl_timer.setText(f"{mins:02d}:{secs:02d}")

    # --- АНІМАЦІЯ ТА КЛІПАННЯ ---
    def trigger_blink(self):
        if self.blink_direction == 0 and not self.is_smiling:
            self.blink_direction = 1

    def trigger_smile(self):
        self.is_smiling = True
        self.blink_state = 0.0
        self.blink_direction = 0
        self.smile_reset_timer.start(1500)

    def reset_smile(self):
        self.is_smiling = False

    def update_animation(self):
        # Відстеження статусу мовлення
        if self.media_player.playbackState() != QMediaPlayer.PlaybackState.PlayingState:
            self.is_talking = False

        if not self.is_smiling:
            if self.blink_direction == 1:
                self.blink_state += 0.25
                if self.blink_state >= 1.0:
                    self.blink_state = 1.0
                    self.blink_direction = -1
            elif self.blink_direction == -1:
                self.blink_state -= 0.25
                if self.blink_state <= 0.0:
                    self.blink_state = 0.0
                    self.blink_direction = 0

        if not self.is_smiling:
            cursor_pos = QCursor.pos()
            center = self.geometry().center()

            dx = cursor_pos.x() - center.x()
            dy = cursor_pos.y() - center.y()
            dist = math.sqrt(dx * dx + dy * dy)

            max_offset_x = 6.0
            max_offset_y = 2.0

            if dist > 0:
                target_x = (dx / max(dist, 300)) * max_offset_x
                target_y = (dy / max(dist, 300)) * max_offset_y

                target_x = max(-max_offset_x, min(max_offset_x, target_x))
                target_y = max(-max_offset_y, min(max_offset_y, target_y))

                self.eye_offset_x += (target_x - self.eye_offset_x) * 0.2
                self.eye_offset_y += (target_y - self.eye_offset_y) * 0.2
        else:
            self.eye_offset_x += (0.0 - self.eye_offset_x) * 0.2
            self.eye_offset_y += (0.0 - self.eye_offset_y) * 0.2

        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Корпус
        painter.setBrush(QColor(10, 12, 16))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, self.width(), self.height(), 9.0, 9.0)

        cyan_glow = QColor(0, 240, 255, 60)
        cyan_solid = QColor(0, 240, 255)

        eye_width = 18
        base_eye_height = 20

        eye_y_base = self.height() - 25

        left_eye_center = QPoint(
            int(37 + self.eye_offset_x), int(eye_y_base + self.eye_offset_y)
        )
        right_eye_center = QPoint(
            int(93 + self.eye_offset_x), int(eye_y_base + self.eye_offset_y)
        )

        # Малювання очей
        if self.is_smiling:
            for center in (left_eye_center, right_eye_center):
                path = QPainterPath()
                path.moveTo(center.x() - 9, center.y() - 1)
                path.quadTo(
                    center.x(), center.y() - 11, center.x() + 9, center.y() - 1
                )

                painter.setBrush(Qt.BrushStyle.NoBrush)
                painter.setPen(
                    QPen(cyan_glow, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                )
                painter.drawPath(path)

                painter.setPen(
                    QPen(cyan_solid, 3.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
                )
                painter.drawPath(path)

        else:
            current_eye_height = base_eye_height * (1.0 - self.blink_state * 0.85)
            if current_eye_height < 2:
                current_eye_height = 2

            for center in (left_eye_center, right_eye_center):
                rect = QRectF(
                    center.x() - eye_width / 2,
                    center.y() - current_eye_height / 2,
                    eye_width,
                    current_eye_height,
                )

                painter.setBrush(cyan_glow)
                painter.setPen(Qt.PenStyle.NoPen)
                glow_rect = rect.adjusted(-2, -2, 2, 2)
                painter.drawRoundedRect(glow_rect, 5.0, 5.0)

                painter.setBrush(cyan_solid)
                painter.drawRoundedRect(rect, 4.0, 4.0)

        # --- МАЛЮВАННЯ РОТА З ЗБІЛЬШЕНОЮ ВИСОТОЮ ---
        if self.is_talking:
            mouth_center_x = (left_eye_center.x() + right_eye_center.x()) / 2
            mouth_y = eye_y_base + 3
            width = 24.0
            height = 22.0  # Збільшено висоту з 16.0 до 22.0

            mouth_path = QPainterPath()
            mouth_path.moveTo(mouth_center_x - width / 2, mouth_y)
            mouth_path.lineTo(mouth_center_x + width / 2, mouth_y)
            mouth_path.arcTo(
                QRectF(
                    mouth_center_x - width / 2,
                    mouth_y - height / 2,
                    width,
                    height,
                ),
                0,
                -180,
            )
            mouth_path.closeSubpath()

            # Світіння навколо рота
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(
                QPen(cyan_glow, 6, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            )
            painter.drawPath(mouth_path)

            # Заповнення та контур рота
            painter.setBrush(cyan_solid)
            painter.setPen(
                QPen(cyan_solid, 1.5, Qt.PenStyle.SolidLine, Qt.PenCapStyle.RoundCap)
            )
            painter.drawPath(mouth_path)

        # Знак питання біля правого ока
        if self.question_opacity > 0.0:
            q_color = QColor(0, 240, 255, int(255 * self.question_opacity))
            painter.setPen(q_color)
            painter.setFont(QFont("Segoe UI", 11, QFont.Weight.Bold))

            q_x = right_eye_center.x() + 12
            q_y = right_eye_center.y() - 4
            painter.drawText(q_x, q_y, "?")

    # --- КЕРУВАННЯ МИШКОЮ ---
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            self.is_dragging = False

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.is_dragging = True

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and not self.is_dragging:
            self.trigger_smile()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    assistant = RoboAssistant()
    assistant.show()
    sys.exit(app.exec())