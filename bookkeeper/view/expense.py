from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QTableWidgetItem


class ExpenseWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QVBoxLayout()
        button_layout = QtWidgets.QHBoxLayout()

        self.expense_table = ExpenseTable()
        self.expense_table.cellClicked.connect(self.cell_clicked)
        self.expense_table.cellChanged.connect(self.cell_changed)

        label = QtWidgets.QLabel("<b>Последние Расходы</b>")
        add_button = QtWidgets.QPushButton("Добавить")
        add_button.clicked.connect(self.arise_add_dialog_form)

        self.delete_button = QtWidgets.QPushButton("Удалить")
        self.delete_button.setEnabled(False)
        self.delete_button.clicked.connect(self.delete_expense_table_row)

        button_layout.addWidget(add_button)
        button_layout.addWidget(self.delete_button)

        layout.addWidget(label)
        layout.addWidget(self.expense_table)
        layout.addLayout(button_layout)

        self.setLayout(layout)

    @QtCore.Slot()
    def cell_clicked(self, row, column) -> None:
        self.delete_button.setEnabled(True)

    @QtCore.Slot()
    def cell_changed(self) -> None:
        self.delete_button.setEnabled(False)

    @QtCore.Slot()
    def delete_expense_table_row(self):
        row_num = self.expense_table.currentRow().numerator
        self.expense_table.delete_row(row_num)
        self.delete_button.setEnabled(False)

    @QtCore.Slot()
    def arise_add_dialog_form(self):
        add_form = AddDialogForm()
        add_form.exec()
        if add_form.is_ok_clicked:
            date: str = add_form.date_input.text()
            amount: int = int(add_form.amount_label_line.text())
            category_id: int = int(add_form.category_box.currentIndex())
            comment: str = add_form.comment_label_line.text()
            self.expense_table.add_new_row(date, amount, category_id, comment)
            add_form.is_ok_clicked = False


class ExpenseTable(QtWidgets.QTableWidget):

    def __init__(self):
        super().__init__()
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Дата", "Сумма", "Категория", "Комментарий"])
        self.stretch_table_elements()

    def stretch_table_elements(self) -> None:
        for h in [self.horizontalHeader()]:
            h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

    def add_new_row(self,
                    date: str,
                    amount: int,
                    category_id: int,
                    comment: str = None) -> None:
        next_row_id = self.rowCount()
        self.insertRow(next_row_id)
        self.setItem(next_row_id, 0, QTableWidgetItem(date))
        self.setItem(next_row_id, 1, QTableWidgetItem(f"{amount}"))
        self.setItem(next_row_id, 2, QTableWidgetItem(f"{category_id}"))
        self.setItem(next_row_id, 3, QTableWidgetItem(comment))

    def delete_row(self, row_id: int) -> None:
        self.removeRow(row_id)


class AddDialogForm(QtWidgets.QDialog):
    is_ok_clicked: bool = False

    def __init__(self):
        super().__init__()

        layout = QtWidgets.QFormLayout()

        date_label = QtWidgets.QLabel("Дата")
        self.date_input_format_choice = QtWidgets.QComboBox()
        self.date_input_format_choice.addItems(["Строка", "Календарь"])
        self.date_input = QtWidgets.QLineEdit()
        date_input_layout = QtWidgets.QHBoxLayout()
        date_input_layout.addWidget(self.date_input)
        date_input_layout.addWidget(self.date_input_format_choice)
        date_input_group = QtWidgets.QGroupBox()
        date_input_group.setLayout(date_input_layout)
        layout.addRow(date_label, date_input_group)

        amount_label = QtWidgets.QLabel("Сумма")
        self.amount_label_line = QtWidgets.QLineEdit()
        layout.addRow(amount_label, self.amount_label_line)

        category_label = QtWidgets.QLabel("Категория")
        self.category_box = QtWidgets.QComboBox()
        layout.addRow(category_label, self.category_box)

        comment_label = QtWidgets.QLabel("Комментарий")
        self.comment_label_line = QtWidgets.QLineEdit()
        layout.addRow(comment_label, self.comment_label_line)

        ok_button = QtWidgets.QDialogButtonBox.StandardButton.Ok
        cancel_button = QtWidgets.QDialogButtonBox.StandardButton.Cancel
        self.buttonBox = QtWidgets.QDialogButtonBox()
        self.buttonBox.addButton(ok_button)
        self.buttonBox.addButton(cancel_button)

        self.buttonBox.accepted.connect(self.ok_button_click)
        self.buttonBox.rejected.connect(self.reject)

        main_layout = QtWidgets.QVBoxLayout()
        main_layout.addLayout(layout)
        main_layout.addWidget(self.buttonBox)
        self.setLayout(main_layout)

    def exec(self):
        super().exec()

    @QtCore.Slot()
    def ok_button_click(self):
        self.is_ok_clicked = True
        self.accept()


class InformationDialog(QtWidgets.QDialog):

    def __init__(self, message: str):
        super().__init__()
        inform_label = QtWidgets.QLabel(message)
        ok_button = QtWidgets.QDialogButtonBox.StandardButton.Ok
        ok_button.accepted.connect(self.accept)

        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(inform_label)
        layout.addWidget(ok_button)
        self.setLayout(layout)