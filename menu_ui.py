# menu_ui.py -- v5.10
#Spacing and visual layout initially generated from AI using picture of previously build app

import sys, os
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGridLayout, QApplication, QGraphicsDropShadowEffect)
from functools import partial
from selector_manager import SelectorManager
from hold_button_utils import make_button_holdable

COLOR_GREEN = "rgb(34, 180, 115)"
COLOR_RED = "rgb(230, 76, 60)"

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

def apply_hover_effect(button, radius=6, hover_color="rgba(0,0,0,0.08)"):
    button.setStyleSheet(f"""
        QPushButton {{
            background-color: transparent;
            border: none;
            border-radius: {radius}px;
        }}
        QPushButton:hover {{
            background-color: {hover_color};
        }}
    """)   


#Hover/Grow Effect For All Icon Buttons
class HoverGrowButton(QPushButton):
    def __init__(self, icon_path):
        super().__init__()
        self.setIcon(QIcon(icon_path))
        self.setIconSize(QSize(36, 36))
        self.setFixedSize(44, 44)
        self.setStyleSheet("border: none;")
        self.normal_size = QSize(36, 36)
        self.hover_size = QSize(44, 44)

    #Make Icon full size - 44px while hovering
    def enterEvent(self, event):
        self.setIconSize(self.hover_size)

    #Make Icon normal size - 36 pixels while not selected/hovered
    def leaveEvent(self, event):
        self.setIconSize(self.normal_size)

