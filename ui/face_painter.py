from PyQt6.QtCore import QPoint, QRectF, Qt
from PyQt6.QtGui import QColor, QFont, QPainter, QPainterPath, QPen

from config import WindowConfig
from ui.face_state import FaceState


class FacePainter:
    """Тільки малювання робота. Не знає про таймер, звук чи кнопки."""

    CYAN = QColor(0, 240, 255)
    DARK = QColor(10, 12, 16)
    GLOW = QColor(0, 240, 255, 60)

    def __init__(self, window_config: WindowConfig):
        self.config = window_config

    def paint(self, painter: QPainter, width: int, height: int, state: FaceState):
        scale = self.config.SCALE
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        painter.setBrush(self.DARK)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRoundedRect(0, 0, width, height, 9 * scale, 9 * scale)

        eye_width = 18 * scale
        base_eye_height = 25 * scale
        eye_y_base = height - 25 * scale
        eye_x = state.eye_offset_x + state.eye_dance_x * scale
        eye_y = state.eye_offset_y + state.eye_dance_y * scale

        left_center = QPoint(
            round(37 * scale + eye_x),
            round(eye_y_base + eye_y),
        )
        right_center = QPoint(
            round(93 * scale + eye_x),
            round(eye_y_base + eye_y),
        )

        if state.smiling:
            self._draw_smiling_eye(painter, left_center, scale)
            self._draw_smiling_eye(painter, right_center, scale)
        else:
            current_height = max(
                2 * scale,
                base_eye_height * (1.0 - state.blink_state * 0.85),
            )
            for center in (left_center, right_center):
                rect = QRectF(
                    center.x() - eye_width / 2,
                    center.y() - current_height / 2,
                    eye_width,
                    current_height,
                )

                painter.setBrush(self.GLOW)
                painter.setPen(Qt.PenStyle.NoPen)
                painter.drawRoundedRect(rect.adjusted(-2 * scale, -2 * scale,
                                                       2 * scale, 2 * scale),
                                         5 * scale, 5 * scale)

                painter.setBrush(self.CYAN)
                painter.drawRoundedRect(rect, 4 * scale, 4 * scale)

        if state.talking or state.singing:
            self._draw_mouth(
                painter,
                left_center,
                right_center,
                eye_y_base,
                scale,
                state.mouth_opening,
            )

        if state.question_opacity > 0:
            self._draw_question_mark(painter, right_center, state.question_opacity, scale)

        painter.restore()

    def _draw_smiling_eye(self, painter, center: QPoint, scale: float):
        path = QPainterPath()
        path.moveTo(center.x() - 9 * scale, center.y() - scale)
        path.quadTo(
            center.x(),
            center.y() - 11 * scale,
            center.x() + 9 * scale,
            center.y() - scale,
        )

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.GLOW, 6 * scale, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

        painter.setPen(QPen(self.CYAN, 3.5 * scale, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

    def _draw_mouth(self, painter, left, right, eye_y_base, scale, openness):
        center_x = (left.x() + right.x()) / 2
        mouth_y = eye_y_base + 3 * scale
        width = 24 * scale
        height = max(2 * scale, 50 * scale * openness)

        path = QPainterPath()
        path.moveTo(center_x - width / 2, mouth_y)
        path.lineTo(center_x + width / 2, mouth_y)
        path.arcTo(
            QRectF(center_x - width / 2, mouth_y - height / 2, width, height),
            0, -180,
        )
        path.closeSubpath()

        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.setPen(QPen(self.GLOW, 6 * scale, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

        painter.setBrush(self.CYAN)
        painter.setPen(QPen(self.CYAN, 1.5 * scale, Qt.PenStyle.SolidLine,
                            Qt.PenCapStyle.RoundCap))
        painter.drawPath(path)

    def _draw_question_mark(self, painter, center, opacity, scale):
        painter.setPen(QColor(0, 240, 255, round(255 * opacity)))
        painter.setFont(QFont("Segoe UI", round(11 * scale), QFont.Weight.Bold))
        painter.drawText(
            round(center.x() + 12 * scale),
            round(center.y() - 4 * scale),
            "?",
        )
