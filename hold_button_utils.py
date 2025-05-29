# hold_button_utils.py
# Entire class ritten by ChatGPT 4o

from PySide6.QtCore import QTimer, Qt, QRectF
from PySide6.QtGui import QPainter, QColor, QPainterPath
from PySide6.QtWidgets import QLabel

class RadialFillOverlay(QLabel):
    def __init__(self, button, duration_ms):
        super().__init__(button)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setGeometry(button.rect())
        self.progress = 0.0
        self.setVisible(False)

        self.duration = duration_ms
        self.update_interval = 16  # ~60 FPS
        self.steps = self.duration / self.update_interval
        self.increment = 1.0 / self.steps

        self.timer = QTimer()
        self.timer.timeout.connect(self.update_progress)

    def start(self):
        self.progress = 0.0
        self.setVisible(True)
        self.timer.start(self.update_interval)

    def stop(self):
        self.timer.stop()
        self.setVisible(False)
        self.progress = 0.0
        self.update()

    def update_progress(self):
        self.progress += self.increment
        if self.progress >= 1.0:
            self.progress = 1.0
            self.timer.stop()
        self.update()

    def paintEvent(self, event):
        if self.progress <= 0.0:
            return

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)

        size = min(self.width(), self.height())
        offset = (self.width() - size) / 2
        rect = QRectF(offset, offset, size, size)

        path = QPainterPath()
        path.moveTo(rect.center())
        path.arcTo(rect, 90, -360 * self.progress)
        path.lineTo(rect.center())

        painter.setBrush(QColor(255, 88, 88))
        painter.drawPath(path)
        painter.end()


def make_button_holdable(button, hold_duration_ms, callback):
    original_leave_event = button.leaveEvent

    timer = QTimer()
    timer.setSingleShot(True)

    overlay = RadialFillOverlay(button, hold_duration_ms)

    def on_press():
        overlay.start()
        timer.start(hold_duration_ms)

    def on_release():
        overlay.stop()
        timer.stop()

    def on_leave(event):
        overlay.stop()
        timer.stop()
        if original_leave_event:
            return original_leave_event(event)
        
    button.leaveEvent = on_leave

    def on_timeout():
        overlay.stop()
        callback()

    button.pressed.connect(on_press)
    button.released.connect(on_release)
    timer.timeout.connect(on_timeout)
    button.leaveEvent = on_leave
