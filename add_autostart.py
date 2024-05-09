# import winreg
# import ctypes
# import sys
# import os
# work_dir = os.path.dirname(os.path.realpath(__file__))
# pythonw_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "pythonw.exe")

# def add_to_startup(value_name, executable_path):
#    key = winreg.HKEY_CURRENT_USER
#    key_path = "Software\Microsoft\Windows\CurrentVersion\Run"
   
#    try:
#       with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as reg_key:
#          winreg.SetValueEx(reg_key, value_name, 0, winreg.REG_SZ, executable_path)
#    except Exception as e:
#       print("Error adding to startup:", e)

# def remove_from_startup(value_name):
#    key = winreg.HKEY_CURRENT_USER
#    key_path = "Software\Microsoft\Windows\CurrentVersion\Run"
   
#    try:
#       with winreg.OpenKey(key, key_path, 0, winreg.KEY_WRITE) as reg_key:
#          winreg.DeleteValue(reg_key, value_name)
#    except Exception as e:
#       print("Error removing from startup:", e)

# def run_as_admin():
#    if not ctypes.windll.shell32.IsUserAnAdmin():
#       ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# # Имя значения и путь к исполняемому файлу программы
# value_name = "USB Controller (Matvey)"
# executable_path = pythonw_path + " " + os.path.join(work_dir, 'usb_block.pyw')

# # Проверка прав доступа и запуск от имени администратора при необходимости
# run_as_admin()

# # Удаление программы из автозапуска
# remove_from_startup(value_name)

# # Добавление программы в автозапуск
# # add_to_startup(value_name, executable_path)

from asyncio import run
import os
import subprocess
import sys
import ctypes
import getpass

work_dir = os.path.dirname(os.path.realpath(__file__))
pythonw_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "pythonw.exe")

adm=getpass.getuser()

def run_as_admin():
   if not ctypes.windll.shell32.IsUserAnAdmin():
      ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

def create_task(program_path):
   # Команда для создания задачи планировщика
   command = 'schtasks /create /tn "USB Controller (Matvey)" /tr "{}" /sc ONLOGON /RL HIGHEST /ru {}'.format(program_path, adm)
   
   # Выполнение команды
   subprocess.call(command, shell=True)

def delete_task():
   # Команда для удаления задачи планировщика
   command = 'schtasks /delete /tn "USB Controller (Matvey)" /f'
   
   # Выполнение команды
   subprocess.call(command, shell=True)


# Путь к вашей основной программе
program_path = pythonw_path + " " + os.path.join(work_dir, 'usb_block.pyw')

run_as_admin()
# Создание задачи планировщика
create_task(program_path)

# Удаление задачи планировщика
# delete_task()





