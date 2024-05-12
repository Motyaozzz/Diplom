import sqlite3
import os

work_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

class Database:
   def __init__(self, db_name):
      self.conn = sqlite3.connect(db_name)
      cursor = self.conn.cursor()

      cursor.execute('''
         CREATE TABLE IF NOT EXISTS items (
               id INTEGER PRIMARY KEY,
               name TEXT NOT NULL,
               ser_num TEXT NOT NULL,
               gost_hash TEXT NOT NULL
         )
      ''')
      self.conn.commit()
      cursor.close()

   def insert_data(self, name, ser_num, gost_hash):
      cursor = self.conn.cursor()
      cursor.execute('INSERT INTO items (name, ser_num, gost_hash) VALUES (?, ?, ?)', (name, ser_num, gost_hash))
      self.conn.commit()
      cursor.close()
      
   def delete_data(self, x, y):
      cursor = self.conn.cursor()
      cursor.execute('DELETE FROM items WHERE '+y+' = ?', (x, ))
      cursor.execute(f'SELECT * FROM items')
      rows = cursor.fetchall()
      for i, row in enumerate(rows, start=1):
         cursor.execute(f'UPDATE items SET id = ? WHERE id = ?', (i, row[0]))
      self.conn.commit()
      cursor.close()

   def check(self, x, y):
      cursor = self.conn.cursor()
      info = cursor.execute('SELECT * FROM items WHERE '+y+' = ?', (x, )).fetchone()
      cursor.close()
      if info is None:
         return
      if len(info) == 0:
         return False
      else:
         return True
         
   def get_data_from_database(self):
      # Создаем подключение к базе данных
      cursor = self.conn.cursor()
      cursor.execute(f'SELECT * FROM items')
      rows = cursor.fetchall()
      cursor.close()
      return rows


   def close_connection(self):
      self.conn.close()

db = Database(os.path.join(work_dir,  'example.db'))