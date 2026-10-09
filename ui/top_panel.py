from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QFontMetrics, QIntValidator
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
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

    def build(
        self,
        layout: QVBoxLayout,
        initial_minutes: int,
        initial_radio_volume: float = 0.8,
        initial_radio_station_name: str = "",
        initial_radio_station_position: tuple[int, int] = (0, 0),
    ):
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
        settings_layout = QVBoxLayout(self.settings_widget)
        settings_layout.setContentsMargins(
            round(8 * s),
            round(4 * s),
            round(8 * s),
            round(4 * s),
        )
        settings_layout.setSpacing(round(4 * s))

        settings_layout.addWidget(self._separator(self.settings_widget, s))

        timer_settings_layout = QHBoxLayout()
        timer_settings_layout.setContentsMargins(0, 0, 0, 0)
        timer_settings_layout.setSpacing(round(4*s))

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

        timer_settings_layout.addWidget(self.input_minutes)
        timer_settings_layout.addWidget(self.btn_apply)
        settings_layout.addLayout(timer_settings_layout)

        settings_layout.addWidget(self._separator(self.settings_widget, s))

        radio_header_layout = QHBoxLayout()
        radio_header_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_station_name = QLabel(self.settings_widget)
        self.lbl_station_name.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_station_name.setFixedWidth(
            max(1, self.parent.width() - round(16 * s))
        )
        self.lbl_station_name.setFixedHeight(round(18 * s))
        self.lbl_station_name.setStyleSheet("color: #00f0ff; background: transparent;")
        radio_header_layout.addWidget(self.lbl_station_name)
        settings_layout.addLayout(radio_header_layout)

        radio_controls_layout = QHBoxLayout()
        radio_controls_layout.setContentsMargins(0, 0, 0, 0)
        radio_controls_layout.setSpacing(round(4*s))
        radio_controls_layout.addStretch()

        self.btn_radio_previous = QPushButton("⏮", self.settings_widget)
        self.btn_radio_toggle = QPushButton("▶", self.settings_widget)
        self.btn_radio_next = QPushButton("⏭", self.settings_widget)
        for button in (
            self.btn_radio_previous,
            self.btn_radio_toggle,
            self.btn_radio_next,
        ):
            button.setFixedSize(round(18*s), round(18*s))
            button.setCursor(Qt.CursorShape.PointingHandCursor)
            button.setStyleSheet(self._button_style(s))

        self.btn_radio_previous.setToolTip("Попередня станція")
        self.btn_radio_toggle.setToolTip("Увімкнути радіо")
        self.btn_radio_next.setToolTip("Наступна станція")

        radio_controls_layout.addWidget(self.btn_radio_previous)
        radio_controls_layout.addWidget(self.btn_radio_toggle)
        radio_controls_layout.addWidget(self.btn_radio_next)
        radio_controls_layout.addStretch()
        settings_layout.addLayout(radio_controls_layout)

        volume_layout = QHBoxLayout()
        volume_layout.setContentsMargins(0, 0, 0, 0)
        volume_layout.setSpacing(round(4*s))

        self.lbl_radio_volume = QLabel("♪", self.settings_widget)
        self.lbl_radio_volume.setToolTip("Гучність радіо")
        self.lbl_radio_volume.setStyleSheet("color: #00f0ff; background: transparent;")

        self.slider_radio_volume = QSlider(
            Qt.Orientation.Horizontal,
            self.settings_widget,
        )
        self.slider_radio_volume.setRange(0, 100)
        self.slider_radio_volume.setValue(round(initial_radio_volume * 100))
        self.slider_radio_volume.setFixedHeight(round(18*s))
        self.slider_radio_volume.setToolTip("Гучність радіо")
        self.slider_radio_volume.setStyleSheet(self._slider_style(s))

        self.lbl_radio_volume_value = QLabel(
            f"{self.slider_radio_volume.value()}%",
            self.settings_widget,
        )
        self.lbl_radio_volume_value.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self.lbl_radio_volume_value.setStyleSheet("color: #00f0ff; background: transparent;")
        self.lbl_radio_volume_value.setFixedWidth(round(26*s))

        self.slider_radio_volume.valueChanged.connect(
            lambda value: self.lbl_radio_volume_value.setText(f"{value}%")
        )
        volume_layout.addWidget(self.lbl_radio_volume)
        volume_layout.addWidget(self.slider_radio_volume, 1)
        volume_layout.addWidget(self.lbl_radio_volume_value)
        settings_layout.addLayout(volume_layout)

        self._radio_station_name = ""
        self._radio_station_position = (0, 0)
        self.set_radio_station_name(initial_radio_station_name)
        self.set_radio_station_position(*initial_radio_station_position)

        self.settings_widget.setVisible(False)
        layout.addWidget(self.settings_widget)
        layout.addStretch()

    def set_radio_station_name(self, name: str):
        self._radio_station_name = name or "Станцій не знайдено"
        self._update_radio_station_label()

    def set_radio_station_position(self, index: int, count: int):
        self._radio_station_position = (index, count)
        self._update_radio_station_label()

    def _update_radio_station_label(self):
        index, count = self._radio_station_position
        display_name = f"{self._radio_station_name} ({index}/{count})"
        self.lbl_station_name.setToolTip(display_name)
        self.lbl_station_name.setText(
            QFontMetrics(self.lbl_station_name.font()).elidedText(
                display_name,
                Qt.TextElideMode.ElideRight,
                self.lbl_station_name.width(),
            )
        )

    @staticmethod
    def _separator(parent: QWidget, scale: float) -> QFrame:
        separator = QFrame(parent)
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Plain)
        separator.setFixedHeight(max(1, round(scale)))
        separator.setStyleSheet("color: rgba(0, 240, 255, 110);")
        return separator

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

    @staticmethod
    def _slider_style(s):
        return f"""
            QSlider::groove:horizontal {{
                height: {max(2, round(3*s))}px;
                background: #0f172a;
                border: {max(1, round(s))}px solid #00f0ff;
                border-radius: {round(2*s)}px;
            }}
            QSlider::sub-page:horizontal {{
                background: #00f0ff;
                border-radius: {round(2*s)}px;
            }}
            QSlider::handle:horizontal {{
                width: {round(10*s)}px;
                margin: {-round(4*s)}px 0;
                background: #00f0ff;
                border-radius: {round(5*s)}px;
            }}
        """
