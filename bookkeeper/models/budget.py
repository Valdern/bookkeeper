"""
Модель бюджета
"""

from dataclasses import dataclass
from enum import Enum

Period = Enum('Period', ["HOUR", "DAY", "WEEK", "MONTH"])


@dataclass(slots=True)
class Budget:
    """
    Сущность, моделирующая бюджет
    total_amount - сумма бюджета
    category_id - id категории расходов
    period - срок ограничения на сумму бюджета
    pk - id записи в базе данных (primary key)
    """

    total_amount: int
    category_id: int
    period: Period
    pk: int = 0