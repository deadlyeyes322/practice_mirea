from db import CSVtoSQLiteImporter
from db import DB_FILE, TABLE_NAME
import sys



def main():
    try:
        data_file = input('Введите имя CSV файла (без расширения): ').strip()
        if not data_file:
            print("Ошибка: Не указано имя файла")
            return
        csv_file = f"{data_file}.csv"

        with CSVtoSQLiteImporter(DB_FILE) as importer:
            imported_rows = importer.import_csv(csv_file, TABLE_NAME)
            print(f"Успешно импортировано {imported_rows} записей")


    except FileNotFoundError as e:
        print(f"Ошибка: Файл не найден - {e}")


    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        sys.exit(1)
if __name__ == "__main__":
    main()

