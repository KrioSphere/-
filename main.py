import sys
import csv
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout,
    QListWidget, QListWidgetItem, QLineEdit, QPushButton,
    QLabel, QComboBox, QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt, QDate

# Импорт наших модулей
from database import TaskDatabase, STATUS_PENDING, STATUS_DONE, STATUS_OVERDUE
from widgets import TaskWidget
from dialogs import TaskDialog, StatsDialog

LIGHT_THEME = """
    QWidget { background-color: #f0f2f5; color: #000000; }
    QLineEdit, QTextEdit, QComboBox, QDateEdit { 
        background-color: white; color: black; border: 1px solid #ccc; border-radius: 5px; padding: 5px; 
    }
    QListWidget { background: transparent; border: none; outline: 0; }
    QPushButton { background-color: #e0e0e0; border: 1px solid #ccc; border-radius: 5px; padding: 5px; }
    QPushButton:hover { background-color: #d0d0d0; }
    QDialog { background-color: #ffffff; }
"""

DARK_THEME = """
    QWidget { background-color: #121212; color: #ffffff; }
    QLineEdit, QTextEdit, QComboBox, QDateEdit { 
        background-color: #2d2d2d; color: #e0e0e0; border: 1px solid #444; border-radius: 5px; padding: 5px; 
    }
    QListWidget { background: transparent; border: none; outline: 0; }
    QPushButton { background-color: #333333; color: #e0e0e0; border: 1px solid #444; border-radius: 5px; padding: 5px; }
    QPushButton:hover { background-color: #444444; }
    QDialog { background-color: #1e1e1e; }
    QMessageBox { background-color: #1e1e1e; color: white; }
    QLabel { color: #e0e0e0; }
"""


