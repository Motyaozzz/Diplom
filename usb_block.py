import wmi
from app.dataBase import Database

import win32serviceutil
import win32service
import win32event
import servicemanager
import socket
import sys

class MyService(win32serviceutil.ServiceFramework):
   _svc_name_ = "MyPythonService"
   _svc_display_name_ = "My Python Service"

   def __init__(self, args):
      win32serviceutil.ServiceFramework.__init__(self, args)
      self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
      socket.setdefaulttimeout(60)

   def SvcStop(self):
      self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
      win32event.SetEvent(self.hWaitStop)

   def SvcDoRun(self):
      servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                           servicemanager.PYS_SERVICE_STARTED,
                           (self._svc_name_, ''))
      self.main()

   def main(self):
      ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage')
      db=Database('example.db')
      drives_mt = ws.MSFT_Partition()
      while True:
         for disk in ws.MSFT_Disk():
            if not(db.check(disk.SerialNumber, "ser_num")):
               for partition in disk.associators("MSFT_DiskToPartition"):
                  if partition.DriveLetter != 0:
                     print(partition.DiskNumber, partition.PartitionNumber, partition.AccessPaths, chr(partition.DriveLetter), disk.SerialNumber, disk.NumberOfPartitions) #DiskNumber постоянный у подключенного накопителя, по нему можно находить те диски которые нужно отключить
                     partition.RemoveAccessPath(f"{chr(partition.DriveLetter)}:") #удаляем букву у накопителя
      pass

if __name__ == '__main__':
   if len(sys.argv) == 1:
      servicemanager.Initialize()
      servicemanager.PrepareToHostSingle(MyService)
      servicemanager.StartServiceCtrlDispatcher()
   else:
      win32serviceutil.HandleCommandLine(MyService)
