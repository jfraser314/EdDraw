#dock_tab.py -- v5.1
#Visual layout created using AI

from PySide6.QtWidgets import QWidget
from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPainter, QMouseEvent, QPainterPath, QColor, QPolygonF, QPixmap
import os
import sys

# Support for PyInstaller resource path
def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

class DockTab(QWidget):
    def __init__(self, canvas, menu, parent=None):
        super().__init__(parent)
        self.canvas = canvas
        self.menu = menu
        self.menu_visible = True
        
        #Tab Dimensions - Seems a little big to me, but we will see after some testing
        self.tab_width = 40
        self.tab_height = 100
        self.fixed_x = 0

        #Container Dimensions
        self.container_width = 80
        self.container_height = 160
        self.offset_x = 15
        self.container_buffer = (self.container_width - self.tab_width)/2 - self.offset_x

        #Clamp Y before bottom of screen, helps with screens of different y values in same setup
        self.clamp_y_offset = 24
        
        #Dragging (is moving) and Dragged (has been moved) variables
        self.dragging = False
        self.dragged = False
        
        # Set initial geometry (right side, 3/4 up the screen)
        screen_geometry = self.canvas.screen_geometries[0]
        self.fixed_x = screen_geometry.right() - self.tab_width - self.container_buffer
        initial_y = int(screen_geometry.height() * 0.25)
        self.setGeometry(self.fixed_x, initial_y, self.tab_width, self.tab_height)
        self.setFixedSize(self.container_width, self.container_height)  # Add buffer for shadow

        #Windows Flags
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint | Qt.Tool)
        self.setAttribute(Qt.WA_TranslucentBackground)

    #Draw Tab and Triangle
    def paintEvent(self, event):
            painter = QPainter(self)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.translate(6, 6)  # Offset to center inside drop shadow buffer

            #Drop Shadow
            shadow_pixmap = QPixmap(resource_path("assetts/shadow_tab.png"))
            painter.drawPixmap(-6, 12, 46, 100, shadow_pixmap)

            # Draw blue rounded tab background
            radius = 10
            bg_path = QPainterPath()
            bg_path.moveTo(self.tab_width, 0)
            bg_path.arcTo(0, 0, radius * 2, radius * 2, 90, 90)
            bg_path.lineTo(0, self.tab_height - radius)
            bg_path.arcTo(0, self.tab_height - radius * 2, radius * 2, radius * 2, 180, 90)
            bg_path.lineTo(self.tab_width, self.tab_height)
            bg_path.closeSubpath()

            painter.setBrush(QColor(0, 113, 187))  # App standard blue
            painter.setPen(Qt.NoPen)
            painter.drawPath(bg_path)

            # Triangle dimensions and position
            w, h = 18, 22
            cx = self.tab_width // 2
            cy = self.tab_height // 2

            f1 = QPointF(cx - w / 2, cy - h / 2)
            f2 = QPointF(cx - w / 2, cy + h / 2)
            f3 = QPointF(cx + w / 2, cy)

            b1 = QPointF(cx - w / 2, cy)
            b2 = QPointF(cx + w / 2, cy - h / 2)
            b3 = QPointF(cx + w / 2, cy + h / 2)

            forward_triangle = QPolygonF([f1, f2, f3])
            backward_triangle = QPolygonF([b1, b2, b3])

            triangle_path = QPainterPath()

            if self.menu_visible:
                triangle_path.addPolygon(forward_triangle)
            else:
                triangle_path.addPolygon(backward_triangle)

            #Added during debugging, still needed?
            triangle_path = triangle_path.simplified()

            painter.setBrush(Qt.white)
            painter.drawPath(triangle_path)

    #Mouse Click
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag_start_offset = event.position().toPoint().y()
            self.drag_start_pos = event.globalPosition().toPoint()
            self.dragging = True
            self.dragged = False

    #Mouse Drag
    def mouseMoveEvent(self, event: QMouseEvent):
        if self.dragging:
            current_y = event.globalPosition().toPoint().y()
            new_y = current_y - self.drag_start_offset

            screen = self.canvas.detect_screen_geometry(self.pos())
            clamped_y = max(screen.top(), min(screen.bottom() - self.tab_height - self.clamp_y_offset, new_y))
            self.move(self.fixed_x, clamped_y)

            if not self.dragged and abs(current_y - self.drag_start_pos.y()) > 5:
                self.dragged = True

    #Mouse Release
    def mouseReleaseEvent(self, event: QMouseEvent):
        if self.dragging and not self.dragged:
            self.toggle_menu()
        self.dragging = False
        self.dragged = False

    #Show and hide menu
    def toggle_menu(self):
        if self.menu_visible:
            self.menu.hide()
        else:
            self.menu.show()
        self.menu_visible = not self.menu_visible
        self.update()

    #Switch tab to screen menu is on, set new values based on new screen size
    def move_to_screen(self, geometry=None):
        if geometry is None and hasattr(self.canvas, "detect_screen_geometry"):
            geometry = self.canvas.detect_screen_geometry(self.pos())

        if geometry:
            self.fixed_x = geometry.right() - self.tab_width - self.container_buffer
            clamped_y = max(geometry.top(), min(geometry.bottom() - self.tab_height - self.clamp_y_offset, self.y()))
            self.move(self.fixed_x, clamped_y)
