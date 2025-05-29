# main.py -- v2.11

import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QPixmap, QIcon
from PySide6.QtCore import Qt, QRect, QPoint
from transparent_canvas import TransparentCanvasWindow
from menu_ui import MenuWindow

from PySide6.QtGui import QPixmap, QCursor, QPainter, QColor
from PySide6.QtCore import Qt

def create_layered_cursor(outer_path, inner_path, color: QColor, size=42):
    outer = QPixmap(outer_path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    inner = QPixmap(inner_path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    final = QPixmap(size, size)
    final.fill(Qt.transparent)
    painter = QPainter(final)

    # Tint outer image white
    tinted_outer = QPixmap(outer.size())
    tinted_outer.fill(Qt.transparent)
    outer_painter = QPainter(tinted_outer)
    outer_painter.setCompositionMode(QPainter.CompositionMode_Source)
    outer_painter.drawPixmap(0, 0, outer)
    outer_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    outer_painter.fillRect(tinted_outer.rect(), QColor("white"))
    outer_painter.end()

    painter.drawPixmap(0, 0, tinted_outer)

    # Tint inner image with selected color
    tinted_inner = QPixmap(inner.size())
    tinted_inner.fill(Qt.transparent)
    inner_painter = QPainter(tinted_inner)
    inner_painter.setCompositionMode(QPainter.CompositionMode_Source)
    inner_painter.drawPixmap(0, 0, inner)
    inner_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    inner_painter.fillRect(tinted_inner.rect(), color)
    inner_painter.end()

    painter.drawPixmap(0, 0, tinted_inner)
    painter.end()

    return QCursor(final)



class Stroke:
    def __init__(self, color: QColor, width: int):
        self.color = color
        self.width = width
        self.segments = []

class DrawingCanvas(TransparentCanvasWindow):
    def __init__(self):
        super().__init__()
        self.pen_color = QColor(255, 88, 88)
        self.pen_width = 5
        self.strokes = []
        self.current_stroke = None
        self.current_path = None
        self.erase_mode = False
        self.current_screen = 0
        self.is_passthrough = True
        self.points_in_segment = 0

        target_geometry = self.detect_screen_geometry(QPoint(50, 50))
        self.set_screen_geometry(target_geometry)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.transparent)

        self.show()

    def set_screen_geometry(self, geometry):
        self.setGeometry(geometry)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.transparent)
        self.redraw_all_strokes()
        self.update()

    def detect_screen_geometry(self, global_pos):
        for g in self.screen_geometries:
            if g.contains(global_pos):
                return g
        return self.virtual_geometry
    
    def set_custom_cursor(self):
        cursor = create_layered_cursor("assetts/arrow_outer.png", "assetts/arrow_inner.png", self.pen_color)
        self.setCursor(cursor)
    
    def set_pen_width(self, width):
            self.pen_width = width

    def undo_last(self):
        if self.strokes:
            self.strokes.pop()
            self.redraw_all_strokes()
            self.update()

    def clear_canvas(self):
        self.strokes.clear()
        self.pixmap.fill(Qt.transparent)
        self.update()

    def set_pen_color(self, color):
        self.pen_color = color
        self.erase_mode = False
        self.disable_passthrough()
        self.set_custom_cursor()
            

    def enable_passthrough(self):
        super().enable_passthrough()
        self.is_passthrough = True
        self.unsetCursor()
        print("Passthrough ENABLED")
        self.raise_()
        if hasattr(self, 'parent_menu'):
            self.parent_menu.toggle_btn.setIcon(QIcon("assetts/comp_draw.png"))  # Will switch to passthrough

    def disable_passthrough(self):
        super().disable_passthrough()
        self.is_passthrough = False
        self.set_custom_cursor()
        self.raise_()
        if hasattr(self, 'parent_menu'):
            self.lower()  # Put canvas behind the menu
            self.parent_menu.raise_()
            self.parent_menu.activateWindow()  # Helps with receiving focus immediately
            self.parent_menu.toggle_btn.setIcon(QIcon("assetts/comp_control.png"))  # Will switch to drawing

    def toggle_passthrough(self):
        if self.is_passthrough:
            self.disable_passthrough()
            if hasattr(self, 'parent_menu'):
                self.parent_menu.toggle_btn.setIcon(QIcon("assetts/comp_control.png"))
        else:
            self.enable_passthrough()
            if hasattr(self, 'parent_menu'):
                self.parent_menu.toggle_btn.setIcon(QIcon("assetts/comp_draw.png"))


    def enter_erase_mode(self):
        self.erase_mode = not self.erase_mode
        if not self.erase_mode:
            self.enable_passthrough()

    def set_background_for_monitor(self, monitor_index, color):
        if 0 <= monitor_index < len(self.screen_geometries):
            g = self.screen_geometries[monitor_index]
            self.background_color = color
            self.background_rect = g
            self.update()

    def move_to_screen(self, geometry):
        self.set_screen_geometry(geometry)

    def redraw_all_strokes(self):
        self.pixmap.fill(Qt.transparent)
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        for stroke in self.strokes:
            for segment in stroke.segments:
                if isinstance(segment, tuple):
                    pen = QPen(stroke.color, stroke.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    painter.setPen(pen)
                    painter.drawLine(segment[0], segment[1])
                else:
                    pen = QPen(stroke.color, stroke.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
                    painter.setPen(pen)
                    painter.drawPath(segment)
        painter.end()

    def paintEvent(self, event):
        painter = self.get_painter(event)
        painter.drawPixmap(0, 0, self.pixmap)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.testAttribute(Qt.WA_TransparentForMouseEvents):
            if self.erase_mode:
                self.erase_at(event.position())
            else:
                self.current_stroke = Stroke(self.pen_color, self.pen_width)
                self.current_path = QPainterPath()
                self.current_path.moveTo(event.position())
                self.current_stroke.segments.append(self.current_path)
                self.strokes.append(self.current_stroke)
                self.points_in_segment = 0
                self.draw_last_segment()
                self.parent_menu.raise_()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton:
            if self.erase_mode:
                self.erase_at(event.position())
            elif self.current_path:
                self.current_path.lineTo(event.position())
                self.points_in_segment += 1
                if self.points_in_segment >= 40:
                    last_point = self.current_path.currentPosition()
                    self.draw_last_segment()
                    self.current_path = QPainterPath()
                    self.current_path.moveTo(last_point)
                    self.current_path.lineTo(event.position())
                    self.current_stroke.segments.append(self.current_path)
                    self.points_in_segment = 1
                self.draw_last_segment()

    def mouseReleaseEvent(self, event):
        #if no movement, draw a point
        if self.current_stroke and self.current_path and self.points_in_segment == 0:
            dot_path = QPainterPath()
            dot_path.addEllipse(event.position(), self.pen_width / 2, self.pen_width / 2)
            self.current_stroke.segments[-1] = dot_path  # Replace the empty path
            self.draw_last_segment()
        
        self.current_stroke = None
        self.current_path = None
        self.points_in_segment = 0
        self.parent_menu.raise_()

    def draw_last_segment(self):
        if not self.current_stroke or not self.current_stroke.segments:
            return
        last = self.current_stroke.segments[-1]
        painter = QPainter(self.pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(self.current_stroke.color, self.current_stroke.width, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin)
        painter.setPen(pen)
        if isinstance(last, tuple):
            painter.drawLine(last[0], last[1])
        else:
            painter.drawPath(last)
        painter.end()
        self.update()

    def erase_at(self, pos):
        erase_buffer = 4  # ← Change this value to test sensitivity (in pixels)

        for stroke in reversed(self.strokes):
            for segment in stroke.segments:
                if isinstance(segment, QPainterPath):
                    rect = segment.boundingRect().adjusted(-erase_buffer, -erase_buffer, erase_buffer, erase_buffer)
                    if rect.contains(pos):
                        self.strokes.remove(stroke)
                        self.redraw_all_strokes()
                        self.update()
                        return


if __name__ == "__main__":
    app = QApplication(sys.argv)
    canvas = DrawingCanvas()
    menu = MenuWindow(canvas)
    canvas.parent_menu = menu
    canvas.show()
    menu.show()
    sys.exit(app.exec())
