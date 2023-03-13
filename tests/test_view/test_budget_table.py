from pytestqt.qt_compat import qt_api

from bookkeeper.view.budget_table import BudgetTableWidget, LabeledBudgetTable

from bookkeeper.models.budget import Budget

test_data = [["1_1", "1_2", "1_3", 1],
             ["2_1", "2_2", "2_3", 2],]

budget_modify_handler = lambda pk, new_limit, period: None

def test_create_widget(qtbot):
    # Create widget:
    widget = BudgetTableWidget(budget_modify_handler)
    qtbot.addWidget(widget)

    # Test constructor:
    assert widget.budget_modify_handler == budget_modify_handler

def test_add_data(qtbot):
    # Create widget:
    widget = BudgetTableWidget(budget_modify_handler)
    qtbot.addWidget(widget)

    # Fill widget with data:
    widget.add_data(test_data)

    # Check the
    assert widget.data == test_data
    for i, row in enumerate(test_data):
        for j, x in enumerate(row[:-1]):

            # Check the visualized texts:
            assert widget.item(i, j).text() == test_data[i][j]

            if j == 0:
                # Check first row for being selected:
                flags = (qt_api.QtCore.Qt.ItemIsEditable
                        | qt_api.QtCore.Qt.ItemIsEnabled
                        | qt_api.QtCore.Qt.ItemIsSelectable)
                assert widget.item(i, j).flags() == flags
            else:
                # Check first all other rows for the editability:
                assert widget.item(i, j).flags() == qt_api.QtCore.Qt.ItemIsEnabled


def test_cell_changed(qtbot):
    # Define a modify handler to be called on cell edit:
    def budget_modify_handler(pk, new_limit, period):
        budget_modify_handler.was_called = True

        assert pk        == test_data[1][-1]
        assert new_limit == test_data[1][0]
        assert period    == "week"

    budget_modify_handler.was_called = False

    # Create widget and fill it with data:
    widget = BudgetTableWidget(budget_modify_handler)
    qtbot.addWidget(widget)

    widget.add_data(test_data)

    # Check the edit without selection:
    widget.cellChanged.emit(1,0)
    assert budget_modify_handler.was_called == False

    # Check the edit after selection:
    widget.cellDoubleClicked.emit(1,0)
    widget.cellChanged.emit(1,0)
    assert budget_modify_handler.was_called == True

def test_create_group(qtbot):
    # Test the creation of LabeledBudgetTable:
    widget = LabeledBudgetTable(budget_modify_handler)
    qtbot.addWidget(widget)

    # No assertions can be made in here :(

def test_set_budgets(qtbot):
    # Create widget and set it's data:
    widget = LabeledBudgetTable(budget_modify_handler)
    qtbot.addWidget(widget)

    bdgs = [Budget(1000, "day", spent=100),
            Budget(7000, "week"),]
    widget.set_budgets(bdgs)

    # Check the internal data:
    assert widget.budgets == bdgs

    for b, w_data in zip(bdgs, widget.data):
        assert str(b.limitation)                     == w_data[0]
        assert str(b.spent)                          == w_data[1]
        assert str(int(b.limitation) - int(b.spent)) == w_data[2]
        assert str(b.pk)                             == w_data[3]

    assert widget.data[2] == ["- Не установлен -", "", "", ""]