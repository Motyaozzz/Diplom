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
   command_start = 'schtasks /run /tn "USB Controller (Matvey)'
   # Выполнение команды
   subprocess.call(command, shell=True)
   subprocess.call(command_start, shell=True)

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
