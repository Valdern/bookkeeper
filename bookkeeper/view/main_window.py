from PySide6 import QtWidgets, QtGui
from PySide6.QtWidgets import QMainWindow
from budget import BudgetWidget
from expense import ExpenseWidget


class MainWindow(QMainWindow):

    BOOKKEEPER_APP_LOGO_PATH: str = "../../../../GitHub_Коля/bookkeeper/resources/logo.png"

    def __init__(self):
        super().__init__()

        self.setWindowTitle("Bookkeeper")
        window_icon = QtGui.QIcon()
        window_icon.addFile(self.BOOKKEEPER_APP_LOGO_PATH)
        self.setWindowIcon(window_icon)

        self.expense_widget = ExpenseWidget()
        self.budget_widget = BudgetWidget()

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(self.expense_widget)
        layout.addWidget(self.budget_widget)

        box = QtWidgets.QGroupBox()
        box.setLayout(layout)
        self.setCentralWidget(box)