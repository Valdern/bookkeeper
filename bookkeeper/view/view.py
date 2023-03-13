from typing import Callable, Any

from PySide6 import QtWidgets

from bookkeeper.view.main_window          import MainWindow
from bookkeeper.view.budget_table         import LabeledBudgetTable
from bookkeeper.view.new_expense          import NewExpense
from bookkeeper.view.expense_table        import LabeledExpenseTable
from bookkeeper.view.category_edit_window import CategoryEditWindow

from bookkeeper.models.category import Category
from bookkeeper.models.expense  import Expense
from bookkeeper.models.budget   import Budget

# Utility function:
def try_for_widget(
    operation : Callable[..., Any],
    widget    : QtWidgets.QWidget
) -> Callable[..., Any]:
    def inner(*args: Any, **kwargs: Any) -> Any:
        try:
            operation(*args, **kwargs)
        except ValueError as exc:
            QtWidgets.QMessageBox.critical(widget, 'Ошибка', str(exc))
    return inner

class View:

    # Class fields:
    main_window      : MainWindow
    budget_table     : LabeledBudgetTable
    new_expense      : NewExpense
    expense_table    : LabeledExpenseTable
    cats_edit_window : CategoryEditWindow

    # Internal representation:
    categories : list[Category] = []
    expenses   : list[Expense]
    budgets    : list[Budget]

    # All sorts of handlers:
    cat_add_handler    : Callable[[str, str | None], None]
    cat_delete_handler : Callable[[str], None]
    cat_checker        : Callable[[str], None]

    exp_add_handler    : Callable[[str, str, str], None]
    exp_delete_handler : Callable[[set[int]], None]
    exp_modify_handler : Callable[[int, str, str], None]

    bdg_modify_handler : Callable[[int | None, str, str], None]

    def __init__(self) -> None:
        self.app = QtWidgets.QApplication.instance()
        if self.app is None:
            raise RuntimeError("Unable to locate the open QApplication instance")

        self.config_category_edit()
        self.budget_table = LabeledBudgetTable(self.modify_budget)
        self.new_expense  = NewExpense(self.categories,
                                       self.show_category_edit,
                                       self.add_expense)
        self.expense_table = LabeledExpenseTable(self.category_pk_to_name,
                                                 self.modify_expense,
                                                 self.delete_expenses)

        self.config_main_window()

    ###########################
    ## Initial configuration ##
    ###########################

    def config_category_edit(self) -> None:
        self.cats_edit_window = CategoryEditWindow(
            self.categories,
            self.add_category,
            self.delete_category)

        self.cats_edit_window.setWindowTitle("Редактирование категорий")
        self.cats_edit_window.resize(600, 600)

    def config_main_window(self) -> None:
        self.main_window = MainWindow(self.budget_table,
                                      self.new_expense,
                                      self.expense_table)
        self.main_window.resize(1000, 800)

    #######################
    ## Show-like methods ##
    #######################

    def show_main_window(self) -> None:
        self.main_window.show()

    def show_category_edit(self) -> None:
        self.cats_edit_window.show()

    #########################
    ## Category operations ##
    #########################

    # Handler-wrappers:
    def set_category_add_handler(
        self,
        cat_add_handler: Callable[[str, str | None], None]
    ) -> None:
        # Add exception-handling to argument handler:
        self.cat_add_handler = try_for_widget(cat_add_handler, self.main_window)

    def set_category_delete_handler(
        self,
        cat_delete_handler: Callable[[str], None]
    ) -> None:
        # Add exception-handling to argument handler:
        self.cat_delete_handler = try_for_widget(cat_delete_handler, self.main_window)

    def set_category_checker(
        self,
        cat_checker : Callable[[str], None]
    ) -> None:
        # Add exception-handling to argument handler:
        self.cat_checker = try_for_widget(cat_checker, self.main_window)

        self.cats_edit_window.set_cat_checker(self.cat_checker)

    # Direct operations:
    def category_pk_to_name(self, pk: int) -> str:
        name = [c.name for c in self.categories if int(c.pk) == int(pk)]
        if len(name):
            return str(name[0])
        return ""

    def set_categories(self, cats: list[Category]) -> None:
        self.categories = cats
        self.new_expense.set_categories(self.categories)
        self.cats_edit_window.set_categories(self.categories)

    def add_category(self, name: str, parent: str | None) -> None:
        self.cat_add_handler(name, parent)

    def delete_category(self, cat_name: str) -> None:
        self.cat_delete_handler(cat_name)

    ########################
    ## Expense operations ##
    ########################

    # Handler-wrapping:
    def set_expense_add_handler(
        self,
        exp_add_handler : Callable[[str, str, str], None]
    ) -> None:
        self.exp_add_handler = try_for_widget(exp_add_handler, self.main_window)

    def set_expense_delete_handler(
        self,
        exp_delete_handler : Callable[[set[int]], None]
    ) -> None:
        self.exp_delete_handler = try_for_widget(exp_delete_handler, self.main_window)

    def set_expense_modify_handler(
        self,
        exp_modify_handler : Callable[[int, str, str], None]
    ) -> None:
        self.exp_modify_handler = try_for_widget(exp_modify_handler, self.main_window)

    # Direct operations:
    def set_expenses(self, exps: list[Expense]) -> None:
        self.expenses = exps
        self.expense_table.set_expenses(self.expenses)

    def add_expense(self, amount: str, cat_name: str, comment: str = "") -> None:
        self.exp_add_handler(amount, cat_name, comment)

    def delete_expenses(self, exp_pks: set[int]) -> None:
        if len(exp_pks) == 0:
            QtWidgets.QMessageBox.critical(self.main_window,
                            'Ошибка',
                            'Траты для удаления не выбраны.')
        else:
            reply = QtWidgets.QMessageBox.question(
                self.main_window,
                'Удаление трат',
                'Вы уверены, что хотите удалить все выбранные траты?')
            if reply == QtWidgets.QMessageBox.Yes:  # type: ignore
                self.exp_delete_handler(exp_pks)

    def modify_expense(
        self,
        pk      : int,
        attr    : str,
        new_val : Any
    ) -> None:
        self.exp_modify_handler(pk, attr, new_val)

    #######################
    ## Budget operations ##
    #######################

    # Handler-wrapping:
    def set_budget_modify_handler(
        self,
        bdg_modify_handler : Callable[[int | None, str, str], None]
    ) -> None:
        self.bdg_modify_handler = try_for_widget(bdg_modify_handler, self.main_window)

    # Direct operations:
    def set_budgets(
        self,
        budgets : list[Budget]
    ) -> None:
        self.budgets = budgets
        self.budget_table.set_budgets(self.budgets)

    def modify_budget(
        self,
        pk        : int | None,
        new_limit : str,
        period    : str
    ) -> None:
        self.bdg_modify_handler(pk, new_limit, period)

    def not_on_budget_message(self) -> None:
        msg = "Бюджет исчерпан"

        QtWidgets.QMessageBox.warning(self.main_window, 'Нужно больше золота!', msg)