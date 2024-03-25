import win32com.client

def block_usb(serial_number):
   wmi = win32com.client.GetObject("winmgmts:")
   usb_devices = wmi.ExecQuery("SELECT * FROM Win32_DiskDrive WHERE InterfaceType='USB'")
   
   for usb_device in usb_devices:
      if usb_device.SerialNumber == serial_number:
         usb_device.Disable() # Блокируем устройство
         print(f"USB флешка с серийным номером {serial_number} заблокирована")
   
   print(f"USB флешка с серийным номером {serial_number} не найдена")

# Применение функции
serial_number = "001CC0C61241C021341D06A8"  # Замените на нужный серийный номер USB флешки
block_usb(serial_number)



# import win32com.client
# import os

# def block_usb(serial_number):
#    wmi = win32com.client.GetObject("winmgmts:")
#    usb_devices = wmi.ExecQuery("SELECT * FROM Win32_DiskDrive WHERE InterfaceType='USB'")
   
#    for usb_device in usb_devices:
#       if usb_device.SerialNumber == serial_number:
#          try:
#                for partition in usb_device.associators("Win32_DiskDriveToDiskPartition"):
#                   for logical_disk in partition.associators("Win32_LogicalDiskToPartition"):
#                      logical_disk.DeviceID
#                      os.system(f'wmic partition where DeviceID="{logical_disk.DeviceID}" set NoDefaultDriveLetter=true')  # Удаляем присвоенную букву диска
#                print(f"USB флешка с серийным номером {serial_number} заблокирована")
#          except Exception as e:
#                print(f"Ошибка при блокировке USB флешки: {str(e)}")
#                return

# serial_number = "001CC0C61241C021341D06A8"  # Замените на нужный серийный номер USB флешки
# block_usb(serial_number)  # Блокировка
# # unblock_usb(serial_number)  # Разблокировка
