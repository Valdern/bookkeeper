import sys
from PySide6 import QtWidgets

from bookkeeper.view.main_window import MainWindow

if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    window = MainWindow()
    window.resize(800, 600)
    window.show()

    sys.exit(app.exec())