from pytestqt.qt_compat import qt_api

from bookkeeper.view.main_window   import MainWindow
from bookkeeper.view.new_expense   import NewExpense
from bookkeeper.view.budget_table  import LabeledBudgetTable
from bookkeeper.view.expense_table import LabeledExpenseTable

# Define dummy handlers:
modifier       = lambda pk, val1, val2: None
pk_to_name     = lambda pk: ""
deleter        = lambda pks: None
cats_edit_show = lambda: None
adder          = lambda amount, name, comment: None

def test_create_window(qtbot):
    # Create the window:
    budget_table   = LabeledBudgetTable(modifier)
    new_expense    = NewExpense([], cats_edit_show, adder)
    expenses_table = LabeledExpenseTable(pk_to_name, modifier, deleter)

    window         = MainWindow(budget_table, new_expense, expenses_table)
    qtbot.addWidget(window)

    # Verify the constructor:
    assert window.budget_table  == budget_table
    assert window.new_expense   == new_expense
    assert window.expense_table == expenses_table

def test_close_event(qtbot, monkeypatch):
    # Test the close event dialogue:
    for result, msg in zip(
                [True, False],
                [qt_api.QtWidgets.QMessageBox.Yes, qt_api.QtWidgets.QMessageBox.No]
                    ):
        # Create the window:
        budget_table   = LabeledBudgetTable(modifier)
        new_expense    = NewExpense([], cats_edit_show, adder)
        expenses_table = LabeledExpenseTable(pk_to_name, modifier, deleter)

        window = MainWindow(budget_table, new_expense, expenses_table)
        qtbot.addWidget(window)

        # Clock on Yes/No:
        monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
            "question", lambda *args: msg)

        # Check the window successive close result:
        assert window.close() == result