import sqlite3
import psycopg2

db_params = {
    'host': 'localhost',
    'port': '5432',
    'dbname': 'book',
    'user': 'postgres',
    'password': 'Aby@36261',
}

sqlite_conn = sqlite3.connect('raw_data/book.db')
sqlite_cur = sqlite_conn.cursor()



############################################### Migration code #########################################################
def insert_textbooks():
    sqlite_cur.execute("SELECT * FROM Textbooks;")
    data = sqlite_cur.fetchall()
    data = data[1:]
    try:
        pg_conn = psycopg2.connect(**db_params)
        pg_cur = pg_conn.cursor()
    
        for row in data:
            pg_cur.execute("""
                           INSERT INTO Textbooks ( book_title ) VALUES (%s);
                           """, row) 
        pg_conn.commit()
        print(f"The textbook table has been migrated successfully!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"The error you are getting id : {error}")
        if pg_conn is not None:
            pg_conn.rollback()
            
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        if pg_cur is not None:
            pg_cur.close()
        if pg_conn is not None:
            pg_conn.close()
            
 
           
def insert_chapters():
    sqlite_cur.execute("SELECT * FROM Chapters;")
    data = sqlite_cur.fetchall()
    data = data[1:]
    try:
        pg_conn = psycopg2.connect(**db_params)
        pg_cur = pg_conn.cursor()
    
        for row in data:
            pg_cur.execute("""
                           INSERT INTO chapters ( textbook_id, chapter_title ) VALUES (%s, %s);
                           """, row) 
        pg_conn.commit()
        print(f"The chapters table has been migrated successfully!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"The error you are getting id : {error}")
        if pg_conn is not None:
            pg_conn.rollback()
            
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        if pg_cur is not None:
            pg_cur.close()
        if pg_conn is not None:
            pg_conn.close()



def insert_qa():
    sqlite_cur.execute("SELECT * FROM Question_Answers;")
    data = sqlite_cur.fetchall()
    data = data[1:]
    try:
        pg_conn = psycopg2.connect(**db_params)
        pg_cur = pg_conn.cursor()
    
        for row in data:
            pg_cur.execute("""
                           INSERT INTO question_answers ( chapter_id, question, answer ) VALUES (%s, %s, %s);
                           """, row) 
        pg_conn.commit()
        print(f"The chapters table has been migrated successfully!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"The error you are getting id : {error}")
        if pg_conn is not None:
            pg_conn.rollback()
            
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        if pg_cur is not None:
            pg_cur.close()
        if pg_conn is not None:
            pg_conn.close()
            
            
            
def insert_bp():
    sqlite_cur.execute("SELECT * FROM BulletPoints;")
    data = sqlite_cur.fetchall()
    data = data[1:]
    try:
        pg_conn = psycopg2.connect(**db_params)
        pg_cur = pg_conn.cursor()
    
        for row in data:
            pg_cur.execute("""
                           INSERT INTO bulletpoints ( chapter_id, bullet_point ) VALUES (%s, %s);
                           """, row) 
        pg_conn.commit()
        print(f"The chapters table has been migrated successfully!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"The error you are getting id : {error}")
        if pg_conn is not None:
            pg_conn.rollback()
            
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        if pg_cur is not None:
            pg_cur.close()
        if pg_conn is not None:
            pg_conn.close()



def insert_fb():
    sqlite_cur.execute("SELECT * FROM FillInTheBlanks;")
    data = sqlite_cur.fetchall()
    data = data[1:]
    try:
        pg_conn = psycopg2.connect(**db_params)
        pg_cur = pg_conn.cursor()
    
        for row in data:
            pg_cur.execute("""
                           INSERT INTO fillintheblanks ( chapter_id, fb_question, fb_answer ) VALUES (%s, %s, %s);
                           """, row) 
        pg_conn.commit()
        print(f"The chapters table has been migrated successfully!")

    except (Exception, psycopg2.DatabaseError) as error:
        print(f"The error you are getting id : {error}")
        if pg_conn is not None:
            pg_conn.rollback()
            
    finally:
        sqlite_cur.close()
        sqlite_conn.close()
        if pg_cur is not None:
            pg_cur.close()
        if pg_conn is not None:
            pg_conn.close()




            
            


            
            



        
        












