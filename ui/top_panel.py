from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QIntValidator
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QVBoxLayout,
    QWidget,
)


class TopPanel:
    """Створення та стилізація панелі керування таймером."""

    def __init__(self, parent: QWidget, scale: float, min_minutes: int, max_minutes: int):
        self.parent = parent
        self.scale = scale
        self.min_minutes = min_minutes
        self.max_minutes = max_minutes

    def build(self, layout: QVBoxLayout, initial_minutes: int):
        s = self.scale

        timer_layout = QHBoxLayout()
        timer_layout.setContentsMargins(0, 0, 0, 0)
        timer_layout.setSpacing(round(4 * s))
        timer_layout.addStretch()

        self.btn_control = QPushButton("▶", self.parent)
        self.btn_control.setFixedSize(round(18 * s), round(18 * s))
        self.btn_control.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_control.setStyleSheet(self._button_style(s))

        self.lbl_timer = QLabel(self.parent)
        self.lbl_timer.setFont(QFont("Consolas", round(11 * s), QFont.Weight.Bold))
        self.lbl_timer.setStyleSheet("color: #00f0ff; background: transparent;")
        self.lbl_timer.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.btn_settings = QPushButton("⚙", self.parent)
        self.btn_settings.setFixedSize(round(18 * s), round(18 * s))
        self.btn_settings.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_settings.setStyleSheet(self._button_style(s))
        
        timer_layout.addWidget(self.btn_control)
        timer_layout.addWidget(self.lbl_timer)
        timer_layout.addWidget(self.btn_settings)
        timer_layout.addStretch()
        layout.addLayout(timer_layout)

        self.settings_widget = QWidget(self.parent)
        settings_layout = QHBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(round(10*s), round(2*s), round(10*s), round(2*s))
        settings_layout.setSpacing(round(4*s))

        self.input_minutes = QLineEdit(self.settings_widget)
        self.input_minutes.setPlaceholderText("хв")
        self.input_minutes.setText(str(initial_minutes))
        self.input_minutes.setFixedHeight(round(22*s))
        self.input_minutes.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_minutes.setValidator(
            QIntValidator(self.min_minutes, self.max_minutes, self.parent)
        )
        self.input_minutes.setStyleSheet(self._input_style(s))

        self.btn_apply = QPushButton("OK", self.settings_widget)
        self.btn_apply.setFixedSize(round(18*s), round(18*s))
        self.btn_apply.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_apply.setStyleSheet(self._apply_style(s))
        
        self.btn_radio = QPushButton("♬", self.parent)
        self.btn_radio.setFixedSize(round(18 * s), round(18 * s))
        self.btn_radio.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_radio.setStyleSheet(self._apply_style(s))

        settings_layout.addWidget(self.input_minutes)
        settings_layout.addWidget(self.btn_apply)
        settings_layout.addWidget(self.btn_radio)

        self.settings_widget.setVisible(False)
        layout.addWidget(self.settings_widget)
        layout.addStretch()

    @staticmethod
    def _button_style(s):
        return f"""
            QPushButton {{
                background-color: #0f172a;
                color: #00f0ff;
                border: {max(1, round(s))}px solid #00f0ff;
                border-radius: {round(4*s)}px;
                font-size: {round(11*s)}px;
                font-weight: bold;
                padding-bottom: {round(2*s)}px;
            }}
            QPushButton:hover {{
                background-color: #00f0ff;
                color: #0a0c10;
            }}
        """

    @staticmethod
    def _input_style(s):
        return f"""
            QLineEdit {{
                background-color: #0f172a;
                color: #00f0ff;
                border: {max(1, round(s))}px solid #00f0ff;
                border-radius: {round(4*s)}px;
                font-size: {round(11*s)}px;
                font-weight: bold;
            }}
        """

    @staticmethod
    def _apply_style(s):
        return f"""
            QPushButton {{
                background-color: #00f0ff;
                color: #0a0c10;
                border-radius: {round(4*s)}px;
                font-size: {round(10*s)}px;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #80f8ff;
            }}
        """
