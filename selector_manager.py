# Selector Manager 5.10
# Utility to show and hide color selectors

from PySide6.QtGui import QColor
from PySide6.QtWidgets import QLabel 

class SelectorManager:
    def __init__(self, canvas, menu_window):
        self.canvas = canvas
        self.menu = menu_window
        self.current_size_name = "size_5"


    # Set Pen Colors & Update Selector
    def select_color_button(self, r, g, b):
        #leave hiding mode if true
        self.canvas.set_canvas_visibility(True)

        color = QColor(r, g, b)

        self.canvas.set_pen_color(color)
        self.canvas.disable_passthrough()
        self.canvas.erase_mode = False

        # Hide all selector rings
        for ring in self.menu.selector_rings.values():
            ring.hide()

        # Show the selected color ring
        selected_ring = self.menu.selector_rings.get((r, g, b))
        if selected_ring:
            selected_ring.show()
    #end Selector Color Button

    #Set Size & Update Selector
    def select_size_button(self, name, width):
        #leave hiding mode if true
        self.canvas.set_canvas_visibility(True)

        self.canvas.set_pen_width(width)
        self.canvas.erase_mode = False

        for btn_name, btn in self.menu.size_buttons_by_name.items():
            indicator = btn.findChild(QLabel)
            if indicator:
                color = "rgb(230, 76, 60)" if btn_name == name else "rgb(128, 128, 128)"
                indicator.setStyleSheet(f"""
                    background-color: {color};
                    border: none;
                    border-radius: {indicator.width() // 2}px;
                """)

        self.menu.current_size_name = name  # Track currently selected size

        # Show size selector ring for selected button
        for ring_name, ring in self.menu.size_selector_rings.items():
            if ring_name == name:
                ring.show()
            else:
                ring.hide()
        self.canvas.disable_passthrough()    
    #End Set Size & Update Selector
    
    #Show Selectors
    def show_selectors(self):
        # Show color selector
        current_color = self.canvas.pen_color
        color_key = (current_color.red(), current_color.green(), current_color.blue())

        for ring in self.menu.selector_rings.values():
            ring.hide()

        color_ring = self.menu.selector_rings.get(color_key)
        if color_ring:
            color_ring.show()

        # Show size selector
        current_size = self.menu.current_size_name
        for ring in self.menu.size_selector_rings.values():
            ring.hide()

        size_ring = self.menu.size_selector_rings.get(current_size)
        if size_ring:
            size_ring.show()
    #End Show Selectors

    #Hide Selectors
    def hide_selectors(self):
        for ring in self.menu.size_selector_rings.values():
            ring.hide()
        for ring in self.menu.selector_rings.values():
            ring.hide()
    #End Hide
