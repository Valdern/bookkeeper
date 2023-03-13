from pytestqt.qt_compat import qt_api

from bookkeeper.models.category  import Category
from bookkeeper.view.new_expense import NewExpense

# Dummy handlers:
edit_button_handler = lambda: None
expense_add_handler = lambda amount, cat_name, comment: None

def test_create_group(qtbot):
    # Create widget:
    widget = NewExpense([],
                        edit_button_handler,
                        expense_add_handler,)

    qtbot.addWidget(widget)

    # Check the constructor result:
    assert widget.edit_button_handler == edit_button_handler
    assert widget.expense_add_handler == expense_add_handler

def test_set_categories(qtbot):
    # Create widget and fill it with data:
    widget = NewExpense([],
                             edit_button_handler,
                             expense_add_handler,)
    qtbot.addWidget(widget)

    cats = [Category("cat1"), Category("cat2"),]
    widget.set_categories(cats)

    # Check the data:
    assert widget.categories == cats
    assert widget.cat_names  == [c.name for c in cats]

def test_add_expense(qtbot):
    # Create the handler to be called on expense addition:
    def expense_add_handler(amount, cat_name, comment):
        expense_add_handler.was_called = True

        assert amount   == "100"
        assert cat_name == "cat1"
        assert comment  == "test"

    expense_add_handler.was_called = False

    # Create widget:
    cats   = [Category("cat1"), Category("cat2"),]
    widget = NewExpense(cats,
                             edit_button_handler,
                             expense_add_handler,)
    qtbot.addWidget(widget)

    # Set the values to line inputs:
    widget.amount_input.set_text  ("100")
    widget.category_input.set_text("cat1")
    widget.comment_input.set_text ("test")

    # Perform the mouseclick:
    qtbot.mouseClick(
                widget.submit_button,
                qt_api.QtCore.Qt.MouseButton.LeftButton
            )

    # Expect the handler to be called:
    assert expense_add_handler.was_called == True