from typing import Protocol, Callable

from bookkeeper.models.category import Category
from bookkeeper.models.expense  import Expense
from bookkeeper.models.budget   import Budget

class AbstractView(Protocol):
    """
    Абстрактный класс интерфейса для приложения Bookkeeper.
    """

    def show_main_window(self) -> None:
        pass

    def set_categories(self, cats : list[Category]) -> None:
        pass

    def set_expenses(self, cats : list[Expense]) -> None:
        pass

    def set_budgets(self, cats : list[Budget]) -> None:
        pass

    def set_category_add_handler(
        self,
        cat_add_handler: Callable[[str, str | None], None]
    ) -> None:
        pass

    def set_category_delete_handler(self, cat_delete_handler: Callable[[str], None]) -> None:
        pass

    def set_category_checker(self, cat_checker: Callable[[str], None]) -> None:
        pass

    def set_budget_modify_handler(self, handler: Callable[['int | None', str, str],
                                                        None]) -> None:
        pass

    def set_expense_add_handler(self, exp_add_handler: Callable[[str, str, str], None]) -> None:
        pass

    def set_expense_delete_handler(self, exp_delete_handler: Callable[[set[int]], None]) -> None:
        pass

    def set_expense_modify_handler(
        self,
        exp_modify_handler: Callable[[int, str, str], None]
    ) -> None:
        pass

    def not_on_budget_message(self) -> None:
        pass
