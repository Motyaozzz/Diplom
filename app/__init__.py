from pygost.gost34112012 import GOST34112012
import ctypes
import sys

from customtkinter import *
from CTkMenuBar import *
from CTkMessagebox import *
from tkinter import ttk

import platform
from typing import List

import cv2
import qrcode

from app.disks import *
from app.dataBase import db

class App():
   
   drives: List[Drive] = []

   selected = None

   drive_tree = None   
   
   
   def __init__(self):
      set_default_color_theme("dark-blue")
      set_appearance_mode("dark")
      
      self.tk = CTk()
      self.OS_TYPE = platform.system()
      
      try:
         if self.OS_TYPE == "Windows":
            if os.system(f'schtasks /query /TN "USB Controller (Matvey)" > nul') == 1:
               os.system(f'python {os.path.dirname(os.path.realpath(__file__))}/add_autostart.py')
            else:
               print("windows service already exists")
               return
            
         elif self.OS_TYPE == "Linux":
            if not (os.path.exists("/etc/systemd/system/USB_Controller_Matvey.service")):
               os.system(f'python {os.path.dirname(os.path.realpath(__file__))}/add_autostart.py')
            else:
               return
      except Exception as e:
         print(e)

      try:
         if self.OS_TYPE == "Windows":
            if ctypes.windll.shell32.IsUserAnAdmin():
               is_admin = True
               self.tk.title("Device monitoring: Administrator")
            else: 
               is_admin = False
               self.tk.title("Device monitoring: User")

         elif self.OS_TYPE == "Linux":
            print("im in init = "+str(os.getuid()))
            if os.geteuid() == 0:
               is_admin = True
               self.tk.title("Device monitoring: Administrator")
            else:
               is_admin = False
               self.tk.title("Device monitoring: User")  

      except Exception as e:
         is_admin = False
         self.tk.title("Device monitoring: Unknown OS user")

      self.is_admin=is_admin
      self.tk.geometry("1000x300")
      self.tk.minsize(1000, 300)
      self.tk.maxsize(1200,500)
      self.__menu()
      self.__init_table()
      self.__update_drives()
      self.tk.mainloop()
      
      
   def __menu(self):
      bg_color = self.tk._apply_appearance_mode(ThemeManager.theme["CTkFrame"]["fg_color"])

      main_menu = CTkMenuBar(self.tk, bg_color=bg_color)
         
      help_menu = main_menu.add_cascade("Справка")

      dropdown1 = CustomDropdownMenu(widget=help_menu)
      dropdown1.add_option(option="Помощь")
      dropdown1.add_separator()
      dropdown1.add_option(option="О программе", command=self.__about)

      self.tk.config(menu=main_menu)

      self.bottom_frame = CTkFrame(self.tk)

      update_button = CTkButton(
         self.bottom_frame, text="Обновить", command=self.__update_drives)
      update_button.pack(side=RIGHT, padx=5)
      
      update_button = CTkButton(
         self.bottom_frame, text="Полная информация о USB", command=self.__full_info)
      update_button.pack(side=RIGHT, padx=5)

      if self.is_admin:
         update_button = CTkButton(
            self.bottom_frame, text="Добавить в базу", command=self.__insert_data)
         update_button.pack(side=RIGHT, padx=5)
         
         update_button = CTkButton(
            self.bottom_frame, text="Удалить из базы", command=self.__delete_data)
         update_button.pack(side=RIGHT, padx=5)
      else:
         update_button = CTkButton(
            self.bottom_frame, text="Перейти адм.консоль", command=self.__make_admin)
         update_button.pack(side=RIGHT, padx=5)         
      
      update_button = CTkButton(
         self.bottom_frame, text="Cоздать QR-код", command=self.__qrcode_make)
      update_button.pack(side=RIGHT, padx=5)
      
      update_button = CTkButton(
         self.bottom_frame, text="Проверить QR-код", command=self.__qrcode_check)
      update_button.pack(side=RIGHT, padx=5)      

      self.bottom_frame.pack(side=BOTTOM, fill=BOTH, padx=5, pady=5)      
      
      
   def __about(self):
      CTkMessagebox(title="О программе", message="Программа учета машинных носителей информации\n(c) Муханов М.Э., Россия, 2024г.")


   def __load_drives(self):
      self.OS_TYPE = platform.system()

      if self.OS_TYPE == "Windows":
         import wmi
         c = wmi.WMI()
         self.drives = []
         if disks := c.Win32_DiskDrive():
            for disk in disks:
               self.drives.append(Drive(disk.Model, disk.Name, disk.InterfaceType, disk.DefaultBlockSize, int(
                  disk.Size), disk.SerialNumber, disk.Index))
      elif self.OS_TYPE == "Linux":
         from diskinfo import Disk, DiskInfo
         di = DiskInfo()
         disks = di.get_disk_list(sorting=True)
         self.drives = []
         for disk in disks:
            if "zram" not in disk.get_path():
               self.drives.append(Drive(disk.get_model(), disk.get_path(), disk.get_type_str(
               ), disk.get_logical_block_size(), int(disk.get_size()*512), disk.get_serial_number(), disk.get_device_id()))
               

   def __init_table(self):

      ###Treeview Customisation (theme colors are selected)
      bg_color = self.tk._apply_appearance_mode(ThemeManager.theme["CTkFrame"]["fg_color"])
      text_color = self.tk._apply_appearance_mode(ThemeManager.theme["CTkLabel"]["text_color"])
      selected_color = self.tk._apply_appearance_mode(ThemeManager.theme["CTkButton"]["fg_color"])

      treestyle = ttk.Style()
      treestyle.theme_use("clam")
      treestyle.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
      treestyle.map('Treeview', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
      treestyle.configure("Treeview.Heading", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0)
      treestyle.map('Treeview.Heading', background=[('selected', bg_color)], foreground=[('selected', selected_color)])
      self.tk.bind("<<TreeviewSelect>>", lambda event: self.tk.focus_set())
      
      # определяем столбцы
      columns = ("index", "name", "type", "capacity", "serial_num", "approved")
      self.drive_tree = ttk.Treeview(
         columns=columns, show="headings", selectmode="browse")
      self.drive_tree.pack(fill=BOTH, expand=1, side=TOP)

      # определяем заголовки
      self.drive_tree.heading("index", text="ID", anchor=W, command=lambda: self.__sort(0, False))
      self.drive_tree.heading("name", text="Имя", anchor=W, command=lambda: self.__sort(1, False))
      self.drive_tree.heading("type", text="Тип", anchor=W, command=lambda: self.__sort(2, False))
      self.drive_tree.heading("capacity", text="Объем", anchor=W, command=lambda: self.__sort(3, False))
      self.drive_tree.heading("serial_num", text="Серийный номер", anchor=W, command=lambda: self.__sort(4, False))
      self.drive_tree.heading("approved", text="Одобренный", anchor=W, command=lambda: self.__sort(5, False))
      

      self.drive_tree.column("#1", stretch=NO, width=60, minwidth=60)
      self.drive_tree.column("#2", stretch=YES, width=250, minwidth=250)
      self.drive_tree.column("#3", stretch=NO, width=60, minwidth=60)
      self.drive_tree.column("#4", stretch=YES, width=100, minwidth=100)
      self.drive_tree.column("#5", stretch=YES, width=250, minwidth=250)
      self.drive_tree.column("#6", stretch=YES, width=150, minwidth=100)
      
      self.drive_tree.bind("<<TreeviewSelect>>", self.__drive_selected)
      self.drive_tree.bind("<Double-Button-1>", lambda event: self.__full_info())

   def __update_drives(self):
      self.drive_tree.delete(*self.drive_tree.get_children())
      self.__load_drives()
      rows = db.get_data_from_database()
      for row in rows:
         self.drive_tree.insert("", END, values=(row[0], row[1], '','', row[2], "Да"))
      for drive in self.drives:
         if not(db.check(drive.serial_num, "ser_num")):
            self.drive_tree.insert("", END, values=(
               drive.index, drive.name, drive.disk_type, self.__human_size(drive.capacity), drive.serial_num, "Нет"))
      self.selected = None


   def __sort(self, col, reverse):
      # получаем все значения столбцов в виде отдельного списка
      l = [(self.drive_tree.set(k, col), k) for k in self.drive_tree.get_children("")]
      # сортируем список
      l.sort(reverse=reverse)
      # переупорядочиваем значения в отсортированном порядке
      for index,  (_, k) in enumerate(l):
         self.drive_tree.move(k, "", index)
      # в следующий раз выполняем сортировку в обратном порядке
      self.drive_tree.heading(col, command=lambda: self.__sort(col, not reverse))
      
      
   def __human_size(self, size):
      units = ['Б', 'КБ', 'МБ', 'ГБ', 'ТБ', 'ПБ']
      for unit in units:
         if size < 1024:
               return f"{size:.1f} {unit}"
         size /= 1024
      
      
   def __drive_selected(self, event):
      for selected_item in self.drive_tree.selection():
         item = self.drive_tree.item(selected_item)
         self.selected = [str(value) for value in item["values"]]
         
         
   def __show_warning(self, text):
      CTkMessagebox(title="Ошибка", message=text)
         
         
         
   def __insert_data(self):

      def extract_string(value):
         if value is None:
            return ""
         return str(value)

      if self.selected is None:
         self.__show_warning("Выберете носитель информации, который хотите добавить в БД")
         return
      
      elif self.selected[4] == 'None':
         self.__show_warning("В базу нельзя добавить носитель без серийного номера")
         return
         #Проверяем, есть ли в базе носитель с таким серийником
      else:
         if db.check(str(self.selected[4]), "ser_num"):
            self.__show_warning("Данный носитель информации уже есть в таблице")
            return
         else:
            for drive in self.drives:
               if self.selected[4] == drive.serial_num:
                  str_drive = "".join([extract_string(drive.serial_num), extract_string(drive.block_size), extract_string(drive.capacity), extract_string(drive.name)])
                  m = GOST34112012(bytes(str_drive, "utf-8"), digest_size=256)
                  name = drive.name
                  ser_num = drive.serial_num

                  db.insert_data(name, ser_num, m.hexdigest())
                  self.__show_warning("Носитель добавлен в базу")

         #Загружаем носители и заносим в базу имя и серийник выбранного носителя
            if self.OS_TYPE == "Windows":
               import wmi
               ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage') # type: ignore
               for disk in ws.MSFT_Disk():
                  if disk.SerialNumber == self.selected[4]:
                     for partition in disk.associators("MSFT_DiskToPartition"):
                        partition.DiskNumber, partition.PartitionNumber, partition.AccessPaths, chr(partition.DriveLetter), disk.SerialNumber, disk.NumberOfPartitions #DiskNumber постоянный у подключенного накопителя, по нему можно находить те диски которые нужно отключить
                        partition.AddAccessPath(None, True) # присваиваем следующую свободную букву

            elif self.OS_TYPE == "Linux":
               from diskinfo import Disk, DiskInfo
               import subprocess

               di = DiskInfo()
               disks: List[Disk] = di.get_disk_list(sorting=True)
               for disk in disks:
                  if self.selected[4] == disk.get_serial_number():
                     plist = disk.get_partition_list() # получаем все разделы на диске
                     for item in plist:
                        if item.get_fs_uuid() != "": # проверяем что раздел имеет uuid, если нет, то не монтируем его, так на нем нет файловой системы
                           os.makedirs(f"/mnt/{item.get_fs_uuid()}", mode=0o777, exist_ok=True)
                           subprocess.run(["sudo", "chmod", "-R", "777", f"/mnt/{item.get_fs_uuid()}"])
                           subprocess.run(["sudo", "mount", item.get_path(), f"/mnt/{item.get_fs_uuid()}"])
                           self.__show_warning(f"Носитель смонтирован в /mnt/{item.get_fs_uuid()}")
      self.__update_drives()
                           
   def __delete_data(self):
      if self.selected is None:
         self.__show_warning("Выберете носитель информации, который хотите удалить из БД")
         return
      else:
         if db.check(self.selected[4], "ser_num"):
            db.delete_data(self.selected[4], "ser_num")
            self.__show_warning("Носитель удален из базы")
            self.__update_drives()
         else:
            self.__show_warning("Такого носителя нет в базе")
            return

         
   def __qrcode_make(self):
      if self.selected is None:
         self.__show_warning("Выберете носитель информации, для которого необходимо создать QR-код")
      else:
            if db.check(self.selected[4], "ser_num"):
               qrcode_img = qrcode.make(self.selected[4])
               qrcode_name = self.selected[1]+".png"
               filename = filedialog.askdirectory()
               if len(filename) == 0:
                  return
               qrcode_path = filename+"/"
               qrcode_img.save(qrcode_path + qrcode_name)
               CTkMessagebox(title="QR-код", message="QR-код создан и размещен по пути:\n" + qrcode_path)
            else:
               self.__show_warning("Невозможно создать QR-код, т.к. данного носителя нет в базе")
               return
      
   def __qrcode_check(self):
      qr_name = filedialog.askopenfilename()
      extensions = ['png', 'jpg', 'jpeg', 'svg']
      qr_png = (qr_name.split('.'))[-1].lower()
      if qr_name !="" and (qr_png in extensions):
         img = cv2.imread(qr_name)
         detect = cv2.QRCodeDetector()
         value, _, _ = detect.detectAndDecode(img)
         if db.check(value, "ser_num"):
            CTkMessagebox(title="QR-код", message="Серийный номер: "+ value)
         else:
            CTkMessagebox(title="QR-код", message="Такого носителя нет в базе")
      else: self.__show_warning("Неверный формат файла или файл не выбран")


   def __make_admin(self):
      self.tk.destroy()
      if self.OS_TYPE == "Windows":
         if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, "./main.py", None, 1)==42:
            exit()
         else:
            App()
      elif self.OS_TYPE == "Linux":
         os.execlp('sudo', 'sudo', sys.executable, *sys.argv)

      
   def __full_info(self):
      self.OS_TYPE = platform.system()

      def make_window_info(substring):
         set_default_color_theme("dark-blue")
         set_appearance_mode("dark")

         window = CTkToplevel()      
         
         window.geometry("800x650")
         window.minsize(800, 650)   
         window.maxsize(800, 650)
         window.title("Полная информация о носителе") 
         
         
         window.textbox = CTkTextbox(master=window, width=800, height=650, corner_radius=0, text_color='white', fg_color="#212121")
         window.textbox.grid(row=0, column=0, sticky="nsew")
         window.textbox.insert("0.0", substring)

      if self.selected is None:
         self.__show_warning("Выберите носитель информации")
         return
      else:
         check = 0
         if self.OS_TYPE == "Windows":
            import wmi
            c=wmi.WMI()
            if items := c.Win32_DiskDrive():
               for item in items:  
                  if self.selected[4] == item.SerialNumber:
                     item = str(item)
                     start = item.find('{') + 1
                     end = item.rfind('}')
                     substring = item[start:end]
                     make_window_info(substring)
                     check = 1                  

         elif self.OS_TYPE == "Linux":
            from diskinfo import Disk, DiskInfo
            di = DiskInfo()
            items = di.get_disk_list(sorting=True)
            for item in items:
               if self.selected[4] == item.get_serial_number():
                  item = str(item)
                  start = item.find('()') + 1
                  end = item.rfind(')')
                  substring = item[start:end]
                  substring = substring.replace(',', '\n')
                  make_window_info(substring)
                  check = 1   
         if check == 0:
            self.__show_warning("Просмотр полной информации возможен только для подключенного носителя")                        