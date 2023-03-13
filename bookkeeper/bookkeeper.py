from datetime import datetime

from typing import Callable, Any

from bookkeeper.view.abstract_view import AbstractView

from bookkeeper.repository.abstract_repository import AbstractRepository

from bookkeeper.models.category import Category
from bookkeeper.models.expense  import Expense
from bookkeeper.models.budget   import Budget

class Bookkeeper:

    # Class fields:
    view          : AbstractView
    category_repo : AbstractRepository[Category]
    budget_repo   : AbstractRepository[Budget]
    expense_repo  : AbstractRepository[Expense]

    def __init__(self,
                 view               : AbstractView,
                 repository_factory : Callable[[Any], AbstractRepository[Any]]):

        # Abstract out of the view details:
        self.view = view

        #########################
        ## Category repository ##
        #########################

        self.category_repo = repository_factory(Category)

        self.categories = self.category_repo.get_all()

        # Configure view:
        self.view.set_categories(self.categories)

        self.view.set_category_add_handler   (self.add_category)
        self.view.set_category_delete_handler(self.delete_category)
        self.view.set_category_checker       (self.cat_checker)

        #######################
        ## Budget repository ##
        #######################

        self.budget_repo = repository_factory(Budget)

        # Fill the budget values:
        self.budgets = self.budget_repo.get_all()

        # Configure view handlers:
        self.view.set_budget_modify_handler(self.modify_budget)

        ########################
        ## Expense repository ##
        ########################

        self.expense_repo = repository_factory(Expense)

        self.update_expenses()
        self.view.set_expense_add_handler   (self.add_expense)
        self.view.set_expense_delete_handler(self.delete_expenses)
        self.view.set_expense_modify_handler(self.modify_expense)

    def start_app(self) -> None:
        self.view.show_main_window()

    #########################
    ## Category operations ##
    #########################

    def cat_checker(self, cat_name: str) -> None:
        if cat_name not in [c.name for c in self.categories]:
            raise ValueError(f"Категории \"{cat_name}\" не существует")

    def add_category(self, name: str, parent: str | None = None) -> None:

        # Category existent:
        if name in [c.name for c in self.categories]:
            raise ValueError(f"Категория \"{name}\" уже существует")

        # No parent category:
        if parent is not None:
            if parent not in [c.name for c in self.categories]:
                raise ValueError(f"Категории \"{parent}\" не существует")
            parent_pk = self.category_repo.get_all(where={'name':parent})[0].pk
        else:
            parent_pk = None

        # Create category:
        cat = Category(name, parent_pk)

        # Update:
        # - Internal state
        # - Repository
        # - View
        self.categories.append(cat)
        self.category_repo.add(cat)
        self.view.set_categories(self.categories)

    def delete_category(self, cat_name: str) -> None:
        # No categories to delete:
        cats = self.category_repo.get_all(where={"name":cat_name})

        if len(cats) == 0:
            raise ValueError(f"Категории \"{cat_name}\" не существует")

        # Repo operation:
        cat = cats[0]
        self.category_repo.delete(cat.pk)

        # Update parent category for all children ("your papa is gone :("):
        for child in self.category_repo.get_all(where={'parent':cat.pk}):
            child.parent = cat.parent
            self.category_repo.update(child)

        # Update internal state:
        self.categories = self.category_repo.get_all()

        # Update view:
        self.view.set_categories(self.categories)

        # Update expense repo:
        for exp in self.expense_repo.get_all(where={'category':cat.pk}):
            self.expense_repo.delete(exp.pk)

        # Uodate expenses:
        self.update_expenses()

    ########################
    ## Expense operations ##
    ########################

    def update_expenses(self) -> None:

        self.expenses = self.expense_repo.get_all()
        self.view.set_expenses(self.expenses)

        # Update budgets as they have expanses inside:
        self.update_budgets()

    def add_expense(self, amount: str, cat_name: str, comment: str="") -> None:

        # Parse user input:
        try:
            amount_int = int(amount)
        except ValueError as exc:
            raise ValueError("Введите сумму целым числом.") from exc

        # Handle negative or zero amounts:
        if amount_int <= 0:
            raise ValueError("Введите положительную величину покупки.")

        # Get expense category (to link to it's id):
        cats = self.category_repo.get_all(where={"name":cat_name.lower()})

        if len(cats) == 0:
            raise ValueError(f"Категории \"{cat_name}\" не существует")

        # Create the expense:
        cat = cats[0]
        new_exp = Expense(amount_int, cat.pk, comment=comment)

        self.expense_repo.add(new_exp)
        self.update_expenses()

        # Check budget limits:
        for budget in self.budgets:
            if budget.spent > budget.limitation:
                self.view.not_on_budget_message()
                return


    def delete_expenses(self, exp_pks: set[int]) -> None:

        for pk in exp_pks:
            self.expense_repo.delete(pk)
        self.update_expenses()

    def modify_expense(self, pk: int, attr: str, new_val: str) -> None:

        # Get expense to be modified:
        exp = self.expense_repo.get(pk)
        if exp is None:
            raise ValueError(f"Расхода с pk=\"{pk}\" не существует")

        # Modify category:
        if attr == "category":
            # Parse string:
            cat_name = new_val.lower()

            if cat_name not in [c.name for c in self.categories]:
                self.view.set_expenses(self.expenses)
                raise ValueError(f"Категории \"{cat_name}\" не существует")

            # Get category pk:
            cat_pk = self.category_repo.get_all(where={'name':cat_name})[0].pk

            # Update expense pk:
            setattr(exp, attr, cat_pk)

        # Modify amount:
        if attr == "amount":
            # Parse integer:
            try:
                amount = int(new_val)
            except ValueError as exc:
                raise ValueError("Чем это Вы расплачивались?\n"
                                    + "Введите сумму целым числом.") from exc

            # Check for negative amount:
            if amount <= 0:
                self.view.set_expenses(self.expenses)
                raise ValueError("Удачная покупка! Записывать не буду.")

            setattr(exp, attr, amount)

        # Modify expense_date:
        if attr == "expense_date":
            # Parse datetime:
            try:
                time = datetime.fromisoformat(new_val).isoformat(
                            sep='\t', timespec='minutes')
            except ValueError as exc:
                self.view.set_expenses(self.expenses)
                raise ValueError("Неправильный формат даты.") from exc

            setattr(exp, attr, time)

        # Update the expense:
        self.expense_repo.update(exp)

        # Update view and expenses in the budget:
        self.update_expenses()

    #######################
    ## Budget operations ##
    #######################

    def update_budgets(self) -> None:

        # Update budget integrity:
        for budget in self.budget_repo.get_all():
            budget.update_spent(self.expense_repo)
            self.budget_repo.update(budget)

        # Update internal representation and view:
        self.budgets = self.budget_repo.get_all()
        self.view.set_budgets(self.budgets)

    def modify_budget(self, pk: int | None, new_limit: str, period: str) -> None:

        # Remove budget if no spendings limit is set:
        if new_limit == "":
            if pk is not None:
                self.budget_repo.delete(pk)
            self.update_budgets()
            return

        # Parse limit as integer:
        try:
            new_limit_int = int(new_limit)
        except ValueError as exc:
            self.update_budgets()
            raise ValueError("Неправильный формат.\n"
                                + "Введите сумму целым числом.") from exc

        # Handler nagative limit:
        if new_limit_int < 0:
            self.update_budgets()
            raise ValueError("За этот период придется заработать.")

        # Handle nonexistent primary key:
        if pk is None:
            # Insert newly-created budget:
            budget_new = Budget(limitation=new_limit_int, period=period)
            self.budget_repo.add(budget_new)
        else:
            # Or update existing one:
            budget_old = self.budget_repo.get(pk)
            if budget_old is None:
                raise ValueError(f"Бюджета с pk=\"{pk}\" не существует")

            budget_old.limitation = new_limit_int
            self.budget_repo.update(budget_old)

        # Final update:
        self.update_budgets()