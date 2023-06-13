import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget, QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QComboBox, QDialog, QDialogButtonBox, QHBoxLayout, QLabel
from PyQt5.QtGui import QFont, QPixmap
import sqlite3
import traceback


class LoginWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle('Вход')
        self.layout = QVBoxLayout(self)

        image_label = QLabel()
        pixmap = QPixmap('123.jpg').scaled(300, 300)
        image_label.setPixmap(pixmap)
        image_label.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(image_label)

        self.username_label = QLabel('Логин:')
        self.username_edit = QLineEdit()

        self.password_label = QLabel('Пароль:')
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)

        self.login_button = QPushButton('Войти')
        self.exit_button = QPushButton('Выход')

        self.layout.addWidget(self.username_label)
        self.layout.addWidget(self.username_edit)
        self.layout.addWidget(self.password_label)
        self.layout.addWidget(self.password_edit)
        self.layout.addWidget(self.login_button)
        self.layout.addWidget(self.exit_button)

        self.login_button.clicked.connect(self.login)
        self.exit_button.clicked.connect(self.reject)

    def login(self):
        username = self.username_edit.text()
        password = self.password_edit.text()

        if username and password:
            self.accept()
        else:
            pass


class AddDataDialog(QDialog):
    def __init__(self, parent=None, update=False):
        super().__init__(parent)

        if update:
            self.setWindowTitle('Редактировать данные')
        else:
            self.setWindowTitle('Добавить данные')
        self.layout = QVBoxLayout(self)

        # Создание меток и полей ввода для каждого столбца таблицы
        self.labels = []
        self.line_edits = []

        self.conn = sqlite3.connect('ис_учёта_успеваемости.db')
        self.cursor = self.conn.cursor()

        # Получение списка столбцов выбранной таблицы
        selected_table = parent.selected_table
        self.cursor.execute(f"PRAGMA table_info({selected_table});")
        columns = self.cursor.fetchall()

        for column in columns:
            label = QLabel(column[1])
            self.labels.append(label)
            line_edit = QLineEdit()
            self.line_edits.append(line_edit)

        # Создание кнопок "ОК" и "Отмена"
        self.button_box = QDialogButtonBox()
        self.button_box.setStandardButtons(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Размещение виджетов на форме
        for label, line_edit in zip(self.labels, self.line_edits):
            self.layout.addWidget(label)
            self.layout.addWidget(line_edit)

        self.layout.addWidget(self.button_box)

    def get_input_data(self):
        # Получение введенных пользователем данных
        data = []
        for line_edit in self.line_edits:
            data.append(line_edit.text())
        return data


class DeleteDataDialog(QDialog):
    def __init__(self, parent=None, edit=False):
        super().__init__(parent)
        if edit:
            self.setWindowTitle('Редактировать данные')
        else:
            self.setWindowTitle('Удалить данные')
        self.layout = QVBoxLayout(self)

        if edit:
            self.label = QLabel('Введите ID записи для редактирования:')
        else:
            self.label = QLabel('Введите ID записи для удаления:')
        self.layout.addWidget(self.label)

        self.line_edit = QLineEdit()
        self.layout.addWidget(self.line_edit)

        self.button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)
        self.layout.addWidget(self.button_box)

    def get_input_id(self):
        return self.line_edit.text()


