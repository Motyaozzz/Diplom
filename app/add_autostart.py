from asyncio import run
import os
import subprocess
import sys
import ctypes
import getpass
import platform

os_type = platform.system()
work_dir = os.path.dirname(os.path.realpath(__file__))
pythonw_path = os.path.join(os.path.dirname(os.path.realpath(sys.executable)), "pythonw.exe")
c = os.getcwd()


if os_type == "Windows":

   adm=getpass.getuser()

   def run_as_admin():
      if not ctypes.windll.shell32.IsUserAnAdmin():
         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

   def create_task(program_path):
      # Команда для создания задачи планировщика
      command = 'schtasks /create /tn "Device Controller" /tr "{}" /sc ONLOGON /RL HIGHEST /ru {}'.format(program_path, adm)
      command_start = 'schtasks /run /tn "Device Controller'
      # Выполнение команды
      subprocess.call(command, shell=True)
      subprocess.call(command_start, shell=True)

   def delete_task():
      # Команда для удаления задачи планировщика
      command = 'schtasks /delete /tn "Device Controller" /f'
      
      # Выполнение команды
      subprocess.call(command, shell=True)


   # Путь к вашей основной программе
   program_path = pythonw_path + " " + os.path.join(work_dir, 'device_block.pyw')

   run_as_admin()
   # Создание задачи планировщика
   create_task(program_path)

   # Удаление задачи планировщика
   # delete_task()

elif os_type == "Linux":
   if os.geteuid() != 0:
   # Перезапускаем программу из-под sudo с запросом пароля
      os.execlp('sudo', 'sudo', sys.executable, *sys.argv)

   rule = f"""[Unit]
Description=Device Controller
After=mnt-wibble.mount
StartLimitIntervalSec=0 

[Service]
Type=simple
Restart=always
User=root
RestartSec=60
WorkingDirectory={work_dir}
ExecStart={c}/venv/bin/python {work_dir}/device_block.pyw

[Install]
WantedBy=multi-user.target
   """
# ExecStart={workdir}/../venv/bin/python {work_dir}/device_block.pyw - попробовать

   # Путь для сохранения правила
   rule_path = "/etc/systemd/system/Device_Controller.service"

   # Запись правила в файл
   with open(rule_path, 'w') as f:
      f.write(rule)
   
   subprocess.run(["systemctl", "daemon-reload"])
   subprocess.run(["systemctl", "enable", "Device_Controller.service"])
   subprocess.run(["systemctl", "start", "Device_Controller.service"])
