from pytestqt.qt_compat import qt_api

from bookkeeper.view.expense_table import ExpenseTableWidget, \
                                          LabeledExpenseTable

from bookkeeper.models.expense import Expense

test_data = [["1_1", "1_2", "1_3", "1_4", 1],
             ["2_1", "2_2", "2_3", "2_4", 2],]

# Define dummy handlers:
expense_modify_handler = lambda pk, attr, new_val: None
category_pk_to_name    = lambda pk: "1_3"
exp_delete_handler     = lambda exp_pks: None

def test_create_widget(qtbot):
    # Create widget:
    widget = ExpenseTableWidget(expense_modify_handler)
    qtbot.addWidget(widget)

    # Check it's constructor:
    assert widget.expense_modify_handler == expense_modify_handler

def test_add_data(qtbot):
    # Create widget with data:
    widget = ExpenseTableWidget(expense_modify_handler)
    qtbot.addWidget(widget)
    widget.add_data(test_data)

    # Check it's intrnal representation:
    assert widget.data == test_data

    # Check visualization:
    for i, row in enumerate(test_data):
        for j, x in enumerate(row[:-1]):
            assert widget.item(i, j).text() == test_data[i][j]

def test_cell_changed(qtbot):
    # Define a modify handler to be called on cell edit:
    def expense_modify_handler(pk, attr, new_val):
        expense_modify_handler.was_called = True

        assert pk      == test_data[0][4]
        assert new_val == test_data[0][0]

    expense_modify_handler.was_called = False

    # Create widget and fill it with data:
    widget = ExpenseTableWidget(expense_modify_handler)
    qtbot.addWidget(widget)
    widget.add_data(test_data)

    # Check the edit without selection:
    widget.cellChanged.emit(0,0)
    assert expense_modify_handler.was_called == False

    # Check the edit after selection:
    widget.cellDoubleClicked.emit(0,0)
    widget.cellChanged.emit(0,0)
    assert expense_modify_handler.was_called == True

def test_create_group(qtbot):
    # Create labeled widget:
    widget = LabeledExpenseTable(category_pk_to_name,
                                 expense_modify_handler,
                                 exp_delete_handler)
    qtbot.addWidget(widget)

    # Check it's field:
    assert widget.category_pk_to_name    == category_pk_to_name
    assert widget.expanse_delete_handler == exp_delete_handler

def test_set_expenses(qtbot):
    # Add widget and fill it with data:
    widget = LabeledExpenseTable(category_pk_to_name,
                                 expense_modify_handler,
                                 exp_delete_handler)
    qtbot.addWidget(widget)

    exps = [Expense(100, 1, expense_date="12.12.2012 15:30",
                            comment="test"),
            Expense(200, 2, expense_date="12.12.2012 15:30")]
    widget.set_expenses(exps)

    # Assert that internal data is the same as input:
    assert widget.expenses == exps

    for exp, w_data in zip(exps, widget.data):
        assert str(exp.expense_date)             == w_data[0]
        assert str(exp.amount)                   == w_data[1]
        assert category_pk_to_name(exp.category) == w_data[2]
        assert str(exp.comment)                  == w_data[3]
        assert str(exp.pk)                       == w_data[4]

def test_delete_expenses(qtbot):
    # Define a delete handler to be called on cell edit:
    def exp_delete_handler(exp_pks):
        exp_delete_handler.was_called = True

        assert exp_pks == set([2,3])

    exp_delete_handler.was_called = False

    # Create widget and fill it with data:
    widget = LabeledExpenseTable(category_pk_to_name,
                                expense_modify_handler,
                                exp_delete_handler)
    qtbot.addWidget(widget)

    exps = [Expense(100, 1, pk=1), Expense(200, 2, pk=2),
            Expense(300, 3, pk=3), Expense(400, 4, pk=4),]
    widget.set_expenses(exps)

    # Select the initial selection:
    widget.table.setRangeSelected(
                qt_api.QtWidgets.QTableWidgetSelectionRange(1,1,2,2), True)
    widget.table.setRangeSelected(
                qt_api.QtWidgets.QTableWidgetSelectionRange(1,3,3,4), True)

    # Perform the mouse-click:
    qtbot.mouseClick(
            widget.del_button,
            qt_api.QtCore.Qt.MouseButton.LeftButton
        )

    # Expect delete handler to be called:
    assert exp_delete_handler.was_called == True