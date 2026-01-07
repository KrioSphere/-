import sqlite3
from datetime import datetime
from PyQt6.QtCore import QDate

# Константы
STATUS_PENDING = "Не выполнено"
STATUS_DONE = "Выполнено"
STATUS_OVERDUE = "Просрочено"

DEFAULT_CATEGORIES = ["Домашние дела", "Учеба", "Личные дела"]
ADD_NEW_CAT_TEXT = "➕ Своя категория..."


class TaskDatabase:
    def __init__(self, db_name="tasks_v2.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.init_db()

    def init_db(self):
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS tasks 
            (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, notes TEXT, deadline TEXT, status TEXT)''')
        try:
            self.cursor.execute("ALTER TABLE tasks ADD COLUMN category TEXT")
        except sqlite3.OperationalError:
            pass
        self.conn.commit()

    def update_overdue_statuses(self):
        """Обновляет статусы просроченных задач"""
        today = QDate.currentDate().toString("yyyy-MM-dd")
        self.cursor.execute("UPDATE tasks SET status = ? WHERE status != ? AND deadline < ?",
                            (STATUS_OVERDUE, STATUS_DONE, today))
        self.conn.commit()

    def get_tasks(self, category_filter=None, status_filter=None, search_text=None):
        """Получает задачи с учетом фильтров и сортировки"""
        self.update_overdue_statuses()

        query = "SELECT id, title, notes, deadline, status, category FROM tasks"
        params = []
        conditions = []

        if category_filter and category_filter != "Все категории":
            conditions.append("category = ?")
            params.append(category_filter)

        if status_filter and status_filter != "Все статусы":
            conditions.append("status = ?")
            params.append(status_filter)

        if search_text:
            conditions.append("title LIKE ?")
            params.append(f"%{search_text}%")

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        # Сортировка: Сначала активные, потом просроченные, в конце выполненные
        query += f""" ORDER BY CASE status 
            WHEN '{STATUS_PENDING}' THEN 0 
            WHEN '{STATUS_OVERDUE}' THEN 1 
            WHEN '{STATUS_DONE}' THEN 2 
            ELSE 3 END, deadline ASC"""

        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def add_task(self, title, notes, deadline, category):
        # Проверяем статус при создании
        status = STATUS_OVERDUE if deadline < QDate.currentDate().toString("yyyy-MM-dd") else STATUS_PENDING
        self.cursor.execute("INSERT INTO tasks (title, notes, deadline, status, category) VALUES (?, ?, ?, ?, ?)",
                            (title, notes, deadline, status, category))
        self.conn.commit()

    def update_task(self, tid, title, notes, deadline, status, category):
        # Если задача не выполнена, перепроверяем дату на просрочку
        if status != STATUS_DONE:
            status = STATUS_OVERDUE if deadline < QDate.currentDate().toString("yyyy-MM-dd") else STATUS_PENDING

        self.cursor.execute("UPDATE tasks SET title=?, notes=?, deadline=?, status=?, category=? WHERE id=?",
                            (title, notes, deadline, status, category, tid))
        self.conn.commit()

    def update_status(self, tid, new_status):
        self.cursor.execute("UPDATE tasks SET status = ? WHERE id = ?", (new_status, tid))
        self.conn.commit()

    def delete_task(self, tid):
        self.cursor.execute("DELETE FROM tasks WHERE id = ?", (tid,))
        self.conn.commit()

    def get_all_categories(self):
        self.cursor.execute("SELECT DISTINCT category FROM tasks")
        db_cats = {row[0] for row in self.cursor.fetchall() if row[0]}
        if ADD_NEW_CAT_TEXT in db_cats:
            db_cats.remove(ADD_NEW_CAT_TEXT)
        return sorted(list(db_cats.union(set(DEFAULT_CATEGORIES))))

    def get_stats(self):
        """Возвращает статистику для диалога"""
        self.cursor.execute("SELECT status FROM tasks")
        rows = self.cursor.fetchall()
        total = len(rows)
        done = sum(1 for r in rows if r[0] == STATUS_DONE)
        overdue = sum(1 for r in rows if r[0] == STATUS_OVERDUE)
        pending = sum(1 for r in rows if r[0] == STATUS_PENDING)
        return total, done, overdue, pending