class DatabaseViewer(QDialog):
    def __init__(self):
        super().__init__()

        # Установка соединения с базой данных
        self.conn = sqlite3.connect('ис_учёта_успеваемости.db')
        self.cursor = self.conn.cursor()

        # Создание главного окна и размещение виджетов
        self.setWindowTitle('Database Viewer')
        self.setGeometry(100, 100, 800, 600)

        self.layout = QVBoxLayout(self)

        # Создание выпадающего списка для выбора таблицы
        self.table_selector = QComboBox(self)
        self.table_selector.currentIndexChanged.connect(self.select_table)
        self.table_selector.setStyleSheet("font-size: 14px; text-align: center;")
        self.layout.addWidget(self.table_selector)

        # Создание таблицы для отображения содержимого
        self.table_widget = QTableWidget(self)
        self.layout.addWidget(self.table_widget)

        # Создание кнопок "Добавить данные", "Удалить данные" и "Редактировать данные"
        buttons_layout = QHBoxLayout()
        self.add_data_button = QPushButton('Добавить данные', self)
        self.delete_data_button = QPushButton('Удалить данные', self)
        self.edit_data_button = QPushButton('Редактировать данные', self)
        self.exit_button = QPushButton('Выход', self)

        buttons_layout.addWidget(self.add_data_button)
        buttons_layout.addWidget(self.delete_data_button)
        buttons_layout.addWidget(self.edit_data_button)
        buttons_layout.addWidget(self.exit_button)
        
        self.layout.addLayout(buttons_layout)

        # Обновление выпадающего списка таблиц
        self.update_table_selector()

        # Подключение функций-обработчиков к кнопкам
        self.add_data_button.clicked.connect(self.add_data)
        self.delete_data_button.clicked.connect(self.delete_data)
        self.edit_data_button.clicked.connect(self.edit_data)
        self.exit_button.clicked.connect(self.reject)


    def edit_data(self):
        try:
            dialog = DeleteDataDialog(parent=self, edit=True)
            if dialog.exec_() == QDialog.Accepted:
                id_value = dialog.get_input_id()

                self.cursor.execute(f"PRAGMA table_info({self.selected_table});")
                columns = self.cursor.fetchall()
                if len(columns) < 1:
                    return
                first_field = columns[0][1]

                query = f"SELECT * FROM {self.selected_table} WHERE {first_field} = ?;"
                self.cursor.execute(query, (id_value,))
                current_data = self.cursor.fetchone()

                dialog = AddDataDialog(parent=self, update=True)
                dialog.selected_table = self.selected_table

                for line_edit, value in zip(dialog.line_edits, current_data):
                    line_edit.setText(str(value))

                if dialog.exec_() == QDialog.Accepted:
                    data = dialog.get_input_data()[1:]
                    query = f"UPDATE {self.selected_table} SET "
                    query += ", ".join([f"{column[1]} = ?" for column in columns[1:]])
                    query += f" WHERE {first_field} = ?;"
                    self.cursor.execute(query, data + [id_value])
                    self.conn.commit()

                    self.select_table()
        except Exception as e:
            print(f"Error occurred during editing: {e}")
            print(traceback.format_exc())

    def update_table_selector(self):
        # Очистка выпадающего списка
        self.table_selector.clear()

        # Получение списка таблиц и представлений из базы данных
        tables = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
        views = self.cursor.execute("SELECT name FROM sqlite_master WHERE type='view';").fetchall()

        # Добавление названий таблиц и представлений в выпадающий список
        for table in tables:
            self.table_selector.addItem(table[0])
        for view in views:
            self.table_selector.addItem(view[0])

    def select_table(self):
        # Очистка таблицы
        self.table_widget.clear()

        # Получение выбранной таблицы из выпадающего списка
        selected_table = self.table_selector.currentText()

        # Установка выбранной таблицы для отображения
        self.selected_table = selected_table

        # Получение списка полей выбранной таблицы
        self.cursor.execute(f"PRAGMA table_info({self.selected_table});")
        columns = self.cursor.fetchall()

        # Установка количества строк и столбцов в таблице
        self.table_widget.setRowCount(0)
        self.table_widget.setColumnCount(len(columns))

        # Заполнение заголовков столбцов таблицы названиями полей
        header_labels = [column[1] for column in columns]
        self.table_widget.setHorizontalHeaderLabels(header_labels)

        # Выполнение запроса для получения содержимого таблицы
        query = f"SELECT * FROM {self.selected_table};"
        self.cursor.execute(query)
        results = self.cursor.fetchall()

        # Установка количества строк в таблице
        self.table_widget.setRowCount(len(results))

        # Заполнение таблицы данными из запроса
        for row, result in enumerate(results):
            for col, value in enumerate(result):
                item = QTableWidgetItem(str(value))
                self.table_widget.setItem(row, col, item)

    def add_data(self):
        dialog = AddDataDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Получение введенных данных
            data = dialog.get_input_data()[1:]

            # Вставка данных в таблицу
            query = f"INSERT INTO {self.selected_table} VALUES ("
            query += ", ".join(["?" for _ in range(len(data))])
            query += ");"
            self.cursor.execute(query, data)
            self.conn.commit()
            
            # Обновление отображения таблицы
            self.select_table()

    def delete_data(self):
        # Открытие диалогового окна для ввода ID записи
        dialog = DeleteDataDialog(parent=self)
        if dialog.exec_() == QDialog.Accepted:
            # Получение введенного ID
            id_value = dialog.get_input_id()

            try:
                # Получить название первого поля
                self.cursor.execute(f"PRAGMA table_info({self.selected_table});")
                columns = self.cursor.fetchall()
                first_field = columns[0][1]

                # Удалить запись из таблицы на основе первого поля
                query = f"DELETE FROM {self.selected_table} WHERE {first_field} = ?;"
                self.cursor.execute(query, (id_value,))
                self.conn.commit()

                # Обновление отображения таблицы
                self.select_table()
            except Exception as e:
                print(f"Error occurred during deletion: {e}")
                print(traceback.format_exc())


if __name__ == '__main__':
    app = QApplication(sys.argv)

    # Отображение окна авторизации
    login_window = LoginWindow()
    if login_window.exec_() == QDialog.Accepted:
        # Проверка успешной авторизации
        # Отображение главного окна приложения
        database_viewer = DatabaseViewer()
        database_viewer.show()
    sys.exit(app.exec_())
