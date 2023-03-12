"""
Модуль описывает репозиторий, работающий поверх СУБД SQLite
"""

import logging
import sqlite3
from inspect import get_annotations
from typing import Any

from bookkeeper.repository.abstract_repository import AbstractRepository, T


class SQLiteRepository(AbstractRepository[T]):
    """
    Репозиторий, предназначенный для работы с СУБД SQLite
    """

    def __init__(self, db_file: str, clazz: type) -> None:
        self.db_file = db_file
        self.table_name = clazz.__name__.lower()
        self.fields = get_annotations(clazz, eval_str=True)
        self.fields.pop('pk')
        self.entity_class = clazz

        names = ", ".join(self.fields.keys())
        placeholder = ", ".join("?" * len(self.fields))
        upd_placeholder = ", ".join([f"{field}=?" for field in self.fields.keys()])
        self.queries = {
            'foreign_keys': "PRAGMA foreign_keys = ON",
            'add': f"INSERT INTO {self.table_name} ({names}) VALUES ({placeholder})",
            'get': f"SELECT ROWID, * FROM {self.table_name} WHERE ROWID = ?",
            'get_all': f"SELECT ROWID, * FROM {self.table_name}",
            'update': f"UPDATE {self.table_name} SET {upd_placeholder} WHERE ROWID = ?",
            'delete': f"DELETE FROM {self.table_name} WHERE ROWID = ?",
        }

    def _map_row(self, values: list[Any]) -> T:
        """  Метод преобразует запись из SQLite БД в объект типа T  """
        class_args = {}
        for field_name, field_value in zip(self.fields.keys(), values[1:]):
            class_args[field_name] = field_value

        obj: T = self.entity_class(**class_args)
        obj.pk = values[0]
        return obj

    def add(self, obj: T) -> int:
        logging.debug("Starting add method with obj = %s", obj)
        if getattr(obj, 'pk', None) != 0:
            raise ValueError(
                f"Unable to insert object {obj}: it already has a primary key"
            )
        values = [getattr(obj, x) for x in self.fields]

        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(self.queries['foreign_keys'])
            cursor.execute(self.queries['add'], values)
        connection.close()

        if cursor.lastrowid is not None:
            obj.pk = cursor.lastrowid

        logging.debug("Exiting add method with: %d", obj.pk)
        return obj.pk

    def get(self, pk: int) -> T | None:
        logging.debug("Starting get method with pk = %d", pk)
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            rows = cursor.execute(self.queries['get'], [pk]).fetchall()
        connection.close()

        rows_number = len(rows)
        if rows_number == 0:
            return None
        if rows_number > 1:
            raise ValueError(f"Several entries found for provided pk={pk}")

        execution_result = self._map_row(rows[0])
        logging.info("Exiting get method with: %s", execution_result)
        return execution_result

    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        logging.debug("Starting get_all method with where = %s", where)

        query = self.queries['get_all']
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()

            if where is not None:
                query = self._add_conditions_to_query(query, where)
                rows = cursor.execute(query, list(where.values())).fetchall()
            else:
                rows = cursor.execute(query).fetchall()
        connection.close()

        execution_result = [self._map_row(row) for row in rows]
        logging.debug("Exiting get_all method with: %s", execution_result)
        return execution_result

    def update(self, obj: T) -> None:
        logging.debug("Starting update method with obj=%s", obj)

        if getattr(obj, 'pk', None) is None:
            raise ValueError(
                "Object without `pk` attribute can't be used in update operation"
            )

        values = [getattr(obj, field) for field in self.fields] + [obj.pk]

        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()
            cursor.execute(self.queries['foreign_keys'])
            cursor.execute(self.queries['update'], values)

            if cursor.rowcount == 0:
                raise ValueError(f"Unable to update object with pk={obj.pk}")
        connection.close()

        logging.debug("Exiting update method")

    def delete(self, pk: int) -> None:
        logging.debug("Starting delete method with pk = %d", pk)
        with sqlite3.connect(self.db_file) as connection:
            cursor = connection.cursor()

            cursor.execute(self.queries['delete'], [pk])
            if cursor.rowcount == 0:
                raise ValueError(f"Unable to delete object with pk={pk}")
        connection.close()

        logging.debug("Exiting delete method")

    @staticmethod
    def _add_conditions_to_query(initial_query: str, conditions: dict[str, Any]) -> str:
        """
        Метод добавляет условия conditions в блок WHERE запроса initial_query
        """
        conditions_string = " AND ".join(
            [f"{condition} = ?" for condition in conditions.keys()]
        )
        return initial_query + f" WHERE {conditions_string}"