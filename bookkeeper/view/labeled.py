from typing import Any

from PySide6        import QtWidgets
from PySide6.QtCore import Qt  # pylint: disable=no-name-in-module


class LabeledLineInput(QtWidgets.QWidget):
    """
    Поле ввода с подписью.
    """

    def __init__(
        self,
        label_text  : str,
        placeholder : str,
        *args       : Any,
        **kwargs    : Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.placeholder = placeholder

        # Label:
        self.label = QtWidgets.QLabel(label_text)

        # Line-edit:
        self.input = QtWidgets.QLineEdit(self.placeholder)

        # Horizontal layout:
        self.box_layout = QtWidgets.QHBoxLayout()

        self.box_layout.addWidget(self.label, stretch=1)
        self.box_layout.addWidget(self.input, stretch=5)

        self.setLayout(self.box_layout)

    def clear(self) -> None:
        self.input.setText(self.placeholder)

    def text(self) -> str:
        return self.input.text()

    def set_text(self, text: str) -> None:
        self.input.setText(text)

class LabeledComboBoxInput(QtWidgets.QWidget):
    """
    Поле выбора из нескольких вариантов.
    """

    def __init__(
        self,
        text     : str,
        items    : list[str],
        *args    : Any,
        **kwargs : Any
    ):
        super().__init__(*args, **kwargs)

        # Label:
        self.label = QtWidgets.QLabel(text)

        # Combo box:
        self.combo_box = QtWidgets.QComboBox()

        self.combo_box.setEditable(True)
        self.combo_box.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded) # type: ignore
        self.combo_box.setMaxVisibleItems(16)

        self.set_items(items)

        # Horizontal layout:
        self.box_layout = QtWidgets.QHBoxLayout()
        self.box_layout.addWidget(self.label, stretch=1)
        self.box_layout.addWidget(self.combo_box, stretch=5)

        self.setLayout(self.box_layout)

    def clear(self) -> None:
        self.combo_box.setCurrentText(self.combo_box.placeholderText())

    def text(self) -> str:
        return self.combo_box.currentText()

    def set_text(self, text: str) -> None:
        self.combo_box.setCurrentText(text)

    def set_items(self, items: list[str]) -> None:
        self.items = items

        self.combo_box.clear()
        self.combo_box.addItems(items)

        if len(items) != 0:
            self.combo_box.setPlaceholderText(items[0])
        else:
            self.combo_box.setPlaceholderText("...")

        self.clear()