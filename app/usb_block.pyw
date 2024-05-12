from dataBase import db, work_dir
from pygost.gost34112012 import GOST34112012
import ctypes
import sys
import time
import platform
import os
from typing import List


OS_TYPE = platform.system()

def extract_string(value):
   if value is None:
      return ""
   return str(value)

if OS_TYPE == "Linux":
   from diskinfo import Disk, DiskInfo
   import subprocess

   if os.geteuid() != 0:
   # Перезапускаем программу из-под sudo с запросом пароля
      os.execlp('sudo', 'sudo', sys.executable, *sys.argv)

   udev_rule = """ACTION=="add"
KERNEL=="sd[b-z]*"
OWNER!="root"
ENV{UDISKS_PRESENTATION_HIDE}="1"
ENV{UDISKS_PRESENTATION_NOPOLICY}="1"
ENV{UDISKS_AUTOMOUNT_HINT}="never"
ENV{UDISKS_SYSTEM_INTERNAL}="1"
ENV{UDISKS_IGNORE}="1"
ENV{UDISKS_AUTO}="0" """

   # Путь для сохранения правила udev
   udev_rule_path = "/etc/udev/rules.d/99-prevent-mount.rules"

   # Запись правила udev в файл
   with open(udev_rule_path, 'w') as f:
      f.write(udev_rule)

   # Запуск команды, чтобы перезагрузить правила udev
   subprocess.run(["udevadm", "control", "--reload"])
   subprocess.run(["udevadm", "trigger"])

   def unmount(disk: Disk):
         # with open('/etc/udisks2/udisks2.conf', 'r') as f:
         #    if 'udisks-daemon-timeout' not in f.read():
         #       # Параметр не задан, добавляем его в файл конфигурации
         #       with open('/etc/udisks2/udisks2.conf', 'a') as f:
         #          f.write('\n[Settings]\nudisks-daemon-timeout=-1\n')
         plist = disk.get_partition_list()
         for item in plist:
            if item.get_fs_uuid() != "" and item.get_fs_mounting_point() != "": # проверяем, что есть фс и она смонтирована куда-то
               try:
                  subprocess.run(["umount", item.get_path()])
                  print(f"Device '{item.get_path()}' has been successfully unmounted.")
                  os.rmdir(f"/mnt/{item.get_fs_uuid()}")
               except subprocess.CalledProcessError as e:
                  print(f"Error: {e}")
               print(f"umount {item.get_path()}") # размонтируем

   while True:
      try:
         di = DiskInfo()
         disks: List[Disk] = di.get_disk_list(sorting=True)
         for disk in disks:
            str_drive = "".join([extract_string(disk.get_serial_number()), extract_string(disk.get_logical_block_size()), extract_string(disk.get_size()*512), extract_string(disk.get_model())])
            m = GOST34112012(bytes(str_drive, "utf-8"), digest_size=256)
            if not db.check(m.hexdigest(),"gost_hash"):
               unmount(disk)
      except Exception as e:
         print(str(e))
      
      time.sleep(3)


elif OS_TYPE == "Windows":
      import wmi
      ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage')

      if not ctypes.windll.shell32.IsUserAnAdmin():
         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

      while True:
         try:
            c = wmi.WMI()
            if disks := c.Win32_DiskDrive():
               for disk in disks:
                  if disk.DefaultBlockSize is None:
                     block_size=512
                  else:
                     block_size=disk.DefaultBlockSize
                     
                  str_drive = "".join([extract_string(disk.SerialNumber), extract_string(block_size), extract_string(disk.Size), extract_string(disk.Model)])
                  m = GOST34112012(bytes(str_drive, "utf-8"), digest_size=256)
                  if not db.check(m.hexdigest(),"gost_hash"):
                     for disk in ws.MSFT_Disk():
                        if not db.check(disk.SerialNumber, "ser_num"):
                           for partition in disk.associators("MSFT_DiskToPartition"):
                              if partition.DriveLetter != 0:
                                 # partition.DiskNumber, partition.PartitionNumber, partition.AccessPaths, chr(partition.DriveLetter), disk.SerialNumber, disk.NumberOfPartitions #DiskNumber постоянный у подключенного накопителя, по нему можно находить те диски которые нужно отключить
                                 partition.RemoveAccessPath(f"{chr(partition.DriveLetter)}:") #удаляем букву у накопителя

         except Exception as e:
            print(str(e))

         time.sleep(3)
