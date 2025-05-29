# EdDraw
EdDraw lets you write/draw/annotate across multiple screens.  While it was designed for educators, it can be used by presenters, streamers, and a wide variety of profesionals in many situations.  It is fast, responsive, and has many features traditional annotation software lacks - like switching backgrounds, collapsing the menu, more colors and sizes.  This tool was designed by me, an educator, to fill the gap in what I needed in my classroom.  Originally built in C#, this was rebuilt in python (with a little help from AI - noted when used).  It is optimized to work on a wide range of display sizes and pixel density.  This is currently a windows only app.


Features:
- Switch between multiple screens and annotate (annotation has been tested across 3 vertical monitors, not horizontal or other configuration)
- Toggle between transparent, white, black, and green backgrounds
- Enable or disable passthrough mode to allow desktop interaction
- Erase individual strokes or clear the entire canvas
- Undo the last stroke
- Collapse/hide menu
- Oversized menu designed to work well on touchscreen tv's for teacher classrooms

(While proofread, the following was generated using AI)
Installation:
You can run EdDraw from source using Python and PySide6, or build an installer using PyInstaller (exe coming soon).

To run from source:
1. Install requirements:
   pip install PySide6

2. Run the app:
   python main.py

To build with PyInstaller:
1. Install PyInstaller:
   pip install pyinstaller

2. Build the executable:
   pyinstaller --noconsole EdDraw.spec

This will produce a distributable installer or executable in the dist/ folder.

An official Windows .exe build will be available on GitHub shortly.

License:
This project is licensed under the GNU General Public License v3 (GPLv3).

You may use, modify, and distribute this software under the terms of that license. If you distribute compiled binaries, you must also provide access to the source code.

For commercial licensing or support inquiries, please contact the author.

Contributions:
Pull requests and issue reports are welcome. If you encounter a bug or have a feature request, please use the issue tracker on the GitHub repository.
