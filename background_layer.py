#background_layer.py -- v5.1
#Was originally part of menu_ui but split off due to some bugs/issues

from PySide6.QtGui import QPainter, QColor
from PySide6.QtCore import Qt
from transparent_canvas import TransparentCanvasWindow

class BackgroundLayer(TransparentCanvasWindow):
    def __init__(self):
        super().__init__()
        self.current_screen_index = 0
        self.background_color = QColor(0, 0, 0, 1)  
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.enable_passthrough()

    def set_background_color(self, screen_index, color: QColor):
        if 0 <= screen_index < len(self.screen_geometries):
            self.current_screen_index = screen_index
            self.background_color = color
            self.setGeometry(self.screen_geometries[screen_index])
            self.update()
            self.repaint()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.background_color)
