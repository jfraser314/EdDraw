# Make window transparent and the size of the screen
# Based on CodeMonkey method https://www.youtube.com/watch?v=XozHdfHrb1U
# Windows only

import ctypes
from PySide6.QtWidgets import QWidget, QApplication
from PySide6.QtCore import Qt, QRect
from PySide6.QtGui import QPainter, QColor

# DPI & Transparency Settings
ctypes.windll.shcore.SetProcessDpiAwareness(2)  # Per-monitor DPI awareness

# Passthrough constants
GWL_EXSTYLE = -20
WS_EX_LAYERED = 0x80000
WS_EX_TRANSPARENT = 0x20

def set_os_passthrough(window, enable: bool):
    hwnd = int(window.winId())
    style = ctypes.windll.user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
    style |= WS_EX_LAYERED
    if enable:
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style | WS_EX_TRANSPARENT)
    else:
        ctypes.windll.user32.SetWindowLongW(hwnd, GWL_EXSTYLE, style & ~WS_EX_TRANSPARENT)

class TransparentCanvasWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.background_color = QColor(0, 0, 0, 1)  # Default transparent background

        # Calculate full virtual screen geometry manually
        screens = QApplication.screens()
        left = top = 99999
        right = bottom = -99999
        self.screen_geometries = []

        for screen in screens:
            g = screen.geometry()
            self.screen_geometries.append(g)
            left = min(left, g.left())
            top = min(top, g.top())
            right = max(right, g.right())
            bottom = max(bottom, g.bottom())

        self.virtual_geometry = QRect(left, top, right - left + 1, bottom - top + 1)

        # Configure canvas window
        self.setGeometry(self.virtual_geometry)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setMouseTracking(True)
        set_os_passthrough(self, False)

    #Enable and Disable methods called from main.py, menu_ui.py, and background_layer.py
    def enable_passthrough(self):
        set_os_passthrough(self, True)

    def disable_passthrough(self):
        set_os_passthrough(self, False)

    def get_painter(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.fillRect(self.rect(), self.background_color)
        return painter
