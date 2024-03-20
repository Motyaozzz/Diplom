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
               ser_num TEXT NOT NULL,
               gost_hash TEXT NOT NULL
         )
      ''')

   def insert_data(self, name, ser_num, gost_hash):
      self.cursor.execute('INSERT INTO items (name, ser_num, gost_hash) VALUES (?, ?, ?)', (name, ser_num, gost_hash))
      self.conn.commit()
      
   def delete_data(self, gost_hash):
      self.cursor.execute('DELETE FROM items WHERE gost_hash = ?',(gost_hash,))
      self.conn.commit()
      
   def check(self, x, y):
         info=self.cursor.execute('SELECT * FROM items WHERE '+y+' = ?', (x, )).fetchone()
         if info is None:
            return
         if len(info) == 0: 
            return False
         else:
            return True
         
   # def check_ser_num(self,ser_num):
   #       info=self.cursor.execute('SELECT * FROM items WHERE gost_hash = ?', (ser_num, )).fetchone()
   #       if info is None:
   #          return
   #       if len(info) == 0: 
   #          return False
   #       else:
   #          return True

   def close_connection(self):
      self.conn.close()