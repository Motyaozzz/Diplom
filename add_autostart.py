import winreg
import ctypes
import sys
import os
work_dir = os.path.dirname(os.path.realpath(__file__))
pythonw_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "pythonw.exe")

def add_to_startup(value_name, executable_path):
   key = winreg.HKEY_CURRENT_USER
   key_path = "Software\Microsoft\Windows\CurrentVersion\Run"
   
   try:
      with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as reg_key:
         winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, executable_path)
   except Exception as e:
      print("Error adding to startup:", e)

def remove_from_startup(value_name):
   key = winreg.HKEY_CURRENT_USER
   key_path = "Software\Microsoft\Windows\CurrentVersion\Run"
   
   try:
      with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as reg_key:
         winreg.DeleteValue(reg_key, value_name)
   except Exception as e:
      print("Error removing from startup:", e)

def run_as_admin():
   if not ctypes.windll.shell32.IsUserAnAdmin():
      ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# Имя значения и путь к исполняемому файлу программы
value_name = "USB Controller (Matvey)"
executable_path = pythonw_path + " " + os.path.join(work_dir, 'usb_block.pyw')

# Проверка прав доступа и запуск от имени администратора при необходимости
run_as_admin()

# Удаление программы из автозапуска
remove_from_startup(value_name)

# Добавление программы в автозапуск
add_to_startup(value_name, executable_path)

