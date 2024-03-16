from app.dataBase import Database
import subprocess
import usb


# Fetches the list of all usb devices:
# result = subprocess.run(['devcon', 'hwids', 'usb'], 
#    capture_output=True, text=True)

def locate_usb():
    import win32file
    drive_list = []
    drivebits = win32file.GetLogicalDrives()
    for d in range(1, 26):
        mask = 1 << d
        if drivebits & mask:
            # here if the drive is at least there
            drname='%c:\\' % chr(ord('A') + d)
            t = win32file.GetDriveType(drname)
            if t == win32file.DRIVE_REMOVABLE:
                drive_list.append(drname)
    return drive_list
 

# subprocess.run(['devcon', 'disable', parsed_hwid]) # to disable
# subprocess.run(['devcon', 'enable', parsed_hwid]) # to enable

