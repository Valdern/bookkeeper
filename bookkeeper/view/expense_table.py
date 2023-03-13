from typing import Callable, Any

from PySide6        import QtWidgets
from PySide6.QtCore import Signal, Qt  # pylint: disable=no-name-in-module

from bookkeeper.models.expense import Expense

class ExpenseTableWidget(QtWidgets.QTableWidget):
    """
    Виджет для расхода.
    """

    cellDoubleClicked : Signal # Double-click handler with attachable pre-handler
    cellChanged       : Signal # Cell changed handler with attachable pre-handler

    data : list[list[str]]

    def __init__(
        self,
        expense_modify_handler : Callable[[int, str, Any], None],
        *args                  : Any,
        **kwargs               : Any
    ):
        super().__init__(*args, **kwargs)

        self.expense_modify_handler = expense_modify_handler

        self.col_to_attr = {0:"expense_date", 1:"amount", 2:"category", 3:"comment"}

        # Table configuration:
        self.setColumnCount(4)
        self.setRowCount(20)

        headers = "Дата Сумма Категория Комментарий".split()
        self.setHorizontalHeaderLabels(headers)

        # Configure table header:
        header = self.horizontalHeader()
        header.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents) # type: ignore
        header.setSectionResizeMode(
            1, QtWidgets.QHeaderView.ResizeToContents) # type: ignore
        header.setSectionResizeMode(
            2, QtWidgets.QHeaderView.ResizeToContents) # type: ignore
        header.setSectionResizeMode(
            3, QtWidgets.QHeaderView.Stretch)          # type: ignore

        # Disable vertical header:
        self.verticalHeader().hide()

        # Enter edit mode on double-click:
        self.setEditTriggers(
            QtWidgets.QAbstractItemView.DoubleClicked) # type: ignore

        # Handle the change event of all cells collectively:
        #   On cell double-click bind onChange handler.
        #   Reset it on "onChanged" event.
        self.cellDoubleClicked.connect(self.double_click)

    def double_click(self, row: int, column: int) -> None:
        # Parameters unused:
        del row, column

        # Bind the cell_changed() as cellChanged handler
        self.cellChanged.connect(self.cell_changed)

    def cell_changed(self, row: int, column: int) -> None:
        # Unbind cell_changed():
        self.cellChanged.disconnect(self.cell_changed)

        # Generate a database request on edit:
        pk      = int(self.data[row][-1])
        new_val = self.item(row, column).text()
        attr    = self.col_to_attr[column]

        self.expense_modify_handler(pk, attr, new_val)

    def add_data(self, data: list[list[str]]) -> None:
        self.data = data
        for row_i, row in enumerate(data):
            for item_j, item in enumerate(row[:-1]):
                self.setItem(
                    row_i, item_j,
                    QtWidgets.QTableWidgetItem(item.capitalize())
                )

class LabeledExpenseTable(QtWidgets.QGroupBox):
    """
    Виджет для расхода с подписью.
    """

    expenses : list[Expense]
    data     : list[list[str]]

    def __init__(
        self,
        category_pk_to_name    : Callable[[int], str],
        expense_modify_handler : Callable[[int, str, Any], None],
        expanse_delete_handler : Callable[[set[int]], None],
        *args                  : Any,
        **kwargs               : Any
    ):
        super().__init__(*args, **kwargs)

        self.category_pk_to_name    = category_pk_to_name
        self.expanse_delete_handler = expanse_delete_handler

        # Label:
        self.label = QtWidgets.QLabel("<b>Последние траты</b>")
        self.label.setAlignment(Qt.AlignCenter) # type: ignore

        # Expense table:
        self.table = ExpenseTableWidget(expense_modify_handler)

        # Delete button:
        self.del_button = QtWidgets.QPushButton('Удалить выбранные траты')
        self.del_button.clicked.connect(self.delete_selected_expenses) # type: ignore

        # Vertical layout:
        self.vbox = QtWidgets.QVBoxLayout()

        self.vbox.addWidget(self.label)
        self.vbox.addWidget(self.table)

        self.setLayout(self.vbox)

    def set_expenses(self, exps: list[Expense]) -> None:
        self.expenses = exps

        # Update rendered data:
        self.data = self.exps_to_data(self.expenses)

        # Update the subsequent table:
        self.table.clearContents()
        self.table.add_data(self.data)

    def exps_to_data(self, exps: list[Expense]) -> list[list[str]]:
        data = []
        for exp in exps:
            # Visualize category fields:
            item = ["","","","",str(exp.pk)]
            if exp.expense_date:
                item[0] = str(exp.expense_date)
            if exp.amount:
                item[1] = str(exp.amount)
            if exp.category:
                item[2] = str(
                    self.category_pk_to_name(exp.category))
            if exp.comment:
                item[3] = str(exp.comment)

            # Insert category visualization:
            data.append(item)

        return data

    def delete_selected_expenses(self) -> None:
        # List of primary keys to delete:
        pks_to_del = []

        # Iterate over ranges shosen for removal:
        chosen_ranges = self.table.selectedRanges()

        for ch_range in chosen_ranges:
            start = ch_range.topRow()
            end   = min(ch_range.bottomRow(), len(self.data))

            pks_to_del += [int(i[-1]) for i in self.data[start:end+1]]

        # Remove from the database all utems with selected pk
        self.expanse_delete_handler(set(pks_to_del))