# main.py -- v5.10
#Screen annotation app 
#Based on Unity app I made years ago
#Using method I learned from CodeMonkey on Youtube https://www.youtube.com/watch?v=XozHdfHrb1U
#This app was 100% AI assisted (mostly for layout, but also in translating some C# into python), if that is a problem, then please don't use

import sys, os
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QColor, QPainter, QPen, QPainterPath, QPixmap, QIcon, QCursor
from PySide6.QtCore import Qt, QPoint

from transparent_canvas import TransparentCanvasWindow
from menu_ui import MenuWindow
from dock_tab import DockTab
from background_layer import BackgroundLayer

COLOR_GREEN = "rgb(34, 180, 115)"
COLOR_RED = "rgb(230, 76, 60)"

#For finding resource path on different machines
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller. """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

#Custom Cursor For Drawing - White outline, color center
def create_layered_cursor(outer_path, inner_path, color: QColor, size=42):
    outer = QPixmap(outer_path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
    inner = QPixmap(inner_path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    final = QPixmap(size, size)
    final.fill(Qt.transparent)
    painter = QPainter(final)

    # Tint outer pointer white
    tinted_outer = QPixmap(outer.size())
    tinted_outer.fill(Qt.transparent)
    outer_painter = QPainter(tinted_outer)
    outer_painter.setCompositionMode(QPainter.CompositionMode_Source)
    outer_painter.drawPixmap(0, 0, outer)
    outer_painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
    outer_painter.fillRect(tinted_outer.rect(), QColor("white"))
    outer_painter.end()

    painter.drawPixmap(0, 0, tinted_outer)

    # Tint inner pointer with selected color
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

    #Cursor hotspot - 0,0 = top left
    return QCursor(final, 0, 0)

#Custom Eraser Cursor
def create_eraser_cursor(size=24):
    pixmap = QPixmap(resource_path("assetts/eraser_pointer.png"))
    
    if pixmap.isNull():
        pixmap = QPixmap(size, size)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(QColor(255, 88, 88))  # Match your app's red
        painter.drawEllipse(1, 1, size - 2, size - 2)
        painter.end()
    else:
        pixmap = pixmap.scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    hotspot = QPoint(pixmap.width() // 2, pixmap.height() // 2)
    return QCursor(pixmap, hotspot.x(), hotspot.y())

class Stroke:
    def __init__(self, color: QColor, width: int):
        self.color = color
        self.width = width
        self.segments = []

#Canvas for drawing - including all basic functions
class DrawingCanvas(TransparentCanvasWindow):
    def __init__(self):
        super().__init__()
        self.pen_color = QColor(255, 88, 88)
        self.pen_width = 5
        self.strokes = []
        self.current_stroke = None
        self.current_path = None
        self.erase_mode = False
        self.just_cleared = False
        self.current_screen = 0
        self.is_passthrough = True
        self.points_in_segment = 0

        target_geometry = self.detect_screen_geometry(QPoint(50, 50))
        self.set_screen_geometry(target_geometry)
        self.setWindowFlag(Qt.WindowStaysOnTopHint, True)

        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.transparent)

        self.setFocusPolicy(Qt.NoFocus)
        self.show()

    #Gets screen geomtery used for bg color, multiscreen sizes, and drawing area
    def set_screen_geometry(self, geometry):
        self.setGeometry(geometry)
        self.pixmap = QPixmap(self.size())
        self.pixmap.fill(Qt.transparent)
        self.redraw_all_strokes()
        self.update()

    #Detect screen geometry, used in moving between multiple displays
    def detect_screen_geometry(self, global_pos):
        for g in self.screen_geometries:
            if g.contains(global_pos):
                return g
        return self.virtual_geometry
    
    #Custom, color based cursor while drawing
    def set_custom_cursor(self):
        cursor = create_layered_cursor(resource_path("assetts/arrow_outer.png"), resource_path("assetts/arrow_inner.png"), self.pen_color)
        self.setCursor(cursor)

    #Undo Last
    def undo_last(self):
        if self.just_cleared and self.strokes_backup:
            self.undo_clear()
        elif self.strokes:
            self.strokes.pop()
            self.redraw_all_strokes()
            self.update()
    
    #Undo Clear (only works once)
    def undo_clear(self):
        if self.just_cleared and self.strokes_backup:
            self.strokes = self.strokes_backup.copy()
            self.redraw_all_strokes()
            self.update()
            self.strokes_backup = []
            self.just_cleared = False

    #Erase all drawings
    def clear_canvas(self):
        self.strokes_backup = self.strokes.copy()
        self.strokes.clear()
        self.pixmap.fill(Qt.transparent)
        self.just_cleared = True
        self.update()
    
    #Show/Hide Drawing Canvas
    def set_canvas_visibility(self, visible: bool):
        if visible:
            #Show Drawing Canvas and Disable Passthrough
            self.show()
            self.disable_passthrough()

            #Update Footer Color Variable and Icon
            self.canvas_color = COLOR_RED
            if hasattr(self, "parent_menu") and hasattr(self.parent_menu, "footer") and hasattr(self.parent_menu, "eye_off_icon"):
                self.parent_menu.footer.setIcon(self.parent_menu.eye_off_icon)
        else:
            #Hide Drawing Canvas and Enable Passthrough
            self.hide()
            self.enable_passthrough()
            
            #Update Footer Color Variable and Icon
            self.canvas_color = COLOR_GREEN
            if hasattr(self, "parent_menu") and hasattr(self.parent_menu, "footer") and hasattr(self.parent_menu, "eye_on_icon"):
                self.parent_menu.footer.setIcon(self.parent_menu.eye_on_icon)

        #Update Footer Color to Correct Color
        if hasattr(self, "parent_menu") and hasattr(self.parent_menu, "footer"):
            self.parent_menu.footer.setStyleSheet(f"""
                background-color: {self.canvas_color};  
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            """)

    #Turn Canvas On and Off
    def toggle_canvas_visibility(self):
        self.set_canvas_visibility(not self.isVisible())
        
    #Change drawing/pen width sizes are 5, 10, 15, and 20 pixels
    def set_pen_width(self, width):
            self.pen_width = width
            self.erase_mode = False
            self.disable_passthrough()

    #Choose pen color
    def set_pen_color(self, color):
        self.pen_color = color
        self.erase_mode = False
        self.disable_passthrough()
        self.set_custom_cursor()
         
    #Enable passthrough/click through for OS
    def enable_passthrough(self):
        super().enable_passthrough()
        self.is_passthrough = True
        self.unsetCursor()
        self.set_background_for_monitor(self.current_screen, QColor(0, 0, 0, 1))
        if hasattr(self, 'parent_menu'):
            self.parent_menu.toggle_btn.setIcon(QIcon(resource_path("assetts/comp_draw.png")))  # Will switch to passthrough
        if hasattr(self, "parent_menu") and hasattr(self.parent_menu, "selector_manager"):
            self.parent_menu.selector_manager.hide_selectors()
        if hasattr(self, "background_layer"):
            self.background_layer.set_background_color(self.current_screen, QColor(0, 0, 0, 1))

    #Disable passthrough/click through and go back to drawing or erase mode
    def disable_passthrough(self):
        super().disable_passthrough()
        self.is_passthrough = False
        self.set_custom_cursor()

        if hasattr(self, 'parent_menu'):
            self.parent_menu.activateWindow()  # Helps with receiving focus immediately
            self.parent_menu.raise_() #test
            self.parent_menu.toggle_btn.setIcon(QIcon(resource_path("assetts/comp_control.png"))) 

        if hasattr(self, "parent_menu") and hasattr(self.parent_menu, "selector_manager"):
            self.parent_menu.selector_manager.show_selectors()

    #Button for toggling passthrough/click through
    def toggle_passthrough(self):
        if self.is_passthrough:
            self.disable_passthrough()
            self.set_canvas_visibility(True)
        else:
            self.enable_passthrough()

    #Eraser function
    def enter_erase_mode(self):
        # If in passthrough mode, disable it first
        if self.is_passthrough:
            self.disable_passthrough()
            if hasattr(self, 'parent_menu'):
                self.parent_menu.toggle_btn.setIcon(QIcon(resource_path("assetts/comp_control.png")))

        self.erase_mode = True
        self.setCursor(create_eraser_cursor(size=24))

    #Turn on background: transparent, white, black, or green
    def set_background_for_monitor(self, monitor_index, color):
        if 0 <= monitor_index < len(self.screen_geometries):
            g = self.screen_geometries[monitor_index]
            self.background_color = color
            self.background_rect = g
            self.update()

    def move_to_screen(self, geometry):
        self.set_screen_geometry(geometry)

        # Update current screen index
        for i, g in enumerate(self.screen_geometries):
            if g == geometry:
                self.current_screen = i
                break

        # Update background position
        if hasattr(self, "background_layer"):
            self.background_layer.set_background_color(self.current_screen, self.background_layer.background_color)

        # Move dock tab to same screen
        if hasattr(self.parent_menu, 'dock_tab'):
            self.parent_menu.dock_tab.move_to_screen(geometry)

        #Raise all layers after screen switching
        if hasattr(self.background_layer, 'raise_'):
            self.background_layer.lower()

        if hasattr(self.parent_menu, 'raise_'):
            self.parent_menu.raise_()
            self.parent_menu.activateWindow()

        if hasattr(self.parent_menu, 'dock_tab'):
            self.parent_menu.dock_tab.raise_()


    #Redraw line as pixmap to allow for better performance
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

    #Click Mouse
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and not self.testAttribute(Qt.WA_TransparentForMouseEvents):
            if self.background_color.alpha() > 1:
                self.parent_menu.raise_()
                self.parent_menu.dock_tab.raise_()
            if self.erase_mode:
                self.erase_at(event.position())
            else:
                self.just_cleared = False
                self.current_stroke = Stroke(self.pen_color, self.pen_width)
                self.current_path = QPainterPath()
                self.current_path.moveTo(event.position())
                self.current_stroke.segments.append(self.current_path)
                self.strokes.append(self.current_stroke)
                self.points_in_segment = 0
                self.parent_menu.setWindowOpacity(0.60)
                self.draw_last_segment()

    #Drag Mouse
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
                else:
                    self.draw_last_segment()

    #Mouse Release - used for single dots, ending lines, and connecting lines
    def mouseReleaseEvent(self, event):
        #if no movement, draw a point
        if self.current_stroke and self.current_path and self.points_in_segment == 0:
            dot_path = QPainterPath()
            dot_path.addEllipse(event.position(), self.pen_width / 2, self.pen_width / 2)
            self.current_stroke.segments[-1] = dot_path  # Replace the empty path
            self.draw_last_segment()
        
        #Reset Drawing
        self.current_stroke = None
        self.current_path = None
        self.points_in_segment = 0
        
        #Reset Menu
        self.parent_menu.setWindowOpacity(1.00)  
        self.parent_menu.raise_()
        self.parent_menu.dock_tab.raise_()

    #For performance, lines are drawn in 40 point segments, then pushed into pixmap images, this method connects them together
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

    #Erases based on a buffer surrounding the pointer
    def erase_at(self, pos):

        erase_buffer = 6  # Size of eraser - may need to revisit
        
        #Raise drawings above menu and dim menu
        self.raise_()
        self.parent_menu.setWindowOpacity(0.60) 

        for stroke in reversed(self.strokes):
            for segment in stroke.segments:
                if isinstance(segment, QPainterPath):
                    rect = segment.boundingRect().adjusted(-erase_buffer, -erase_buffer, erase_buffer, erase_buffer)
                    if rect.contains(pos) and segment.contains(pos):
                        self.strokes.remove(stroke)
                        self.redraw_all_strokes()
                        self.update()
                        return



if __name__ == "__main__":

    app = QApplication(sys.argv)

    # Set app icon for taskbar and title bar
    app.setWindowIcon(QIcon(resource_path("assetts/eddraw_icon.ico")))

    #Set up all needed layers background, drawing canvas, menu, and docking tab
    background = BackgroundLayer()
    canvas = DrawingCanvas()
    menu = MenuWindow(canvas)
    tab = DockTab(canvas, menu)

    canvas.parent_menu = menu
    canvas.background_layer = background
    menu.dock_tab = tab
    
    background.show()
    canvas.show()
    menu.show()    
    tab.show()

    sys.exit(app.exec())
