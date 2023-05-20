from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt

from backend import MainWindow_controller

if __name__ == '__main__':
    import sys
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow_controller()

    # Set the window flags to always stay on top
    window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)   
    window.show()
    sys.exit(app.exec_())
