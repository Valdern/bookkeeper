import pytest
import sqlite3
from dataclasses import dataclass
from datetime import datetime

from bookkeeper.repository.sqlite_repository import SQLiteRepository

##################################
## Testing stand initialization ##
##################################

DB_FILE    = "database/bookkeeper_test.db"
FIELD_INT  = 58008
FIELD_STR  = "\"I am string\""
FIELD_DATE = datetime.now()

@pytest.fixture
def custom_class():
    @dataclass
    class Custom:
        pk         : int       = 0
        field_int  : int       = FIELD_INT
        field_str  : str       = FIELD_STR
        field_date : datetime  = FIELD_DATE

    return Custom

@pytest.fixture
def custom_initialization():
    with sqlite3.connect(DB_FILE) as con:
        cur = con.cursor()

        # Remove the table to be tested:
        cur.execute("DROP TABLE IF EXISTS custom")

        # Create it back from scratch:
        cur.execute("CREATE TABLE IF NOT EXISTS custom(field_int int, field_str int, field_date text)")
    con.close()

@pytest.fixture
def repo(custom_initialization, custom_class):
    return SQLiteRepository(db_file=DB_FILE, cls=custom_class)

############################
## SQL repository testing ##
############################

# Basic operational test:
def test_crud(repo, custom_class):
    # Create
    obj_add = custom_class()
    pk      = repo.add(obj_add)
    assert pk == obj_add.pk

    # Read
    obj_get = repo.get(pk)
    assert obj_get is not None
    assert obj_get.pk         == obj_add.pk
    assert obj_get.field_int  == obj_add.field_int
    assert obj_get.field_str  == obj_add.field_str
    assert obj_get.field_date == obj_add.field_date

    # Update
    obj_update = custom_class(
        field_int  = 5318008,
        field_str  = "\"I am an another string\"",
        field_date = datetime.now(),
        pk         = pk)
    repo.update(obj_update)
    obj_get = repo.get(pk)
    assert obj_get.pk         == obj_update.pk
    assert obj_get.field_int  == obj_update.field_int
    assert obj_get.field_str  == obj_update.field_str
    assert obj_get.field_date == obj_update.field_date

    # Delete
    repo.delete(pk)
    assert repo.get(pk) is None

# Test a bunch of corner cases to lift the coverage to 100%:

def test_cannot_add_with_filled_pk(repo, custom_class):
    obj = custom_class(pk=1)
    with pytest.raises(ValueError):
        repo.add(obj)

def test_cannot_add_without_pk_property(repo):
    with pytest.raises(ValueError):
        repo.add(0)

def test_get_nonexistent(repo):
    assert repo.get(-1) is None

def test_get_all(repo, custom_class):
    # Fill repo with objects:
    objs = [custom_class() for _ in range(5)]
    for obj in objs:
        repo.add(obj)

    # Veridy
    objs_get_all = repo.get_all()
    assert objs == objs_get_all


def test_get_all_with_condition(repo, custom_class):
    # Fill repo with objects:
    objs = [custom_class(field_int=i) for i in range(5)]
    for obj in objs:
        repo.add(obj)

    # Verify result:
    assert repo.get_all({'field_int':         0}) == [objs[0]]
    assert repo.get_all({'field_str': FIELD_STR}) == objs

def test_cannot_update_nonexistent(repo, custom_class):
    obj = custom_class(pk=2)
    with pytest.raises(ValueError):
        repo.update(obj)

def test_cannot_update_without_pk_property(repo, custom_class):
    with pytest.raises(ValueError):
        repo.update(0)

def test_cannot_delete_nonexistent(repo):
    with pytest.raises(ValueError):
        repo.delete(-1)