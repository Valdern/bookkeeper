from PySide6 import QtWidgets


class BudgetWidget(QtWidgets.QWidget):

    def __init__(self):
        super().__init__()

        widget_layout = QtWidgets.QVBoxLayout()

        label = QtWidgets.QLabel("<b>Бюджет</b>")
        reset_button = QtWidgets.QPushButton("Обнулить счётчик")
        budget_table = BudgetTable()

        widget_layout.addWidget(label)
        widget_layout.addWidget(budget_table)
        widget_layout.addWidget(reset_button)

        self.setLayout(widget_layout)


class BudgetTable(QtWidgets.QTableWidget):
    def __init__(self):
        super().__init__()
        self.setColumnCount(3)
        self.setRowCount(3)
        self.setHorizontalHeaderLabels(["Бюджет", "Потрачено", "Осталось"])
        self.setVerticalHeaderLabels(["День", "Неделя", "Месяц"])
        self.stretch_table_elements()

    def stretch_table_elements(self) -> None:
        for h in [self.horizontalHeader(), self.verticalHeader()]:
            h.setSectionResizeMode(QtWidgets.QHeaderView.Stretch)