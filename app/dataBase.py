import sqlite3
import os

work_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

class Database:
   def __init__(self, db_name):
      self.conn = sqlite3.connect(db_name)
      cursor = self.conn.cursor()

      cursor.execute('''
         CREATE TABLE IF NOT EXISTS hash (
               ser_num TEXT PRIMARY KEY,
               name TEXT NOT NULL,
               gost_hash TEXT NOT NULL
         )
      ''')
      cursor.execute('''   
         CREATE TABLE IF NOT EXISTS interface (
               name TEXT PRIMARY KEY,
               interface_type TEXT NOT NULL
         )
      ''')
      # cursor.execute("REINDEX <table_name>") вот это пересчитывает
      self.conn.commit()
      cursor.close()

   def insert_data(self, ser_num, name, gost_hash, interface_type):
      cursor = self.conn.cursor()
      cursor.execute("SELECT * FROM interface WHERE name = ?", (name,))
      existing_record = cursor.fetchone()
      cursor.execute("INSERT INTO hash (ser_num, name, gost_hash) VALUES (?, ?, ?)", (ser_num, name, gost_hash))
      if existing_record is None:
         cursor.execute("INSERT INTO interface (name, interface_type) VALUES (?, ?)", (name, interface_type))
      self.conn.commit()
      cursor.close()
      
      
   def delete_data(self, x):
      cursor = self.conn.cursor()
      cursor.execute("SELECT name FROM hash WHERE ser_num = ?", (x,))
      deleted_model = cursor.fetchone()[0]
      cursor.execute("DELETE FROM interface WHERE name = ?", (deleted_model,))
      cursor.execute("DELETE FROM hash WHERE ser_num = ?", (x,))

      self.conn.commit()
      cursor.close()

   def check(self, x, y):
      cursor = self.conn.cursor()
      info = cursor.execute('SELECT * FROM hash WHERE '+y+' = ?', (x, )).fetchone()
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
      cursor.execute(f'SELECT * FROM hash')
      
      cursor.execute("SELECT hash.*, interface.* FROM hash LEFT JOIN interface ON hash.name = interface.name")
      combined_records = cursor.fetchall()
      cursor.close()
      return combined_records
   
   def close_connection(self):
      self.conn.close()

db = Database(os.path.join(work_dir,  'example.db'))