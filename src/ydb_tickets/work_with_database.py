import sqlite3

class DatabaseManager:
    def __init__(self, db_path: str):
        """
        Инициализация менеджера базы данных.
        :param db_path: путь к файлу базы данных SQLite
        """
        self.db_path = db_path
        self.connection = None

    def connect(self):
        """Устанавливает соединение с базой данных."""
        try:
            self.connection = sqlite3.connect(self.db_path)
            print("✅ Соединение с базой данных установлено.")
        except sqlite3.Error as e:
            print(f"❌ Ошибка при подключении к базе данных: {e}")

    def execute_query(self, query: str, params: tuple = ()):
        """
        Выполняет SQL-запрос (например, INSERT, UPDATE, DELETE).
        :param query: SQL-запрос
        :param params: параметры для запроса (если есть)
        :return: количество изменённых строк
        """
        if not self.connection:
            print("⚠️ Нет соединения с базой данных. Подключитесь сначала.")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            self.connection.commit()
            print(f"✅ Запрос выполнен успешно. Изменено строк: {cursor.rowcount}")
            return cursor.rowcount
        except sqlite3.Error as e:
            print(f"❌ Ошибка при выполнении запроса: {e}")
            return None

    def fetch_query(self, query: str, params: tuple = ()):
        """
        Выполняет SELECT-запрос и возвращает результат.
        :param query: SQL-запрос
        :param params: параметры для запроса
        :return: список кортежей с результатами
        """
        if not self.connection:
            print("⚠️ Нет соединения с базой данных. Подключитесь сначала.")
            return None

        try:
            cursor = self.connection.cursor()
            cursor.execute(query, params)
            result = cursor.fetchall()
            print(f"✅ Запрос выполнен. Получено {len(result)} строк.")
            return result
        except sqlite3.Error as e:
            print(f"❌ Ошибка при выполнении запроса: {e}")
            return None

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.connection:
            self.connection.close()
            self.connection = None
            print("🔌 Соединение с базой данных закрыто.")