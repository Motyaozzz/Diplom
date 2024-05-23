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

   udev_rule = """ACTION=="add"
KERNEL=="sd[b-z]*"
ENV{UDISKS_PRESENTATION_HIDE}="1"
ENV{UDISKS_PRESENTATION_NOPOLICY}="1"
ENV{UDISKS_AUTOMOUNT_HINT}="never"
ENV{UDISKS_SYSTEM_INTERNAL}="1"
ENV{UDISKS_IGNORE}="1"
ENV{UDISKS_AUTO}="0" """

   udev_rule_path = "/etc/udev/rules.d/99-prevent-mount.rules"

   with open(udev_rule_path, 'w') as f:
      f.write(udev_rule)

   subprocess.run(["udevadm", "control", "--reload"])
   subprocess.run(["udevadm", "trigger"])

   def mount(disk: Disk):
      plist = disk.get_partition_list()
      for item in plist:
         if item.get_fs_uuid() != "" and item.get_fs_mounting_point() == "":
               if os.path.ismount(f"/mnt/{item.get_fs_uuid()}"):
                  subprocess.run(["sudo", "umount", f"/mnt/{item.get_fs_uuid()}"])                              
               subprocess.run(["sudo", "mount", item.get_path(), f"/mnt/{item.get_fs_uuid()}"])

   def unmount(disk: Disk):
         plist = disk.get_partition_list()
         for item in plist:
            if item.get_fs_uuid() != "" and item.get_fs_mounting_point() != "": # проверяем, что есть фс и она смонтирована куда-то
                  subprocess.run(["sudo", "umount", item.get_path()])
                  subprocess.run(["sudo", "rm", "-rf", f"/mnt/{item.get_fs_uuid()}"])

   while True:
      di = DiskInfo()
      disks: List[Disk] = di.get_disk_list(sorting=True)
      for disk in disks:
         str_drive = "".join([extract_string(disk.get_serial_number()), extract_string(disk.get_logical_block_size()), extract_string(disk.get_size()*512), extract_string(disk.get_model())])
         m = GOST34112012(bytes(str_drive, "utf-8"), digest_size=256)
         if not db.check(m.hexdigest(),"hash"):
            unmount(disk)
         else:
            mount(disk)
      time.sleep(3)

elif OS_TYPE == "Windows":
      import wmi
      ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage')
      
      if not ctypes.windll.shell32.IsUserAnAdmin():
         ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
         
      while True:
         c = wmi.WMI()
         if disks := c.Win32_DiskDrive():
            block_size = 512
            for disk in disks:
               str_drive = "".join([extract_string(disk.SerialNumber), extract_string(block_size), extract_string(disk.Size), extract_string(disk.Model), extract_string(disk.TotalSectors), extract_string(disk.TotalCylinders)])
               print("str_device block: "+ str_drive)
               m = GOST34112012(bytes(str_drive, "utf-8"), digest_size=256)
               print(m.hexdigest())
               if not db.check(m.hexdigest(),"hash"):
                  for disk in ws.MSFT_Disk():
                     if not db.check(disk.SerialNumber, "ser_num"):
                        for partition in disk.associators("MSFT_DiskToPartition"):
                           if partition.DriveLetter != 0:
                              partition.RemoveAccessPath(f"{chr(partition.DriveLetter)}:")
         time.sleep(2)