#Hover Grow For Footer
class FooterButton(QPushButton):
    def __init__(self, icon_on_path, icon_off_path, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.icon_on = QIcon(icon_on_path)
        self.icon_off = QIcon(icon_off_path)
        self.setIcon(self.icon_off)
        self.setIconSize(QSize(32, 32)) 
        self.setFixedHeight(36)
        self.setCursor(Qt.ArrowCursor)
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: {COLOR_RED};
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }}
        """)

    #Hover Grow Icon
    def enterEvent(self, event):
        self.setIconSize(QSize(40, 40))  # Grow on hover
        super().enterEvent(event)

    #Leave Hover Shrink Icon
    def leaveEvent(self, event):
        self.setIconSize(QSize(32, 32))  
        super().leaveEvent(event)

    
class MenuWindow(QWidget):
    #Create & Setup tools buttons - draw/passththrough, undo, erase, delete-all
    def create_tool_buttons(self, layout):
        # Create buttons with hover-grow effect
        self.toggle_btn = HoverGrowButton(resource_path("assetts/comp_draw.png"))
        undo_btn = HoverGrowButton(resource_path("assetts/undo.png"))
        erase_btn = HoverGrowButton(resource_path("assetts/eraser.png"))
        trash_btn = HoverGrowButton(resource_path("assetts/trash_can.png"))
        self.eye_on_icon = QIcon(resource_path("assetts/eye_on.png"))
        self.eye_off_icon = QIcon(resource_path("assetts/eye_off.png"))

        # Assign actions
        self.toggle_btn.clicked.connect(self.canvas.toggle_passthrough)
        undo_btn.clicked.connect(self.canvas.undo_last)
        erase_btn.clicked.connect(self.canvas.enter_erase_mode)
        make_button_holdable(trash_btn, 1000, self.canvas.clear_canvas)

        # Add to layout
        tools = [self.toggle_btn, undo_btn, erase_btn, trash_btn]

        tool_grid = QGridLayout()
        for i, btn in enumerate(tools):
            tool_grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(tool_grid)

    #End Create Tool Buttons

    #Create & Setup Color Buttons
    def create_color_buttons(self, layout):
        color_grid = QGridLayout()

        self.color_definitions = [
            (255, 144, 38),   # Orange
            (151, 51, 151),   # Purple
            (69, 194, 235),   # Cyan
            (255, 153, 204),  # Pink
            (255, 88, 88),    # Red
            (76, 191, 102),   # Green
            (0, 0, 0),        # Black
            (1, 105, 103)     # Teal
        ]

        self.color_buttons = []
        self.selector_rings = {}

        button_size = 44

        for i, (r, g, b) in enumerate(self.color_definitions):
            # Create Color Button
            btn = QPushButton()
            btn.setFixedSize(button_size, button_size)
            btn.setCursor(Qt.ArrowCursor)
            apply_hover_effect(btn, radius=22)

            # Create a pixmap circle for button
            pixmap = QPixmap(32, 32)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setBrush(QColor(r, g, b))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, 32, 32)
            painter.end()

            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(32, 32))

            # Add to button list
            self.color_buttons.append(btn)
            color_grid.addWidget(btn, i // 2, i % 2)

            # Create Color Selector Ring 
            ring = QLabel(btn)  # << attach directly to the button
            ring.setFixedSize(button_size, button_size)
            ring.setStyleSheet(f"""
                background-color: transparent;
                border: 3px solid rgb({r}, {g}, {b});
                border-radius: {button_size // 2}px;
            """)
            ring.move(0, 0)  # (0,0) relative to button, perfect overlay
            ring.hide()

            self.selector_rings[(r, g, b)] = ring

            # Connect click to color_manager
            btn.clicked.connect(partial(self.selector_manager.select_color_button, r, g, b))
        
        layout.addLayout(color_grid)
    # end create_color_buttons

    #Create Size Buttons & Selectors
    def create_size_buttons(self, layout):
        size_grid = QGridLayout()
        self.size_buttons = []
        self.size_buttons_by_name = {}
        self.size_selector_rings = {}

        #Make sizes dictionary, name them after size -- change later?
        sizes = [
            ("size_5", 15, 5),
            ("size_10", 20, 10),
            ("size_15", 25, 15),
            ("size_20", 30, 20)
        ]

        for i, (name, diameter, width) in enumerate(sizes):
            btn = QPushButton()
            btn.setFixedSize(44, 44)
            btn.setCursor(Qt.ArrowCursor)
            apply_hover_effect(btn, radius=22)
            btn.setObjectName(name)

            # Inner visual indicator
            indicator = QLabel(btn)
            indicator.setFixedSize(diameter, diameter)
            indicator.move((44 - diameter) // 2, (44 - diameter) // 2)
            indicator.setStyleSheet(f"""
                background-color: rgb(128, 128, 128);
                border: none;
                border-radius: {diameter // 2}px;
            """)

            # Selector ring attached to button
            ring = QLabel(btn)  # attach to button
            ring.setFixedSize(44, 44)
            ring.move(0, 0)  # perfect overlay
            ring.setStyleSheet("""
                background-color: transparent;
                border: 3px solid rgb(77, 77, 77);
                border-radius: 22px;
            """)
            ring.hide()
            self.size_selector_rings[name] = ring

            # Connection and storage
            btn.clicked.connect(partial(self.selector_manager.select_size_button, name, width))
            size_grid.addWidget(btn, i // 2, i % 2)
            self.size_buttons.append(btn)
            self.size_buttons_by_name[name] = btn

        # Select default size
        self.selector_manager.select_size_button("size_5", 5)
        layout.addLayout(size_grid)
    #end Size Selector

    #Background Selectors
    def create_background_selector(self, layout):
        bg_grid = QGridLayout()
        backgrounds = [
            (resource_path("assetts/trans_board.png"), QColor(0, 0, 0, 1)),  # transparent
            (resource_path("assetts/white_board.png"), QColor("white")),
            (resource_path("assetts/black_board.png"), QColor("black")),
            (resource_path("assetts/green_board.png"), QColor(81, 144, 106))  # green
        ]

        for i, (path, color) in enumerate(backgrounds):
            btn = HoverGrowButton(path)
            btn.setIconSize(QSize(36, 36))  # hover logic will bump this to 40
            btn.setCursor(Qt.ArrowCursor)
            btn.setStyleSheet("border: none; background-color: transparent;")
            btn.clicked.connect(partial(self.set_background_color, color))
            bg_grid.addWidget(btn, i // 2, i % 2)

        layout.addLayout(bg_grid)


    def __init__(self, canvas):
        super().__init__()
        
        #Menu and Button layout originally done using AI from image
        #then HEAVILY edited
        self.canvas = canvas
        self.selector_manager = SelectorManager(canvas, self)

        self.drag_position = None
        self.last_monitor_index = -1
        self.last_background_color = None

        #Over sized container, allows for drop shadow
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFixedSize(160, 596)  # length is 560 + 36 for footer
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        self.color_buttons = []
        self.selected_color_button = None
        self.size_buttons = []
        self.selected_size_button = None

        layout = QVBoxLayout(self)
        margin = 20
        layout.setContentsMargins(margin, margin, margin, margin)
        layout.setSpacing(0)

        #Blue App Header
        header = QWidget()
        header.setStyleSheet("background-color: #007acc; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        header.setFixedHeight(34)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 0, 8, 0)

        #EdDraw Text
        header_label = QLabel("EdDraw")
        header_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addWidget(header)

        #Exit Button
        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(QIcon(resource_path("assetts/btn_x.png")))
        self.close_btn.setIconSize(QSize(18, 18))
        self.close_btn.setFixedSize(28, 28)
        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: rgb(255, 88, 88);
                border: none;
                border-radius: 14px;
            }
            QPushButton:hover {
                background-color: rgb(220, 50, 50);
            }
        """)
        self.close_btn.clicked.connect(QApplication.quit)
        self.close_btn.move(self.width() - self.close_btn.width() - 10, 10)

        #Drop Shadow
        shadow_bg = QLabel(self)
        shadow_bg.setPixmap(QPixmap(resource_path("assetts/shadow_menu.png")))
        shadow_bg.setScaledContents(True)
        shadow_bg.setGeometry(0, 0, 160, 596)  # Match full menu size
        shadow_bg.lower()  # Make sure it's behind all other widgets

        #White Background
        inner_widget = QWidget()
        inner_widget.setStyleSheet("background-color: white;")
        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setContentsMargins(8, 8, 8, 8)
        inner_layout.setSpacing(4)

        #Footer Button
        self.footer = FooterButton(
            resource_path("assetts/eye_on.png"),
            resource_path("assetts/eye_off.png")
        )
        self.footer.clicked.connect(self.canvas.toggle_canvas_visibility)

        """"
        #Drop Shadow
        shadow = QGraphicsDropShadowEffect(inner_widget)
        shadow.setBlurRadius(20)
        shadow.setOffset(4, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        inner_widget.setGraphicsEffect(shadow)
        """

        #Setup Tools
        self.create_tool_buttons(inner_layout)

        #Make Color Circles
        self.create_color_buttons(inner_layout)

        #Make Size Selector Butttons
        self.create_size_buttons(inner_layout)

        #Set up bg's
        self.create_background_selector(inner_layout)

        #Hide Selectors
        self.selector_manager.hide_selectors()

        #Line up and starting values
        inner_widget.setLayout(inner_layout)
        inner_widget.setFixedHeight(inner_widget.sizeHint().height() + 0 )
        
        self.footer.setIcon(self.eye_off_icon)
        self.footer.setIconSize(QSize(32, 32))

        layout.addWidget(inner_widget)
        layout.addWidget(self.footer)

        self.footer.show()

        self.setLayout(layout)
        self.move(50, 50)
        self.canvas.enable_passthrough()
        self.show()
        
        #Raise exit button
        self.close_btn.raise_()
    #end init

    def set_background_color(self, color):

        self.canvas.set_canvas_visibility(True)
        self.canvas.background_layer.set_background_color(self.canvas.current_screen, color)

        if color.alpha() > 1:
            self.canvas.disable_passthrough()
            self.toggle_btn.setIcon(QIcon(resource_path("assetts/comp_control.png")))
            self.selector_manager.show_selectors()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            new_geometry = self.canvas.detect_screen_geometry(self.pos())
            self.canvas.move_to_screen(new_geometry)  # updates current_screen index



