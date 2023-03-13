"""
Модель бюджета
"""

from dataclasses import dataclass
from enum import Enum

Period = Enum('Period', ["HOUR", "DAY", "WEEK", "MONTH"])


@dataclass(slots=True)
class Budget:
    limitation : int      # Maximum allowed sum of spendings
    period     : Period   # The period to be budgeted
    spent      : int = 0  # The amount of money spent in the period
    pk         : int = 0  # Primary key

    def __init__(self, limitation: int, period: str,
                       spent: int = 0, pk: int = 0):
        # Parse the period:
        if period == "day":
            self.period = Period.DAY
        elif period == "week":
            self.period = Period.WEEK
        elif period == "month":
            self.period = Period.MONTH
        else:
            raise ValueError(f"unknown period \"{period}\" for budget\n"
                             + "should be \"day\", \"week\" or \"month\"")

        # Set other parameters:
        self.limitation = limitation
        self.spent      = spent
        self.pk         = pk

    def update_spent(self, expense_repo: AbstractRepository[Expense]) -> None:
        # Generate timestamp for operation:
        date = datetime.now().isoformat()[:10] # YYYY-MM-DD format

        if self.period == Period.DAY:
            date_mask   = f"{date}"
            period_exps = expense_repo.get_all_by_pattern(patterns={"expense_date":date_mask})

        elif self.period == Period.WEEK:
            weekday_now    = datetime.now().weekday()
            day_now        = datetime.fromisoformat(date)
            first_week_day = day_now - timedelta(days=weekday_now)

            period_exps = []
            for i in range(7):
                weekday   = first_week_day + timedelta(days=i)
                date_mask = f"{weekday.isoformat()[:10]}"

                period_exps += expense_repo.get_all_by_pattern(patterns={"expense_date":date_mask})

        elif self.period == Period.MONTH:
            date_mask = f"{date[:7]}-"

            period_exps = expense_repo.get_all_by_pattern(patterns={"expense_date":date_mask})

        # Update money spent:
        self.spent = sum([int(exp.amount) for exp in period_exps])  # pylint: disable=consider-using-generator