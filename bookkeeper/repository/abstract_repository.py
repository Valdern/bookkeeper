"""
Модуль содержит описание абстрактного репозитория

Репозиторий реализует хранение объектов, присваивая каждому объекту уникальный
идентификатор в атрибуте pk (primary key). Объекты, которые могут быть сохранены
в репозитории, должны поддерживать добавление атрибута pk и не должны
использовать его для иных целей.
"""

from abc import ABC, abstractmethod
from typing import Generic, TypeVar, Protocol, Any


class Model(Protocol):  # pylint: disable=too-few-public-methods
    """
    Модель должна содержать атрибут pk
    """
    pk: int


T = TypeVar('T', bound=Model)


class AbstractRepository(ABC, Generic[T]):
    """
    Абстрактный репозиторий.
    Абстрактные методы:
    add
    get
    get_all
    update
    delete
    """

    @abstractmethod
    def add(self, obj: T) -> int:
        """
        Добавить объект в репозиторий, вернуть id объекта,
        также записать id в атрибут pk.
        """

    @abstractmethod
    def get(self, pk: int) -> T | None:
        """ Получить объект по id """

    @abstractmethod
    def get_all(self, where: dict[str, Any] | None = None) -> list[T]:
        """
        Получить все записи по некоторому условию
        where - условие в виде словаря {'название_поля': значение}
        если условие не задано (по умолчанию), вернуть все записи
        """

    @abstractmethod
    def get_all_by_pattern(self, patterns: dict[str, str]) -> list[T]:
        """
        Получить все записи по некоторому условию
        pattern - условие в виде словаря {'название_поля': значение},
        где значение имеет тип строки и для выполнения условия
        переданное значение должно содержаться внутри реального
        значения поля.
        """

    @abstractmethod
    def update(self, obj: T) -> None:
        """ Обновить данные об объекте. Объект должен содержать поле pk. """

    @abstractmethod
    def delete(self, pk: int) -> None:
        """ Удалить запись """

def repository_factory(
    repo_type : Any,
    db_file   : str | None = None
) -> Callable[[Model], Any]:
    """
    Конкретная фабрика абстрактных репозиториев:
    больше абстракции богу абстракции!
    """

    if db_file is None:
        def repo_gen_nofile(model: Model) -> Any:
            return repo_type[model](cls=model)
        return repo_gen_nofile

    def repo_gen_withfile(model: Model) -> Any:
        return repo_type[model](db_file=db_file, cls=model)
    return repo_gen_withfile
