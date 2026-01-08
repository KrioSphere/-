from PyQt6.QtWidgets import (QDialog, QLineEdit, QTextEdit, QComboBox,
                             QDateEdit, QDialogButtonBox, QFormLayout,
                             QInputDialog, QVBoxLayout, QLabel, QProgressBar, QPushButton)
from PyQt6.QtCore import QDate
from database import ADD_NEW_CAT_TEXT


class TaskDialog(QDialog):

    def __init__(self, available_categories, title="", notes="", deadline=None, category=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Задача")
        self.setMinimumWidth(350)

        self.title_edit = QLineEdit(title)
        self.notes_edit = QTextEdit(notes)
        self.notes_edit.setMaximumHeight(100)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(False)
        self.category_combo.addItems(available_categories)
        self.category_combo.addItem(ADD_NEW_CAT_TEXT)

        if category and category in available_categories:
            self.category_combo.setCurrentText(category)
        else:
            self.category_combo.setCurrentIndex(0)

        self.category_combo.currentIndexChanged.connect(self.check_custom_category)

        self.deadline_edit = QDateEdit(calendarPopup=True)
        if deadline:
            self.deadline_edit.setDate(QDate.fromString(deadline, "yyyy-MM-dd"))
        else:
            self.deadline_edit.setDate(QDate.currentDate())

        self.button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QFormLayout(self)
        layout.addRow("Название:", self.title_edit)
        layout.addRow("Категория:", self.category_combo)
        layout.addRow("Заметки:", self.notes_edit)
        layout.addRow("Дедлайн:", self.deadline_edit)
        layout.addWidget(self.button_box)

    def check_custom_category(self):
        if self.category_combo.currentText() == ADD_NEW_CAT_TEXT:
            text, ok = QInputDialog.getText(self, "Новая категория", "Введите название категории:")
            if ok and text.strip():
                insert_index = self.category_combo.count() - 1
                self.category_combo.insertItem(insert_index, text.strip())
                self.category_combo.setCurrentIndex(insert_index)
            else:
                self.category_combo.setCurrentIndex(0)

    def get_data(self):
        cat = self.category_combo.currentText()
        if cat == ADD_NEW_CAT_TEXT:
            cat = "Без категории"
        return (self.title_edit.text().strip(),
                self.notes_edit.toPlainText().strip(),
                self.deadline_edit.date().toString("yyyy-MM-dd"),
                cat)


class StatsDialog(QDialog):
    """Окно статистики"""

    def __init__(self, db, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Статистика продуктивности")
        self.setFixedSize(300, 250)

        total, done, overdue, pending = db.get_stats()

        layout = QVBoxLayout(self)
        layout.addWidget(QLabel(f"<b>Всего задач:</b> {total}"))
        layout.addWidget(QLabel(f"✅ Выполнено: {done}"))
        layout.addWidget(QLabel(f"❌ Просрочено: {overdue}"))
        layout.addWidget(QLabel(f"⏳ В работе: {pending}"))
        layout.addSpacing(20)

        layout.addWidget(QLabel("Общий прогресс:"))
        progress_bar = QProgressBar()
        progress_bar.setStyleSheet(
            "QProgressBar { border: 1px solid grey; border-radius: 5px; text-align: center; } QProgressBar::chunk { background-color: #d1e7dd; width: 20px; }")

        if total > 0:
            progress_bar.setValue(int((done / total) * 100))
        else:
            progress_bar.setValue(0)

        layout.addWidget(progress_bar)

        btn = QPushButton("Закрыть")
        btn.clicked.connect(self.accept)
        layout.addWidget(btn)