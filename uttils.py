import os
import csv
import sqlite3 as sql


def create_table(conn, table_name, columns):
    c = conn.cursor()
    columns_list = ', '.join([f'"{col}"' for col in columns])
    c.execute(f'''
              CREATE TABLE IF NOT EXISTS {table_name} (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
                {columns_list}
                )
            ''')
    conn.commit()

def import_csv_to_sqlite(csv_file,db_file, table_name):
    if not os.path.exists(csv_file):
        raise FileNotFoundError(f"{csv_file} not found")
    with open(csv_file, 'r', encoding = 'utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader)
    conn = sql.connect(db_file)
    
    try:
        create_table(conn, table_name, headers)
        with open(csv_file, 'r', encoding = 'utf-8') as f:
            reader = csv.DictReader(f)
            c = conn.cursor()
            placeholders = ', '.join(['?' for _ in headers])
            columns = ', '.join([f'"{col}"' for col in headers])
            sql_query = f'INSERT INTO {table_name} ({columns}) VALUES ({placeholders})'
            
            for row in reader:
                values = [row[col] for col in headers]
                c.execute(sql_query, values)
                print(values)
            conn.commit()
        print(f"{reader.line_num - 1}")

    except Exception as e:
        conn.rollback()
        raise e
    
    finally:
        conn.close()

data_file = input('file name: ')

if __name__ == '__main__':
    CSV_FILE = f'data_pars/{data_file}.csv'
    DB_FILE = 'database.db'
    TABLE_NAME = 'imployees'

    try:
        import_csv_to_sqlite(
            csv_file=CSV_FILE,
            db_file=DB_FILE,
            table_name=TABLE_NAME
        )
    except Exception as e:
        print(f"Import error: {str(e)}")