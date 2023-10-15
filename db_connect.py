import sqlite3

def create_table():
    conn = sqlite3.connect('raw_data/book.db')
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS book (
            id INTEGER PRIMARY KEY,
            question TEXT,
            answer TEXT,
            bullet_points TEXT,
            FBquestion TEXT,
            FBanswer TEXT
        )
    ''')

    conn.commit()
    conn.close()
    
def clear_all_tables():
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()
        cursor.execute("DELETE FROM Chapters")
        cursor.execute("DELETE FROM Textbooks")
        cursor.execute("DELETE FROM Question_Answers")
        cursor.execute("DELETE FROM FillInTheBlanks")
        cursor.execute("DELETE FROM BulletPoints")
        conn.commit()
    except sqlite3.Error as e:
        print("SQLite error:", e)
    finally:
        if conn:
            conn.close()
  
 
 
def insert_book(book_title):
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()
           
        cursor.execute("INSERT INTO Textbooks (book_title) VALUES (?)",
                           (book_title,))
        conn.commit()
        
    except sqlite3.Error as e:
        print("\n SQLite error has occured : ", e)
        return None
    
    finally:
        if conn:
            conn.close() 
        
            
            
def get_previous_chapter_id():
    
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT chapter_id FROM Chapters ORDER BY chapter_id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            previous_chapter_id = row[0]
            return previous_chapter_id
        else:
            return 1
        
    except sqlite3.Error as e:
        print("\n SQLite error has occured : ", e)
        return None
    
    finally:
        if conn:
            conn.close()
            
            

def insert_chapter(chapter_title):
    
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()
        
        cursor.execute("SELECT textbook_id FROM Textbooks ORDER BY textbook_id DESC LIMIT 1")
        row = cursor.fetchone()
        
        if row:
            last_textbook_id = row[0]
            cursor.execute("INSERT INTO Chapters (textbook_id, chapter_title) VALUES (?, ?)",
                           (last_textbook_id, chapter_title))
            conn.commit()
            
            cursor.execute("SELECT chapter_id FROM Chapters ORDER BY chapter_id DESC LIMIT 1")
            chapter_row = cursor.fetchone()
            
            if chapter_row:
                last_chapter_id = chapter_row[0]
                return last_chapter_id
            else:
                return 1
            
        else:
            return 1
        
    except sqlite3.Error as e:
        print("\n SQLite error has occured : ", e)
        return None
    
    finally:
        if conn:
            conn.close()
            
            


    

def insert_qa(chapter_id, question, answer):
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()
        
        cursor.execute("INSERT INTO Question_Answers (chapter_id, question_text, answer_text) VALUES (?, ?, ?)",
                           (chapter_id, question, answer))
        conn.commit()
            
    except sqlite3.Error as e:
        print("\n SQLite error has occured : ", e)
        return None
    
    finally:
        if conn:
            conn.close()
            

            
    
def insert_fbqa(chapter_id, FBquestion, FBanswer):
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO FillInTheBlanks (chapter_id, fb_question, fb_answer) VALUES (?, ?, ?)",
                           (chapter_id, FBquestion, FBanswer))
        conn.commit()
            
    except sqlite3.Error as e:
        print("\n SQLite error has occured : ", e)
        return None
    
    finally:
        if conn:
            conn.close()
            
    
            
            
def insert_bp(chapter_id, bullet_point):
    try:
        conn = sqlite3.connect('raw_data/book.db')
        cursor = conn.cursor()

        cursor.execute("INSERT INTO BulletPoints (chapter_id, bullet_point_text) VALUES (?, ?)",
                           (chapter_id, bullet_point))
        conn.commit()
            
    except sqlite3.Error as e:
        print("\n SQLite error has occured : ", e)
        return None
    
    finally:
        if conn:
            conn.close()
    
    
    
 

if __name__=='__main__':
    clear_all_tables()
    insert_book("TrialBook")