class ToDoApp(QWidget):
    def __init__(self):
        super().__init__()
        self.db = TaskDatabase()
        self.is_dark_mode = False  # Флаг текущей темы
        self.init_ui()
        self.load_tasks()

        self.apply_theme()

    def init_ui(self):
        self.setWindowTitle("ToDo Список Pro")
        self.resize(500, 750)

        self.title_label = QLabel("Менеджер задач")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet("font-size: 22px; font-weight: bold; margin: 10px;")

        top_menu_layout = QHBoxLayout()
        self.theme_btn = QPushButton("🌓 Тема")
        self.stats_btn = QPushButton("📊 Статистика")
        self.export_btn = QPushButton("💾 Экспорт")

        top_menu_layout.addWidget(self.theme_btn)
        top_menu_layout.addWidget(self.stats_btn)
        top_menu_layout.addWidget(self.export_btn)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("🔍 Поиск по названию...")


        self.filter_layout = QHBoxLayout()
        self.cat_filter = QComboBox()

        self.status_filter = QComboBox()
        self.status_filter.addItems(["Все статусы", STATUS_PENDING, STATUS_DONE, STATUS_OVERDUE])

        self.reset_filter_btn = QPushButton("❌")
        self.reset_filter_btn.setFixedWidth(30)

        self.filter_layout.addWidget(QLabel("Фильтр:"))
        self.filter_layout.addWidget(self.cat_filter)
        self.filter_layout.addWidget(self.status_filter)
        self.filter_layout.addWidget(self.reset_filter_btn)

        self.task_list_widget = QListWidget()
        self.task_list_widget.setSpacing(8)


        self.add_btn = QPushButton("+ Создать задачу")
        self.add_btn.setStyleSheet(
            "background-color: #007bff; color: white; font-weight: bold; padding: 12px; border-radius: 8px;")

        self.complete_btn = QPushButton("Выполнить / Вернуть")
        self.remove_btn = QPushButton("Удалить выбранное")
        self.remove_btn.setStyleSheet("background-color: #842029; color: white; padding: 8px; border-radius: 5px;")

        layout = QVBoxLayout(self)
        layout.addLayout(top_menu_layout)
        layout.addWidget(self.title_label)
        layout.addWidget(self.search_input)
        layout.addLayout(self.filter_layout)
        layout.addWidget(self.add_btn)
        layout.addWidget(self.task_list_widget)

        btns_layout = QHBoxLayout()
        btns_layout.addWidget(self.complete_btn)
        btns_layout.addWidget(self.remove_btn)
        layout.addLayout(btns_layout)

        self.add_btn.clicked.connect(self.open_add_dialog)
        self.complete_btn.clicked.connect(self.toggle_task_status)
        self.remove_btn.clicked.connect(self.remove_task)
        self.task_list_widget.itemDoubleClicked.connect(self.edit_task)
        self.task_list_widget.itemSelectionChanged.connect(self.update_selection_styles)

        self.cat_filter.currentTextChanged.connect(self.load_tasks)
        self.status_filter.currentTextChanged.connect(self.load_tasks)
        self.reset_filter_btn.clicked.connect(self.reset_filters)
        self.search_input.textChanged.connect(self.load_tasks)

        self.stats_btn.clicked.connect(self.show_stats)
        self.export_btn.clicked.connect(self.export_tasks)
        self.theme_btn.clicked.connect(self.toggle_theme)

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        self.apply_theme()

        for i in range(self.task_list_widget.count()):
            item = self.task_list_widget.item(i)
            widget = self.task_list_widget.itemWidget(item)
            if widget:
                widget.set_theme(self.is_dark_mode)

    def apply_theme(self):
        app_style = DARK_THEME if self.is_dark_mode else LIGHT_THEME
        QApplication.instance().setStyleSheet(app_style)

        self.add_btn.setStyleSheet(
            "background-color: #007bff; color: white; font-weight: bold; padding: 12px; border-radius: 8px;")

        if self.is_dark_mode:
            self.remove_btn.setStyleSheet("background-color: #61131a; color: white; padding: 8px; border-radius: 5px;")
        else:
            self.remove_btn.setStyleSheet("background-color: #dc3545; color: white; padding: 8px; border-radius: 5px;")

    def update_filter_combo(self):
        current = self.cat_filter.currentText()
        all_cats = self.db.get_all_categories()

        self.cat_filter.blockSignals(True)
        self.cat_filter.clear()
        self.cat_filter.addItems(["Все категории"] + all_cats)

        idx = self.cat_filter.findText(current)
        self.cat_filter.setCurrentIndex(idx if idx >= 0 else 0)
        self.cat_filter.blockSignals(False)

    def reset_filters(self):
        self.cat_filter.setCurrentIndex(0)
        self.status_filter.setCurrentIndex(0)
        self.search_input.clear()

    def load_tasks(self):
        self.task_list_widget.clear()

        rows = self.db.get_tasks(
            category_filter=self.cat_filter.currentText(),
            status_filter=self.status_filter.currentText(),
            search_text=self.search_input.text().strip()
        )

        for row in rows:
            tid, title, notes, deadline, status, category = row
            category = category if category else "Без категории"

            item = QListWidgetItem(self.task_list_widget)
            custom_widget = TaskWidget(title, notes, deadline, status, category, item.isSelected(), self.is_dark_mode)
            item.setSizeHint(custom_widget.sizeHint())
            item.setData(Qt.ItemDataRole.UserRole, tid)
            item.setData(Qt.ItemDataRole.UserRole + 1, {
                "title": title, "notes": notes, "deadline": deadline, "status": status, "category": category
            })
            self.task_list_widget.setItemWidget(item, custom_widget)

        if self.sender() != self.cat_filter:
            self.update_filter_combo()

    def update_selection_styles(self):
        for i in range(self.task_list_widget.count()):
            item = self.task_list_widget.item(i)
            widget = self.task_list_widget.itemWidget(item)
            if widget:
                widget.set_theme(self.is_dark_mode)
                widget.is_selected = item.isSelected()
                widget.update_style()

    def open_add_dialog(self):
        cats = self.db.get_all_categories()
        dialog = TaskDialog(cats, parent=self)
        if dialog.exec():
            title, notes, deadline, category = dialog.get_data()
            if not title: return
            self.db.add_task(title, notes, deadline, category)
            self.load_tasks()

    def edit_task(self, item):
        tid = item.data(Qt.ItemDataRole.UserRole)
        data = item.data(Qt.ItemDataRole.UserRole + 1)
        cats = self.db.get_all_categories()

        dialog = TaskDialog(cats, data['title'], data['notes'], data['deadline'], data['category'], self)
        if dialog.exec():
            title, notes, deadline, category = dialog.get_data()
            self.db.update_task(tid, title, notes, deadline, data['status'], category)
            self.load_tasks()

    def toggle_task_status(self):
        today = QDate.currentDate().toString("yyyy-MM-dd")
        for i in range(self.task_list_widget.count()):
            item = self.task_list_widget.item(i)
            if item.isSelected():
                tid = item.data(Qt.ItemDataRole.UserRole)
                data = item.data(Qt.ItemDataRole.UserRole + 1)

                new_status = STATUS_DONE if data['status'] != STATUS_DONE else \
                    (STATUS_OVERDUE if data['deadline'] < today else STATUS_PENDING)

                self.db.update_status(tid, new_status)
        self.load_tasks()

    def remove_task(self):
        for i in range(self.task_list_widget.count()):
            item = self.task_list_widget.item(i)
            if item.isSelected():
                self.db.delete_task(item.data(Qt.ItemDataRole.UserRole))
        self.load_tasks()

    def show_stats(self):
        dialog = StatsDialog(self.db, self)
        dialog.exec()

    def export_tasks(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить отчет", "", "CSV Files (*.csv);;All Files (*)")
        if file_path:
            try:
                rows = self.db.get_tasks()
                with open(file_path, mode='w', newline='', encoding='utf-8-sig') as file:
                    writer = csv.writer(file, delimiter=';')
                    writer.writerow(["ID", "Заголовок", "Заметки", "Дедлайн", "Статус", "Категория"])
                    writer.writerows(rows)
                QMessageBox.information(self, "Успех", f"Успешно сохранено в:\n{file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Ошибка", f"Не удалось сохранить:\n{e}")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = ToDoApp()
    window.show()
    sys.exit(app.exec())