import wmi
from app.dataBase import Database

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
