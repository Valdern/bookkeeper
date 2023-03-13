from datetime import datetime

import pytest

from bookkeeper.repository.memory_repository import MemoryRepository
from bookkeeper.models.budget import Period, Budget

@pytest.fixture
def repo():
    return MemoryRepository()

def test_create_with_full_args_list():
    b = Budget(limitation=100, period="day", spent=10, pk=2)

    assert b.limitation == 100
    assert b.period     == Period.DAY
    assert b.spent      == 10
    assert b.pk         == 2

def test_create_brief():
    b = Budget(100, "day", 10, 2)

    assert b.limitation == 100
    assert b.period     == Period.DAY
    assert b.spent      == 10
    assert b.pk         == 2


def test_can_add_to_repo(repo):
    b  = Budget(100, "day", 10)
    pk = repo.add(b)

    assert b.pk == pk