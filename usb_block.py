import wmi

ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage')
drives_mt = ws.MSFT_Partition()
for disk in ws.MSFT_Disk():
   if disk.SerialNumber == "AA04012700028260":
      for partition in disk.associators("MSFT_DiskToPartition"):
         print(partition.DiskNumber, partition.PartitionNumber, partition.AccessPaths, chr(partition.DriveLetter), disk.SerialNumber, disk.NumberOfPartitions) #DiskNumber постоянный у подключенного накопителя, по нему можно находить те диски которые нужно отключить
         input("Введите любой символ чтобы размонтировать... ")
         partition.RemoveAccessPath(f"{chr(partition.DriveLetter)}:") #удаляем букву у накопителя
         input("Введите любой символ чтобы примонтировать... ")
         partition.AddAccessPath(None, True) # присваиваем следующую свободную букву