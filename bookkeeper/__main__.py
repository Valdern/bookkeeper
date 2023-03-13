"""
Простая программа для управления личными финансами.
"""

import sys

from PySide6.QtWidgets import QApplication  # pylint: disable=no-name-in-module

from bookkeeper.bookkeeper import Bookkeeper

from bookkeeper.view.view import View

from bookkeeper.repository.abstract_repository import repository_factory
from bookkeeper.repository.sqlite_repository import SQLiteRepository

###################
## Main finction ##
###################

# Create the application and it's interface object:
app = QApplication(sys.argv)
view = View()

# Repo factory:
repo_gen = repository_factory(SQLiteRepository, db_file="database/bookkeeper.db")

bookkeeper_app = Bookkeeper(view, repo_gen)

# Execute it!
bookkeeper_app.start_app()

# Exit program on application exit:
sys.exit(app.exec())