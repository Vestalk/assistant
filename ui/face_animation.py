from PyQt6.QtCore import QTimer
from PyQt6.QtGui import QCursor

class FaceAnimationController:
    """Керує станом очей/рота та не малює UI."""

    def __init__(self, face_state, widget, audio_service, config):
        self.state = face_state
        self.widget = widget
        self.audio_service = audio_service
        self.config = config

        self.animation_timer = QTimer(widget)
        self.animation_timer.timeout.connect(self.update)
        self.animation_timer.start(config.FRAME_INTERVAL_MS)

        self.blink_timer = QTimer(widget)
        self.blink_timer.timeout.connect(self.trigger_blink)
        self.blink_timer.start(config.BLINK_INTERVAL_MS)

        self.smile_reset_timer = QTimer(widget)
        self.smile_reset_timer.setSingleShot(True)
        self.smile_reset_timer.timeout.connect(self.reset_smile)

    def trigger_blink(self):
        if self.state.blink_direction == 0 and not self.state.smiling:
            self.state.blink_direction = 1

    def trigger_smile(self):
        self.state.smiling = True
        self.state.blink_state = 0.0
        self.state.blink_direction = 0
        self.smile_reset_timer.start(self.config.SMILE_DURATION_MS)

    def reset_smile(self):
        self.state.smiling = False

    def update(self):
        self.state.talking = self.audio_service.is_playing()

        if self.state.smiling:
            self._center_eyes()
        else:
            self._update_blink()
            self._update_eyes()

        self.widget.update()

    def _update_blink(self):
        if self.state.blink_direction == 1:
            self.state.blink_state += self.config.BLINK_STEP
            if self.state.blink_state >= 1:
                self.state.blink_state = 1
                self.state.blink_direction = -1
        elif self.state.blink_direction == -1:
            self.state.blink_state -= self.config.BLINK_STEP
            if self.state.blink_state <= 0:
                self.state.blink_state = 0
                self.state.blink_direction = 0

    def _update_eyes(self):
        cursor = QCursor.pos()
        center = self.widget.geometry().center()

        dx = cursor.x() - center.x()
        dy = cursor.y() - center.y()
        dist = (dx * dx + dy * dy) ** 0.5

        if dist == 0:
            return

        max_x = 6.0
        max_y = 2.0
        target_x = (dx / max(dist, 300)) * max_x
        target_y = (dy / max(dist, 300)) * max_y

        target_x = max(-max_x, min(max_x, target_x))
        target_y = max(-max_y, min(max_y, target_y))

        smoothing = self.config.EYE_SMOOTHING
        self.state.eye_offset_x += (target_x - self.state.eye_offset_x) * smoothing
        self.state.eye_offset_y += (target_y - self.state.eye_offset_y) * smoothing

    def _center_eyes(self):
        smoothing = self.config.EYE_SMOOTHING
        self.state.eye_offset_x += -self.state.eye_offset_x * smoothing
        self.state.eye_offset_y += -self.state.eye_offset_y * smoothing
