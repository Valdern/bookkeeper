from typing import Callable, Any

from PySide6        import QtWidgets
from PySide6.QtCore import Qt  # pylint: disable=no-name-in-module

from bookkeeper.view.labeled import LabeledComboBoxInput, LabeledLineInput

from bookkeeper.models.category import Category

class NewExpense(QtWidgets.QGroupBox):
    def __init__(
        self,
        categories          : list[Category],
        edit_button_handler : Callable[[], None],
        expense_add_handler : Callable[[str, str, str], None],
        *args               : Any,
        **kwargs            : Any
    ):
        super().__init__(*args, **kwargs)

        # Categories:
        self.categories          = categories
        self.cat_names           = [c.name for c in categories]
        self.edit_button_handler = edit_button_handler
        self.expense_add_handler = expense_add_handler

        # Label:
        self.label = QtWidgets.QLabel("<b>Новая трата</b>")
        self.label.setAlignment(Qt.AlignCenter)  # type: ignore

        # Expense amount input line:
        self.amount_input = LabeledLineInput("Сумма", "0")

        # Expense category selection:
        self.category_input = LabeledComboBoxInput("Категория", self.cat_names)

        # Edit button:
        self.cats_edit_button = QtWidgets.QPushButton('Редактировать')
        self.cats_edit_button.clicked.connect(self.edit_button_handler)  # type: ignore

        # Comment section:
        self.comment_input = LabeledLineInput("Комментарий", "")

        # Expense Submit
        self.submit_button = QtWidgets.QPushButton('Добавить')
        self.submit_button.clicked.connect(self.add_expense)  # type: ignore

        # Grid layout:
        self.grid = QtWidgets.QGridLayout()

        # AddWidget parameter meaning -----------> Y  X  dY  dX
        self.grid.addWidget(self.label,            0, 0,  1,  5)
        self.grid.addWidget(self.amount_input,     1, 0,  1,  4)
        self.grid.addWidget(self.category_input,   2, 0,  1,  4)
        self.grid.addWidget(self.cats_edit_button, 2, 4,  1,  1)
        self.grid.addWidget(self.comment_input,    3, 0,  1,  4)
        self.grid.addWidget(self.submit_button,    4, 0,  1,  5)

        self.setLayout(self.grid)

    def set_categories(self, categories: list[Category]) -> None:
        self.categories = categories
        self.cat_names  = [c.name for c in categories]
        self.category_input.set_items(self.cat_names)

    def add_expense(self) -> None:
        # Call handler:
        self.expense_add_handler(
            self.amount_input.text(),
            self.category_input.text(),
            self.comment_input.text())

        # Clear all input lines:
        self.amount_input.clear()
        self.category_input.clear()
        self.comment_input.clear()