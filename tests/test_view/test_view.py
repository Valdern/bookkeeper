from pytestqt.qt_compat import qt_api

from bookkeeper.view.view       import View, try_for_widget
from bookkeeper.models.category import Category
from bookkeeper.models.expense  import Expense
from bookkeeper.models.budget   import Budget

def test_create():
    # Test view creation:
    view = View()

def test_set_categories():
    view = View()

    # Check the categories for updatability:
    for cats in [[],
                 [Category("cat1", pk=1),
                  Category("cat2", pk=2)]]:
        view.set_categories(cats)

        assert view.categories == cats

def test_category_pk_to_name():
    # Create view with categories set:
    view = View()

    cats = [Category("cat1", pk=1),
            Category("cat2", pk=2),]
    view.set_categories(cats)

    # Test search results:
    assert view.category_pk_to_name(1) == "cat1"
    assert view.category_pk_to_name(3) == ""

def test_set_expenses():
    # Create view with expenses set:
    view = View()

    exps = [Expense(100, 1, comment="test"),
            Expense(200, 2, expense_date="12.12.2012 15:30")]
    view.set_expenses(exps)

    # Test search results:
    assert view.expenses               == exps
    assert view.expense_table.expenses == exps

def test_set_budgets():
    # Create view with budget set:
    view = View()

    bdgs = [Budget(1000, "day", spent=100),
            Budget(7000, "week"),]
    view.set_budgets(bdgs)

    # Test search results:
    assert view.budgets              == bdgs
    assert view.budget_table.budgets == bdgs

def test_handle_error(qtbot, monkeypatch):
    # Define handlers:
    def handler_err():
        raise ValueError('test')

    def handler_noerr():
        pass

    def monkey_func(*args):
        monkey_func.was_called = True

        return qt_api.QtWidgets.QMessageBox.Ok

    monkey_func.was_called = False

    # Create widget:
    widget = qt_api.QtWidgets.QWidget()
    qtbot.addWidget(widget)

    # Set the handler to be called on exception:
    monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
        "critical", monkey_func)

    # Test no-error no-handler scenario:
    try_for_widget(handler_noerr, widget)()
    assert monkey_func.was_called == False

    # Test error+handler scenario:
    try_for_widget(handler_err, widget)()
    assert monkey_func.was_called == True

def test_set_handler(monkeypatch):
    # Create view:
    view = View()

    def handler(*args):
        handler.call_count += 1

    handler.call_count = 0

    # Test set_category_add_handler:
    view.set_category_add_handler(handler)
    view.add_category('name', 'parent')
    assert handler.call_count == 1

    # Test set_category_delete_handler:
    view.set_category_delete_handler(handler)
    view.delete_category('cat_name')
    assert handler.call_count == 2

    # Test set_cat_checker:
    view.set_category_checker(handler)
    view.cat_checker('cat_name')
    assert handler.call_count == 3

    # Test set_budget_modify_handler:
    view.set_budget_modify_handler(handler)
    view.modify_budget(1, 'new_limit', 'period')
    assert handler.call_count == 4

    # Test set_expense_add_handler:
    view.set_expense_add_handler(handler)
    view.add_expense('amount', 'cat_name')
    assert handler.call_count == 5

    # Press the Yes button for the message box:
    monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
                "question", lambda *args: qt_api.QtWidgets.QMessageBox.Yes)

    # Test set_expense_add_handler:
    view.set_expense_delete_handler(handler)
    view.delete_expenses([1])
    assert handler.call_count == 6

    # Test set_expense_modify_handler:
    view.set_expense_modify_handler(handler)
    view.modify_expense(1, 'attr', 'new_val')
    assert handler.call_count == 7

def test_delete_expenses(monkeypatch):
    # Define expense delete handler:
    def deleter(*args):
        deleter.was_called = True

    deleter.was_called = False

    # Create view:
    view = View()
    view.set_expense_delete_handler(deleter)

    #============================#
    # Define "Ok" m-box answerer:
    def monkey_func_ok(*args):
        monkey_func_ok.was_called = True

        return qt_api.QtWidgets.QMessageBox.Ok

    monkey_func_ok.call_count = False

    # Set handler called on m-box answer:
    monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
            "critical", monkey_func_ok)

    # Delete expenses incorrectly:
    view.delete_expenses([])

    # Expect nothing to be deleted:
    assert monkey_func_ok.was_called == True
    assert deleter.was_called        == False

    #============================#
    # Define "No" m-box answerer:
    def monkey_func_no(*args):
        monkey_func_no.was_called = True

        return qt_api.QtWidgets.QMessageBox.No

    monkey_func_no.was_called = False

    # Set handler called on m-box answer:
    monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
                "question", monkey_func_no)

    # Delete expenses correctly:
    view.delete_expenses([1])

    # Expect nothing to be deleted:
    assert monkey_func_no.was_called == True
    assert deleter.was_called == False

    #============================#
    # Define "No" m-box answerer:
    def monkey_func_yes(*args):
        monkey_func_yes.was_called = True

        return qt_api.QtWidgets.QMessageBox.Yes

    monkey_func_yes.was_called = False

    # Set handler called on m-box answer:
    monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
                "question", monkey_func_yes)

    # Delete expenses correctly:
    view.delete_expenses([1])

    # Expect delete_handler to be called:
    assert monkey_func_yes.was_called == True
    assert deleter.was_called == True

def test_not_on_budget_message(monkeypatch):
    # Create handler to be called on messagebox:
    def monkey_func(*args):
        monkey_func.was_called = True

        return qt_api.QtWidgets.QMessageBox.Ok

    monkey_func.was_called = False

    # Create view:
    view = View()

    # Set handler called on m-box answer:
    monkeypatch.setattr(qt_api.QtWidgets.QMessageBox,
            "warning", monkey_func)

    # Eject message:
    view.not_on_budget_message()

    # Expect message to appear:
    assert monkey_func.was_called == True