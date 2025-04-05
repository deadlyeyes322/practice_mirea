import sqlite3 as sql
import os
import csv
from typing import List, Dict


class CSVtoSQLiteImporter:
    """Класс для импорта данных из CSV файла в SQLite базу данных"""
    
    def __init__(self, db_file: str = 'database.db'):
        """
        Инициализация импортера
        :param db_file: Путь к файлу базы данных SQLite
        """
        self.db_file = db_file
        self.conn = None

    def __enter__(self):
        """Поддержка контекстного менеджера"""
        self.connect()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Поддержка контекстного менеджера"""
        self.close()

    def connect(self):
        """Установка соединения с базой данных"""
        self.conn = sql.connect(self.db_file)

    def close(self):
        """Закрытие соединения с базой данных"""
        if self.conn:
            self.conn.close()
            self.conn = None

    def create_table(self, table_name: str, columns: List[str]) -> None:
        """
        Создание таблицы в базе данных
        :param table_name: Имя таблицы
        :param columns: Список колонок
        """
        if not self.conn:
            raise ConnectionError("Database connection is not established")

        columns_list = ', '.join([f'"{col}" TEXT' for col in columns])
        
        with self.conn:
            cursor = self.conn.cursor()
            cursor.execute(f'''
                CREATE TABLE IF NOT EXISTS {table_name} (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    {columns_list}
                )
            ''')

    def import_csv(self, csv_file: str, table_name: str) -> int:
        """
        Импорт данных из CSV файла в таблицу
        :param csv_file: Путь к CSV файлу
        :param table_name: Имя таблицы для импорта
        :return: Количество импортированных строк
        """
        if not os.path.exists(csv_file):
            raise FileNotFoundError(f"CSV file {csv_file} not found")

        # Чтение заголовков из CSV
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            headers = next(reader)

        if not self.conn:
            self.connect()

        try:
            # Создание таблицы
            self.create_table(table_name, headers)

            # Импорт данных
            with open(csv_file, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                cursor = self.conn.cursor()

                placeholders = ', '.join(['?' for _ in headers])
                columns = ', '.join([f'"{col}"' for col in headers])
                sql_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
                
                count = 0
                for row in reader:
                    values = [row[col] for col in headers]
                    cursor.execute(sql_query, values)
                    count += 1

                self.conn.commit()
                return count

        except Exception as e:
            if self.conn:
                self.conn.rollback()
            raise e

    @staticmethod
    def get_table_info(db_file: str, table_name: str) -> Dict:
        """
        Получение информации о таблице
        :param db_file: Путь к файлу БД
        :param table_name: Имя таблицы
        :return: Словарь с информацией о таблице
        """
        with sql.connect(db_file) as conn:
            cursor = conn.cursor()
            
            # Получаем информацию о колонках
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            
            # Получаем количество записей
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            count = cursor.fetchone()[0]
            
            return {
                'table_name': table_name,
                'columns': [col[1] for col in columns],
                'row_count': count
            }


if __name__ == '__main__':
    try:
        # Ввод параметров от пользователя
        data_file = input('Введите имя CSV файла (без расширения): ').strip()
        csv_file = f'{data_file}.csv'
        db_file = 'database.db'
        table_name = 'employees'  # Исправлено с 'imployees' на 'employees'

        # Создаем экземпляр импортера
        importer = CSVtoSQLiteImporter(db_file)
        
        # Импортируем данные
        with importer:
            imported_rows = importer.import_csv(csv_file, table_name)
            print(f"Успешно импортировано {imported_rows} записей")

        # Показываем информацию о таблице
        table_info = CSVtoSQLiteImporter.get_table_info(db_file, table_name)
        print(f"\nИнформация о таблице {table_info['table_name']}:")
        print(f"Колонки: {', '.join(table_info['columns'])}")
        print(f"Всего записей: {table_info['row_count']}")

    except Exception as e:
        print(f"Ошибка: {str(e)}")
