from app.dataBase import Database
import subprocess
import usb




# Fetches the list of all usb devices:
# result = subprocess.run(['devcon', 'hwids', '=usb'], 
#    capture_output=True, text=True)

import wmi
c = wmi.WMI()
if items := c.Win32_DiskDrive():
   for item in items:
      if item.InterfaceType=="USB":
         hwid = item.SerialNumber
         # print(hwid)
         command = f'pnputil /disable-device "{hwid}"'
         # print(command)
         subprocess.run(command, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
         print("USB Root Hub disabled successfully.")
         # subprocess.run(['devcon', 'disable', hwid]) # to disable

# for items in c.Win32_DiskDrive():
#    for item in items:
#       if item.InterfaceType=="USB":
#          print(item)

# subprocess.run(['devcon', 'disable', parsed_hwid]) # to disable
# subprocess.run(['devcon', 'enable', parsed_hwid]) # to enable

