import wmi
from app.dataBase import db, work_dir
from pygost.gost34112012 import GOST34112012
import ctypes
import sys
import time
   
ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage')

# def run_as_admin():
#    if not ctypes.windll.shell32.IsUserAnAdmin():
#       ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)

# run_as_admin()

def extract_string(value):
   if value is None:
      return ""
   return str(value)

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

   time.sleep(1)
