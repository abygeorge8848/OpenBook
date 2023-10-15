import sqlite3
import psycopg2

from db_server_connect import insert_textbooks, insert_chapters, insert_qa, insert_bp, insert_fb


db_params = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'book',
    'user': 'postgres',
    'password': 'Aby@36261',
}

sqlite_conn = sqlite3.connect('raw_data/book.db')
sqlite_cur = sqlite_conn.cursor()


#Migrates all the sql data from the local sqlite3 database to the postgreSQL database server
if __name__ == "__main__":
    insert_textbooks()
    insert_chapters()
    insert_qa()
    insert_bp()
    insert_fb()
