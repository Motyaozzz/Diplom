import sqlite3
import os

work_dir = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')

class Database:
   def __init__(self, db_name):
      self.conn = sqlite3.connect(db_name)
      cursor = self.conn.cursor()

      cursor.execute('''
      CREATE TABLE IF NOT EXISTS main (
      device_id INTEGER PRIMARY KEY,
      ser_num TEXT UNIQUE NOT NULL,
      model_id INTEGER NOT NULL,
      interface_id INTEGER NOT NULL
      )
      ''')
      cursor.execute('''   
      CREATE TABLE IF NOT EXISTS interface (
      interface_id INTEGER PRIMARY KEY NOT NULL,
      interface_type TEXT UNIUQE NOT NULL
      )
      ''')
      
      cursor.execute('''   
      CREATE TABLE IF NOT EXISTS model (
      model_id INTEGER PRIMARY KEY,
      model TEXT UNIQUE NOT NULL 
      )
      ''')
            
      cursor.execute('''   
      CREATE TABLE IF NOT EXISTS hash (
      device_id INTEGER PRIMARY KEY,
      hash TEXT UNIQUE NOT NULL
      )
      ''')
      
      self.conn.commit()
      cursor.close()

   def insert_data(self, ser_num, model, gost_hash, interface_type):
      cursor = self.conn.cursor()
      
      cursor.execute("SELECT * FROM model WHERE model=?", (model,))
      models = cursor.fetchall()
      if len(models) == 0:
         cursor.execute("INSERT INTO model (model) VALUES (?)", (model,))

      cursor.execute("SELECT model_id FROM model WHERE model=?", (model,))
      model_id = cursor.fetchone()[0]


      cursor.execute("SELECT * FROM interface WHERE interface_type=?", (interface_type,))
      interfaces = cursor.fetchall()
      if len(interfaces) == 0:
         cursor.execute("INSERT INTO interface (interface_type) VALUES (?)", (interface_type,))

      cursor.execute("SELECT interface_id FROM interface WHERE interface_type=?", (interface_type,))
      interface_id = cursor.fetchone()[0]

      cursor.execute("INSERT INTO main (ser_num, model_id, interface_id) VALUES (?, ?, ?)", (str(ser_num), int(model_id), int(interface_id)))
      cursor.execute("SELECT device_id FROM main WHERE ser_num=?", (ser_num,))
      device_id = cursor.fetchone()[0]

      cursor.execute("INSERT INTO hash (device_id, hash) VALUES (?, ?)", (int(device_id), gost_hash))
         
      self.conn.commit()
      cursor.close()
      
   def __reindex(self, table, column) -> None:
      cursor = self.conn.cursor()
      cursor.execute(f'SELECT * FROM {table}')
      rows = cursor.fetchall()

      for i, row in enumerate(rows, start=1):
         cursor.execute(f'UPDATE {table} SET {column} = ? WHERE {column} = ?', (i, row[0]))
      
         if table == "model":
            cursor.execute("UPDATE main SET model_id = ? WHERE model_id = ?", (i, row[0]))
         if table == "interface":
            cursor.execute("UPDATE main SET interface_id = ? WHERE interface_id = ?", (i, row[0]))
      
   def delete_data(self, x):
      cursor = self.conn.cursor()

      cursor.execute("SELECT device_id, interface_id, model_id FROM main WHERE ser_num = ?", (x,))
      deletion = cursor.fetchone()

      if deletion:
         device_id, interface_id, model_id = deletion

         cursor.execute("DELETE FROM hash WHERE device_id=?", (int(device_id),))
         self.__reindex("hash", "device_id")
         cursor.execute("DELETE FROM main WHERE device_id=?", (int(device_id),))
         self.__reindex("main", "device_id")

         cursor.execute("SELECT interface_id FROM main WHERE interface_id=?", (int(interface_id),))
         check_interface = cursor.fetchall()

         cursor.execute("SELECT model_id FROM main WHERE model_id = ?", (int(model_id),))
         check_model = cursor.fetchall()
         
         if check_model is None or len(check_model) == 0:
            cursor.execute("DELETE FROM model WHERE model_id=?", (model_id,))
            self.__reindex("model", "model_id")
         if check_interface is None or len(check_interface) == 0:
            cursor.execute("DELETE FROM interface WHERE interface_id=?", (interface_id,))
            self.__reindex("interface", "interface_id")
      

      self.conn.commit()
      cursor.close()

   def check(self, x, y, z):
      cursor = self.conn.cursor()
      info = cursor.execute('SELECT * FROM '+z+' WHERE '+y+' = ?', (x, )).fetchone()
      cursor.close()
      if info is None:
         return
      if len(info) == 0:
         return False
      else:
         return True
         
   def get_data_from_database(self):
      cursor = self.conn.cursor()
      
      cursor.execute("SELECT main.ser_num, model.model, interface.interface_type, hash.hash FROM main \
      JOIN model ON main.model_id = model.model_id \
      JOIN interface ON main.interface_id = interface.interface_id \
      JOIN hash ON main.device_id = hash.device_id")

      rows = cursor.fetchall()

      cursor.close()
      return rows
   
   def close_connection(self):
      self.conn.close()

db = Database(os.path.join(work_dir,  'example.db'))