from PyQt6.QtWidgets import QFrame, QVBoxLayout, QLabel
from database import STATUS_DONE, STATUS_OVERDUE


class TaskWidget(QFrame):
    """Виджет отдельной плитки задачи с поддержкой тем"""

    def __init__(self, title, notes, deadline, status, category, is_selected=False, is_dark_mode=False, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.setFrameShape(QFrame.Shape.StyledPanel)

        # Сохраняем параметры для обновления стиля
        self.current_status = status
        self.is_selected = is_selected
        self.is_dark_mode = is_dark_mode

        self.title_label = QLabel()
        self.category_label = QLabel()
        self.deadline_label = QLabel()
        self.notes_label = QLabel()

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.category_label)
        self.layout.addWidget(self.deadline_label)
        self.layout.addWidget(self.notes_label)

        self.update_content(title, notes, deadline, status, category, is_selected, is_dark_mode)

    def update_content(self, title, notes, deadline, status, category, is_selected, is_dark_mode):
        self.current_status = status
        self.is_selected = is_selected
        self.is_dark_mode = is_dark_mode

        icon = "✅" if status == STATUS_DONE else ("❌" if status == STATUS_OVERDUE else "⏳")

        # Цвет текста зависит от темы
        text_color = "#e0e0e0" if is_dark_mode else "black"
        subtext_color = "#aaaaaa" if is_dark_mode else "#666666"

        self.title_label.setText(f"<b>{icon} {title}</b>")
        self.title_label.setStyleSheet(f"color: {text_color};")

        self.category_label.setText(f"<i>📁 {category}</i>")
        self.category_label.setStyleSheet(f"color: {subtext_color}; font-size: 11px;")

        self.deadline_label.setText(f"📅 Срок: {deadline}")
        self.deadline_label.setStyleSheet(f"color: {text_color};")

        note_text = notes.strip().split('\n')[0][:35] + "..." if notes else "заметок нет"
        self.notes_label.setText(f"📝 {note_text}")
        self.notes_label.setStyleSheet(f"color: {text_color};")

        self.update_style()

    def set_theme(self, is_dark):
        self.is_dark_mode = is_dark
        # Обновляем цвета текста
        text_color = "#e0e0e0" if is_dark else "black"
        subtext_color = "#aaaaaa" if is_dark else "#666666"

        self.title_label.setStyleSheet(f"color: {text_color};")
        self.category_label.setStyleSheet(f"color: {subtext_color}; font-size: 11px;")
        self.deadline_label.setStyleSheet(f"color: {text_color};")
        self.notes_label.setStyleSheet(f"color: {text_color};")

        self.update_style()

    def update_style(self):
        if self.current_status == STATUS_DONE:
            bg_color = "#1e3a2a" if self.is_dark_mode else "#d1e7dd"
            border_base = "#2f5c40" if self.is_dark_mode else "#badbcc"
        elif self.current_status == STATUS_OVERDUE:
            bg_color = "#4a1e1e" if self.is_dark_mode else "#f8d7da"
            border_base = "#6b2b2b" if self.is_dark_mode else "#f5c6cb"
        else:
            bg_color = "#2d2d2d" if self.is_dark_mode else "#ffffff"
            border_base = "#444444" if self.is_dark_mode else "#cccccc"

        border_color = "#4a90e2" if self.is_selected else border_base
        border_width = "2px" if self.is_selected else "1px"

        self.setStyleSheet(f"""
            TaskWidget {{
                background-color: {bg_color};
                border: {border_width} solid {border_color};
                border-radius: 8px;
            }}
            QLabel {{ background: transparent; }}
        """)