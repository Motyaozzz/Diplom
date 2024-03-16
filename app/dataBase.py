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
               gost_hash TEXT
         )
      ''')

   def insert_data(self, name, gost_hash):
      self.cursor.execute('INSERT INTO items (name, gost_hash) VALUES (?, ?)', (name, gost_hash))
      self.conn.commit()
      
   def check(self,gost_hash):
         info=self.cursor.execute('SELECT * FROM items WHERE gost_hash = ?', (gost_hash, )).fetchone()
         if info is None:
            return
         if len(info) == 0: 
            return False
         else:
            return True

   def close_connection(self):
      self.conn.close()