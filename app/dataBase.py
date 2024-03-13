from multiprocessing import connection
import sqlite3

class Database:
   def __init__(self, db_name):
      self.conn = sqlite3.connect(db_name)
      self.cursor = self.conn.cursor()

      self.cursor.execute('''
         CREATE TABLE IF NOT EXISTS items (
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL,
               description TEXT
         )
      ''')

   def insert_data(self, name, description):
      self.cursor.execute('INSERT INTO items (name, description) VALUES (?, ?)', (name, description))
      self.conn.commit()
      
   def check(self,user_id):
         info=self.cursor.execute('SELECT * FROM items WHERE description = ?', (user_id, )).fetchone()
         if info is None:
            return
         if len(info) == 0: 
            return False
         else:
            return True

   def close_connection(self):
      self.conn.close()