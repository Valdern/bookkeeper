"""
Модуль описывает репозиторий, работающий поверх СУБД SQLite
"""

import sqlite3
from inspect import get_annotations
from typing import Any, Callable
from datetime import datetime

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, предназначенный для работы с СУБД SQLite
    """

    # Class static variables:
    DEFAULT_DATE_FORMAT: str
    DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

    def __init__(self, db_file: str, cls: type) -> None:
        # Type annotations:
        self.db_file: str  # Database file
        self.table_name: str  # Name of a table in database
        self.cls: Callable[[], T]  # Class constructor of type T
        self.fields: dict[str, type]  # Field of a class to be stored
        self.queries: dict[str, str]  # Shortcuts of SQL queries to be made

        # Initialization:
        self.table_name = cls.__name__.lower()
        self.db_file = db_file
        self.fields = get_annotations(cls, eval_str=True)
        self.fields.pop('pk')
        self.cls = cls

        # Pregenerate the queries to be used in database access methods:
        names = ", ".join(self.fields.keys())
        pholder = ", ".join("?" * len(self.fields))
        ph_upd = ", ".join([f"{field}=?" for field in self.fields.keys()])

        self.queries = {
            'foreign_keys': "PRAGMA foreign_keys = ON",
            'create': f"CREATE TABLE IF NOT EXISTS {self.table_name} ({names})",
            'add': f"INSERT INTO {self.table_name} ({names}) VALUES ({pholder})",
            'get': f"SELECT ROWID, * FROM {self.table_name} WHERE ROWID = ?",
            'get_all': f"SELECT ROWID, * FROM {self.table_name}",
            'update': f"UPDATE {self.table_name} SET {ph_upd} WHERE ROWID = ?",
            'delete': f"DELETE FROM {self.table_name} WHERE ROWID = ?",
        }

        # Create the requested table in the database file:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(self.queries['create'])
        con.close()

    def generate_object(self, fields: dict[str, type], values: list[Any]) -> T:
        """
        Вспомогательный метод, используемый для генерации объектов класса T
        из значений, хранящихся в базе даных.
        """
        class_arguments = {}

        for field_name, field_value in zip(fields.keys(), values[1:]):
            field_type = fields[field_name]

            if field_type == datetime:
                field_value = datetime.strptime(field_value, self.DEFAULT_DATE_FORMAT)

            class_arguments[field_name] = field_value

        obj = self.cls(**class_arguments)
        obj.pk = values[0]

        return obj

    def add(self, obj: T) -> int:
        # Check for input values:
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(f"Unable to add object {obj} with filled `pk` attribute")

        # Generate the query:
        values = [getattr(obj, x) for x in self.fields]

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(self.queries['foreign_keys'])

            # Insert row into database:
            cur.execute(self.queries['add'], values)
        con.close()

        if cur.lastrowid is not None:
            obj.pk = cur.lastrowid

        return obj.pk

    def get(self, pk: int) -> T | None:
        # Generate the query:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            rows = cur.execute(self.queries['get'], [pk]).fetchall()
        con.close()

        # Check result:
        num_rows = len(rows)
        if num_rows == 0:
            return None
        if num_rows > 1:
            raise ValueError(f"Several entries found with pk={pk}")

        # Generate the resulting object:
        return self.generate_object(self.fields, rows[0])

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        # Generate the query:
        query_base = self.queries['get_all']

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()

            if where is not None:
                conditions = " AND ".join([f"{field} = ?" for field in where.keys()])
                query = query_base + f" WHERE {conditions}"

                rows = cur.execute(query, list(where.values())).fetchall()
            else:
                rows = cur.execute(query_base).fetchall()
        con.close()

        return [self.generate_object(self.fields, row) for row in rows]

    def get_all_by_pattern(self, patterns: dict[str, str]) -> list[T]:
        # Insert '%' sign to allow pattern-matching
        values = [f"%{v}%" for v in patterns.values()]
        where = dict(zip(patterns.keys(), values))

        # Call regular get_all():
        return self.get_all(where=where)

    def update(self, obj: T) -> None:
        if getattr(obj, 'pk', None) is None:
            raise ValueError("Unable to update object without `pk` attribute")

        values = [getattr(obj, field) for field in self.fields] + [obj.pk]

        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()
            cur.execute(self.queries['foreign_keys'])

            # Update the entry with ROWID=pk:
            print(self.queries['update'])
            print(values)

            cur.execute(self.queries['update'], values)

            if cur.rowcount == 0:
                raise ValueError(f"Unable to update object with pk={obj.pk}")
        con.close()

    def delete(self, pk: int) -> None:
        with sqlite3.connect(self.db_file) as con:
            cur = con.cursor()

            # Remove the entry with ROWID=pk:
            cur.execute(self.queries['delete'], [pk])
            if cur.rowcount == 0:
                raise ValueError("Unable to delete object with pk={pk}")
        con.close()
