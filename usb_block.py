# import win32com.client

# def block_usb(serial_number):
#    wmi = win32com.client.GetObject("winmgmts:")
#    usb_devices = wmi.ExecQuery("SELECT * FROM Win32_DiskDrive WHERE InterfaceType='USB'")
   
#    for usb_device in usb_devices:
#       if usb_device.SerialNumber == serial_number:
#          usb_device.Disable() # Блокируем устройство
#          print(f"USB флешка с серийным номером {serial_number} заблокирована")
   
#    print(f"USB флешка с серийным номером {serial_number} не найдена")

# # Применение функции
# serial_number = "001CC0C61241C021341D06A8"  # Замените на нужный серийный номер USB флешки
# block_usb(serial_number)



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


import winreg as reg
import ctypes
import sys

if not ctypes.windll.shell32.IsUserAnAdmin():
   ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "./usb_block.py", None, 1)
else: exit()

key = reg.CreateKey(reg.HKEY_LOCAL_MACHINE, 'SYSTEM\\CurrentControlSet\\Services\\mountmgr')
reg.SetValue(key, 'NoAutoMount', reg.REG_DWORD, '00000001')
reg.CloseKey(key)

import win32file
import winioctlcon

startDisk = win32file.CreateFile(f"\\\\.\\PHYSICALDRIVE1", 
                                 win32file.GENERIC_READ | win32file.GENERIC_WRITE,
                                 win32file.FILE_SHARE_READ |
                                 win32file.FILE_SHARE_WRITE,
                                 None,
                                 win32file.OPEN_EXISTING,
                                 win32file.FILE_ATTRIBUTE_NORMAL,
                                 None)
win32file.DeviceIoControl(startDisk, 
                        winioctlcon.FSCTL_DISMOUNT_VOLUME,
                        None,
                        None)
win32file.DeviceIoControl(startDisk,
                        winioctlcon.FSCTL_LOCK_VOLUME,
                        None,
                        None)

