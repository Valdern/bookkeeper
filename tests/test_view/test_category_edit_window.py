from pytestqt.qt_compat import qt_api

from bookkeeper.view.category_edit_window import CategoryEditWindow

from bookkeeper.models.category import Category

# Dummy handlers:
cat_add_handler    = lambda name, parent : None
cat_delete_handler = lambda cat_name     : None
cat_checker        = lambda parent_name  : None

def test_create_window(qtbot):
    # Create widget:
    widget = CategoryEditWindow([], cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)

    # Verify the constructor:
    assert widget.cat_add_handler    == cat_add_handler
    assert widget.cat_delete_handler == cat_delete_handler

def test_set_categories(qtbot):
    # Create widget and fill it with data:
    widget = CategoryEditWindow([], cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)

    cats = [Category("cat1",   pk=1),
            Category("cat2",   pk=2),
            Category("cat11",  pk=11,  parent=1),
            Category("cat12",  pk=12,  parent=1),
            Category("cat121", pk=121, parent=12)]

    widget.set_categories(cats)

    # Verify the categories:
    assert widget.categories == cats
    assert widget.cat_names  == [c.name for c in cats]

    # Verify category tree structure:
    assert widget.cat_tree.topLevelItem(0).text(0) == "cat1"
    assert widget.cat_tree.topLevelItem(1).text(0) == "cat2"
    assert widget.cat_tree.topLevelItem(0).child(0).text(0) == "cat11"
    assert widget.cat_tree.topLevelItem(0).child(1).text(0) == "cat12"
    assert widget.cat_tree.topLevelItem(0).child(1).child(0).text(0) == "cat121"

def test_set_cat_checker(qtbot):
    # Create widget with checker handler set:
    widget = CategoryEditWindow([], cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)

    widget.set_cat_checker(cat_checker)

    # Verify the checker:
    assert widget.cat_checker == cat_checker

def test_double_clicked(qtbot):
    # Create widget:
    widget = CategoryEditWindow([Category("cat1", pk=1)],
                                  cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)

    # Double click at the top-most category:
    item = widget.cat_tree.topLevelItem(0)
    widget.cat_tree.itemDoubleClicked.emit(item, 0)
    clicked_cat_name = item.text(0)

    # Verify the category that was clicked is selected
    # for deletion or as a parent for new-born category:
    assert widget.cat_del.text()        == clicked_cat_name
    assert widget.cat_add_parent.text() == clicked_cat_name

def test_delete_category(qtbot):
    # Define category deletion handler:
    def cat_delete_handler(cat_name):
        cat_delete_handler.was_called = True

        assert cat_name == "cat1"

    cat_delete_handler.was_called = False

    # Create widget:
    widget = CategoryEditWindow([Category("cat1", pk=1)],
                                   cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)

    # Set the category to be deleted:
    widget.cat_del.set_text("cat1")
    qtbot.mouseClick(
        widget.cat_del_button,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # Check the handler to be called:
    assert cat_delete_handler.was_called == True

def test_add_category(qtbot):
    # Define category addition handler:
    def cat_add_handler(name, parent):
        cat_add_handler.was_called = True

        assert name   == "cat12"
        assert parent == "cat1"

    cat_add_handler.was_called = False

    # Create widget:
    widget = CategoryEditWindow([Category("cat1", pk=1)],
                                   cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)
    widget.set_cat_checker(cat_checker)

    # Create category by double-clicking the button:
    widget.cat_add_name.set_text("cat12")
    widget.cat_add_parent.set_text("cat1")
    qtbot.mouseClick(
        widget.cat_add_button,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # Expect the handler to be called:
    assert cat_add_handler.was_called == True

def test_add_category_no_parent(qtbot):
    # Define category addition handler:
    def cat_add_handler(name, parent):
        cat_add_handler.was_called = True

        assert name   == "cat1"
        assert parent == None

    cat_add_handler.was_called = False

    # Create widget:
    widget = CategoryEditWindow([], cat_add_handler, cat_delete_handler)
    qtbot.addWidget(widget)

    widget.set_cat_checker(cat_checker)

    # Create category by double-clicking the button:
    widget.cat_add_name.set_text("cat1")
    widget.cat_add_parent.set_text("- Без родительской категории -")
    qtbot.mouseClick(
        widget.cat_add_button,
        qt_api.QtCore.Qt.MouseButton.LeftButton
    )

    # Check that category name was cleared:
    add_name_text = widget.cat_add_name.text()
    widget.cat_add_name.clear()
    assert add_name_text == widget.cat_add_name.text()

    # Check that category parent was cleared:
    add_parent_text = widget.cat_add_parent.text()
    widget.cat_add_parent.clear()
    assert add_parent_text == widget.cat_add_parent.text()

    # Expect the handler to be called:
    assert cat_add_handler.was_called == True