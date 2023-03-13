from typing import Any

from PySide6        import QtWidgets
from PySide6.QtCore import QEvent  # pylint: disable=no-name-in-module

from bookkeeper.view.budget_table  import LabeledBudgetTable
from bookkeeper.view.expense_table import LabeledExpenseTable
from bookkeeper.view.new_expense   import NewExpense

# pylint: disable=too-few-public-methods
class MainWindow(QtWidgets.QWidget):
    def __init__(
        self,
        budget_table  : LabeledBudgetTable,
        new_expense   : NewExpense,
        expense_table : LabeledExpenseTable,
        *args         : Any,
        **kwargs      : Any
    ):
        super().__init__(*args, **kwargs)

        # Window options:
        self.setWindowTitle("Bookkeeper")

        # Window internal widgets:
        self.budget_table  = budget_table
        self.new_expense   = new_expense
        self.expense_table = expense_table

        # Vertical layout:
        self.vbox = QtWidgets.QVBoxLayout()

        self.vbox.addWidget(self.budget_table,  stretch=3)
        self.vbox.addWidget(self.new_expense,   stretch=1)
        self.vbox.addWidget(self.expense_table, stretch=6)

        self.setLayout(self.vbox)

    def closeEvent(self, event: QEvent) -> None:  # pylint: disable=invalid-name
        # Spawn a messagebox:
        reply = QtWidgets.QMessageBox.question(self,
            "Закрыть приложение",
            "Вы уверены?\nВсе несохраненные данные будут потеряны.")

        # Parse Yes/No reply:
        if reply == QtWidgets.QMessageBox.Yes:  # type: ignore
            event.accept()
            app = QtWidgets.QApplication.instance()
            app.closeAllWindows()  # type: ignore
        else:
            event.ignore()