from typing import Callable, Any

from PySide6        import QtWidgets
from PySide6.QtCore import Qt  # pylint: disable=no-name-in-module

from bookkeeper.models.category import Category
from bookkeeper.view.labeled    import LabeledComboBoxInput, LabeledLineInput

class CategoryEditWindow(QtWidgets.QWidget):

    # Class static variables:
    NO_PARENT_CATEGORY: str = "- Без родительской категории -"

    cat_checker : Callable[[str], None]

    def __init__(self,
        cats               : list[Category],
        cat_add_handler    : Callable[[str, str | None], None],
        cat_delete_handler : Callable[[str], None],
        *args              : Any,
        **kwargs           : Any
    ):
        super().__init__(*args, **kwargs)

        self.cat_add_handler    = cat_add_handler
        self.cat_delete_handler = cat_delete_handler

        #===============#
        # Category tree #
        #===============#
        # Label:
        label_cats = QtWidgets.QLabel("<b>Список категорий</b>")
        label_cats.setAlignment(Qt.AlignCenter)  # type: ignore

        # Category tree:
        self.cat_tree = QtWidgets.QTreeWidget()
        self.cat_tree.setHeaderLabel("")
        self.cat_tree.itemDoubleClicked.connect(self.double_clicked)  # type: ignore

        #===================#
        # Category deletion #
        #===================#
        # Label:
        label_del = QtWidgets.QLabel("<b>Удаление категории</b>")
        label_del.setAlignment(Qt.AlignCenter)  # type: ignore

        # Category to be deleted:
        self.cat_del = LabeledComboBoxInput("Категория", [])

        # Delete button:
        self.cat_del_button = QtWidgets.QPushButton('Удалить')
        self.cat_del_button.clicked.connect(self.delete_category)  # type: ignore

        #===================#
        # Category addition #
        #===================#
        # Label:
        label_add = QtWidgets.QLabel("<b>Добавление категории</b>")
        label_add.setAlignment(Qt.AlignCenter)  # type: ignore

        # Added category parent:
        self.cat_add_parent = LabeledComboBoxInput("Родитель", [])

        # Added category name:
        self.cat_add_name = LabeledLineInput("Название", "Новая категория")

        # Add button:
        self.cat_add_button = QtWidgets.QPushButton('Добавить')
        self.cat_add_button.clicked.connect(self.add_category)  # type: ignore

        # Grid layout:
        self.grid = QtWidgets.QGridLayout()

        # AddWidget parameter meaning ---------> Y  X  dY  dX
        self.grid.addWidget(label_cats,          0, 0,  1,  2)
        self.grid.addWidget(self.cat_tree,       1, 0,  1,  2)
        self.grid.addWidget(label_del,           2, 0,  1,  2)
        self.grid.addWidget(self.cat_del,        3, 0,  1,  1)
        self.grid.addWidget(self.cat_del_button, 3, 1,  1,  1)
        self.grid.addWidget(label_add,           4, 0,  1,  2)
        self.grid.addWidget(self.cat_add_parent, 5, 0,  1,  1)
        self.grid.addWidget(self.cat_add_name,   6, 0,  1,  1)
        self.grid.addWidget(self.cat_add_button, 6, 1,  1,  1)

        self.setLayout(self.grid)

        # Set categories when the class is all set up:
        self.set_categories(cats)

    def set_categories(self, cats: list[Category]) -> None:
        self.categories = cats

        self.cat_names = [c.name for c in cats]

        # Recursively traverse categories adding subcategories into the tree:
        cat_hierarchy = self.find_children()

        self.cat_tree.clear()
        self.cat_tree.insertTopLevelItems(0, cat_hierarchy)

        self.cat_del.set_items(self.cat_names)
        self.cat_add_parent.set_items([CategoryEditWindow.NO_PARENT_CATEGORY]
                                      + self.cat_names)

    def delete_category(self) -> None:
        # Category to be deleted:
        del_cat_name = self.cat_del.text()

        self.cat_delete_handler(del_cat_name)
        self.cat_del.clear()

    def set_cat_checker(self, checker : Callable[[str], None]) -> None:
        self.cat_checker = checker

    def add_category(self) -> None:
        cat_add_name    = self.cat_add_name.text()
        parent_cat_name = self.cat_add_parent.text()

        if parent_cat_name == CategoryEditWindow.NO_PARENT_CATEGORY:
            self.cat_add_handler(cat_add_name, None)
        else:
            # Often only the presence of parent is checked:
            self.cat_checker(parent_cat_name)

            self.cat_add_handler(cat_add_name, parent_cat_name)

        self.cat_add_name.clear()
        self.cat_add_parent.clear()


    def find_children(self, parent_pk: int | None = None) -> list[QtWidgets.QTreeWidgetItem]:

        items = []
        children = [c for c in self.categories if c.parent == parent_pk]
        for child in children:
            item = QtWidgets.QTreeWidgetItem([child.name])

            item.addChildren(self.find_children(parent_pk=child.pk))

            items.append(item)

        return items

    def double_clicked(self, item: QtWidgets.QTreeWidgetItem, column: int) -> None:
        clicked_cat_name = item.text(column)

        # Put into input lines the name of double-clicked category:
        self.cat_del.set_text(clicked_cat_name)
        self.cat_add_parent.set_text(clicked_cat_name)