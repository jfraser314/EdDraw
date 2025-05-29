
# menu_ui.py -- v2.22

from PySide6.QtCore import Qt, QPoint, QSize, QTimer
from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QPushButton, QLabel, QHBoxLayout, QGridLayout, QApplication, QGraphicsDropShadowEffect
)
from functools import partial

class MenuWindow(QWidget):

    def create_tinted_icon(self, path, color, size=36):
        base = QPixmap(path).scaled(size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        tinted = QPixmap(base.size())
        tinted.fill(Qt.transparent)

        painter = QPainter(tinted)
        painter.setCompositionMode(QPainter.CompositionMode_Source)
        painter.drawPixmap(0, 0, base)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), color)
        painter.end()

        return QIcon(tinted)

    def __init__(self, canvas):
        super().__init__()
        self.canvas = canvas
        self.drag_position = None
        self.last_monitor_index = -1
        self.last_background_color = None

        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint)
        self.setFixedSize(160, 540)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFocusPolicy(Qt.NoFocus)

        self.color_buttons = []
        self.selected_color_button = None
        self.size_buttons = []
        self.selected_size_button = None

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(0)

        header = QWidget()
        header.setStyleSheet("background-color: #007acc; border-top-left-radius: 12px; border-top-right-radius: 12px;")
        header.setFixedHeight(34)
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(8, 0, 8, 0)

        header_label = QLabel("EdDraw")
        header_label.setStyleSheet("color: white; font-weight: bold; font-size: 14px;")

        self.close_btn = QPushButton(self)
        self.close_btn.setIcon(QIcon("assetts/btn_x.png"))
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
        self.close_btn.raise_()

        header_layout.addWidget(header_label)
        header_layout.addStretch()
        layout.addWidget(header)

        inner_widget = QWidget()
        inner_widget.setStyleSheet("background-color: white; border-bottom-left-radius: 12px; border-bottom-right-radius: 12px;")
        inner_layout = QVBoxLayout(inner_widget)
        inner_layout.setContentsMargins(8, 8, 8, 8)
        inner_layout.setSpacing(4)

        shadow = QGraphicsDropShadowEffect(inner_widget)
        shadow.setBlurRadius(20)
        shadow.setOffset(4, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        inner_widget.setGraphicsEffect(shadow)

        self.toggle_btn = QPushButton()
        self.toggle_btn.setIcon(QIcon("assetts/comp_draw.png"))
        self.toggle_btn.setIconSize(QSize(36, 36))
        self.toggle_btn.setFixedSize(44, 44)
        self.toggle_btn.setStyleSheet("border: none; background-color: transparent;")
        self.toggle_btn.clicked.connect(self.canvas.toggle_passthrough)

        tools = [
            self.toggle_btn,
            QPushButton(), QPushButton(), QPushButton()
        ]

        actions = [
            self.canvas.toggle_passthrough,
            self.canvas.undo_last,
            self.canvas.enter_erase_mode,
            self.canvas.clear_canvas
        ]

        icons = [
            None,
            "assetts/undo.png",
            "assetts/eraser.png",
            "assetts/trash_can.png"
        ]

        for i in range(1, 4):
            tools[i].setIcon(QIcon(icons[i]))
            tools[i].setIconSize(QSize(36, 36))
            tools[i].setFixedSize(44, 44)
            tools[i].setStyleSheet("border: none; background-color: transparent;")
            tools[i].clicked.connect(actions[i])

        tool_grid = QGridLayout()
        for i, btn in enumerate(tools):
            tool_grid.addWidget(btn, i // 2, i % 2)
        inner_layout.addLayout(tool_grid)

        self.color_ring_indicator = QLabel(self)
        self.color_ring_indicator.setFixedSize(44, 44)
        self.color_ring_indicator.setStyleSheet("background-color: transparent;")
        self.color_ring_indicator.hide()

        #Color Circles Begin
        color_rgb = [
            (255, 144, 38), (151, 51, 151), (69, 194, 235), (255, 153, 204),
            (255, 88, 88), (76, 191, 102), (0, 0, 0), (178, 127, 83)
        ]

        color_grid = QGridLayout()
        for i, (r, g, b) in enumerate(color_rgb):
            btn = QPushButton()
            btn.setFixedSize(44, 44)
            btn.setIcon(self.create_tinted_icon("assetts/circle.png", QColor(r, g, b)))
            btn.setIconSize(QSize(32, 32))
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("border: none; background-color: transparent;")


            btn.clicked.connect(partial(self.select_color_button, btn, QColor(r, g, b)))
            color_grid.addWidget(btn, i // 2, i % 2)
            self.color_buttons.append(btn)

        inner_layout.addLayout(color_grid)
        #Color Circles End

        self.size_ring_indicator = QLabel(self)
        self.size_ring_indicator.setFixedSize(44, 44)
        self.size_ring_indicator.setStyleSheet("""
            background-color: transparent;
            border: 3px solid rgb(77, 77, 77);
            border-radius: 22px;
        """)
        self.size_ring_indicator.hide()

        size_grid = QGridLayout()
        sizes = [(15, 5), (20, 10), (25, 15), (30, 20)]
        for i, (diameter, width) in enumerate(sizes):
            btn = QPushButton()
            btn.setFixedSize(44, 44)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setStyleSheet("border: none; background-color: transparent;")

            indicator = QLabel(btn)
            indicator.setFixedSize(diameter, diameter)
            indicator.move((44 - diameter) // 2, (44 - diameter) // 2)
            indicator.setStyleSheet("background-color: rgb(128, 128, 128); border: none; border-radius: {}px;".format(diameter // 2))

            btn.clicked.connect(partial(self.select_size_button, btn, width))
            size_grid.addWidget(btn, i // 2, i % 2)
            self.size_buttons.append(btn)
        inner_layout.addLayout(size_grid)

        #Set up bg's
        bg_grid = QGridLayout()
        backgrounds = [
            ("assetts/trans_board.png", QColor(0, 0, 0, 1)),
            ("assetts/white_board.png", QColor("white")),
            ("assetts/black_board.png", QColor("black")),
            ("assetts/green_board.png", QColor("darkgreen"))
        ]
        for i, (path, color) in enumerate(backgrounds):
            btn = QPushButton()
            btn.setIcon(QIcon(path))
            btn.setIconSize(QSize(38, 38))
            btn.setStyleSheet("border: none; background-color: transparent;")
            btn.setCursor(Qt.PointingHandCursor)
            btn.clicked.connect(partial(self.set_background_color, color))
            bg_grid.addWidget(btn, i // 2, i % 2)
        inner_layout.addLayout(bg_grid)

        inner_widget.setLayout(inner_layout)
        layout.addWidget(inner_widget)
        self.setLayout(layout)
        self.move(50, 50)
        self.canvas.enable_passthrough()
        self.show()
        #end set up bg's

        QTimer.singleShot(0, self.initialize_color_ring)
        QTimer.singleShot(0, lambda: self.select_size_button(self.size_buttons[0], 5))
        self.close_btn.raise_()

    def initialize_color_ring(self):
        if self.color_buttons:
            btn = self.color_buttons[0]
            self.select_color_button(btn, QColor(255, 144, 38))

    def select_color_button(self, wrapper, color):
        print("select_color_button")
        self.canvas.set_pen_color(color)
        self.canvas.disable_passthrough()

        self.color_ring_indicator.setStyleSheet(
            f"""
            background-color: transparent;
            border: 3px solid rgb({color.red()},{color.green()},{color.blue()});
            border-radius: 22px;
            """
        )
        global_pos = wrapper.mapToGlobal(QPoint(0, 0))
        local_pos = self.mapFromGlobal(global_pos)
        self.color_ring_indicator.move(local_pos)
        self.color_ring_indicator.raise_()
        self.color_ring_indicator.show()

    def select_size_button(self, button, width):
        print("Select Size")
        self.canvas.set_pen_width(width)

        for btn in self.size_buttons:
            indicator = btn.findChild(QLabel)
            if indicator:
                indicator.setStyleSheet("""
                    background-color: rgb(128, 128, 128);
                    border: none;
                    border-radius: %dpx;
                """ % (indicator.width() // 2))

        indicator = button.findChild(QLabel)
        if indicator:
            indicator.setStyleSheet("""
                background-color: rgb(230, 76, 60);
                border: none;
                border-radius: %dpx;
            """ % (indicator.width() // 2))

        global_pos = button.mapToGlobal(QPoint(0, 0))
        local_pos = self.mapFromGlobal(global_pos)
        self.size_ring_indicator.move(local_pos)
        self.size_ring_indicator.raise_()
        self.size_ring_indicator.show()

        self.selected_size_button = button

    def set_background_color(self, color):
        print("Select Background")
        self.canvas.background_color = color
        self.canvas.set_background_for_monitor(self.canvas.current_screen, color)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        if event.buttons() & Qt.LeftButton and self.drag_position:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            self.canvas.move_to_screen(self.canvas.detect_screen_geometry(self.pos()))
