from pygost.gost34112012 import GOST34112012
import ctypes
import sys
import os   
import time
import customtkinter as ctk
import CTkMenuBar as ctkMBar
import CTkMessagebox as ctkMBox
from tkinter import ttk

import platform
from typing import List

import cv2
import qrcode
   
from app.disks import Drive
from app.dataBase import db

class App():
   
   drives: List[Drive] = []

   selected = None

   drive_tree = None

   def __show_wait_window(self, title: str, message: str) -> None:
      msg_box = ctkMBox.CTkMessagebox(title=title, message=message)
      msg_box.wait_window()

   def __check_admin(self) -> bool:
      if self.OS_TYPE == "Windows":
         return ctypes.windll.shell32.IsUserAnAdmin()
      elif self.OS_TYPE == "Linux":
         return os.geteuid() == 0
      else:
         return False

   def __check_task(self):
      if self.OS_TYPE == "Windows":
         return os.system(f'schtasks /query /TN "Device Controller" > nul') == 0
      if self.OS_TYPE == 'Linux':
         return (os.path.exists("/etc/systemd/system/Device_Controller.service"))
   
   def __add_autostart_task(self):
      if not self.__check_task():
         if self.OS_TYPE == "Windows":
            ctkMBox.CTkMessagebox(title="Добавление задания Windows", message="Задание Device Controller для автоблокировки носителей добавлено")
         elif self.OS_TYPE == "Linux":
            ctkMBox.CTkMessagebox(title="Добавление службы Linux", message="Служба Device_Controller.service для автоблокировки носителей добавлена")
         os.system(f'python {os.path.dirname(os.path.realpath(__file__))}/add_autostart.py')
   
   def __init__(self):
      ctk.set_default_color_theme("dark-blue")
      ctk.set_appearance_mode("dark")
      
      self.tk = ctk.CTk()
      self.OS_TYPE = platform.system()
      self.window_info = None
      
      if not self.__check_task():
         if not self.__check_admin():
            self.__show_wait_window(title="Внимание", message="Войдите под администратором, чтобы добавить задание")
         self.__add_autostart_task()

         time.sleep(5)
         
      if not self.__check_admin() and not self.__check_task():
         os._exit(1)
      
      try:
         if self.OS_TYPE == "Windows":
            if ctypes.windll.shell32.IsUserAnAdmin():
               is_admin = True
               self.tk.title("Device monitoring: Administrator")
            else: 
               is_admin = False
               self.tk.title("Device monitoring: User")

         elif self.OS_TYPE == "Linux":
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
      bg_color = self.tk._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])

      main_menu = ctkMBar.CTkMenuBar(self.tk, bg_color=bg_color)
         
      help_menu = main_menu.add_cascade("Справка")

      dropdown1 = ctkMBar.CustomDropdownMenu(widget=help_menu)
      dropdown1.add_option(option="Помощь")
      dropdown1.add_separator()
      dropdown1.add_option(option="О программе", command=self.__about)

      self.tk.config(menu=main_menu)

      self.bottom_frame = ctk.CTkFrame(self.tk)

      update_button = ctk.CTkButton(
         self.bottom_frame, text="Обновить", command=self.__update_drives)
      update_button.pack(side=ctk.RIGHT, padx=5)
      
      update_button = ctk.CTkButton(
         self.bottom_frame, text="Полная информация о МНИ", command=self.__full_info)
      update_button.pack(side=ctk.RIGHT, padx=5)

      if self.is_admin:
         update_button = ctk.CTkButton(
            self.bottom_frame, text="Добавить в базу", command=self.__insert_data)
         update_button.pack(side=ctk.RIGHT, padx=5)
         
         update_button = ctk.CTkButton(
            self.bottom_frame, text="Удалить из базы", command=self.__delete_data)
         update_button.pack(side=ctk.RIGHT, padx=5)
      else:
         update_button = ctk.CTkButton(
            self.bottom_frame, text="Перейти адм.консоль", command=self.__make_admin)
         update_button.pack(side=ctk.RIGHT, padx=5)         
      
      update_button = ctk.CTkButton(
         self.bottom_frame, text="Cоздать QR-код", command=self.__qrcode_make)
      update_button.pack(side=ctk.RIGHT, padx=5)
      
      update_button = ctk.CTkButton(
         self.bottom_frame, text="Проверить QR-код", command=self.__qrcode_check)
      update_button.pack(side=ctk.RIGHT, padx=5)      

      self.bottom_frame.pack(side=ctk.BOTTOM, fill=ctk.BOTH, padx=5, pady=5)      
      
      
   def __about(self):
      ctkMBox.CTkMessagebox(title="О программе", message="Приложение для автоматизированного учета машинных носителей защищенной информации, их проверки и подготовки бирок для маркировки на предприятии\n(c) Муханов М.Э., Россия, 2024г.")


   def __load_drives(self):
      self.OS_TYPE = platform.system()

      if self.OS_TYPE == "Windows":
         import wmi
         c = wmi.WMI()
         self.drives = []
         
         ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage')
         drives_mt = ws.MSFT_PhysicalDisk()

         if disks := c.Win32_DiskDrive():
            for disk in disks:
               for drive in drives_mt:
                  if disk.Index == int(drive.DeviceId):
                     self.drives.append(Drive(disk.Model, disk.Name, drive.MediaType, disk.DefaultBlockSize, int(
                        disk.Size), disk.SerialNumber, disk.Index, disk.TotalSectors, disk.TotalCylinders))
      elif self.OS_TYPE == "Linux":
         from diskinfo import DiskInfo
         di = DiskInfo()
         disks = di.get_disk_list(sorting=True)
         self.drives = []
         for disk in disks:
            if "zram" not in disk.get_path():
               self.drives.append(Drive(disk.get_model(), disk.get_path(), disk.get_type_str(
               ), disk.get_logical_block_size(), int(disk.get_size()*512), disk.get_serial_number(), disk.get_device_id()))
               # Добавить totalsectors и totalcylinders

   def __init_table(self):

      ###Treeview Customisation (theme colors are selected)
      bg_color = self.tk._apply_appearance_mode(ctk.ThemeManager.theme["CTkFrame"]["fg_color"])
      text_color = self.tk._apply_appearance_mode(ctk.ThemeManager.theme["CTkLabel"]["text_color"])
      selected_color = self.tk._apply_appearance_mode(ctk.ThemeManager.theme["CTkButton"]["fg_color"])

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
      self.drive_tree.pack(fill=ctk.BOTH, expand=1, side=ctk.TOP)

      # определяем заголовки
      self.drive_tree.heading("index", text="ID", anchor=ctk.W, command=lambda: self.__sort(0, False))
      self.drive_tree.heading("name", text="Имя", anchor=ctk.W, command=lambda: self.__sort(1, False))
      self.drive_tree.heading("type", text="Тип", anchor=ctk.W, command=lambda: self.__sort(2, False))
      self.drive_tree.heading("capacity", text="Объем", anchor=ctk.W, command=lambda: self.__sort(3, False))
      self.drive_tree.heading("serial_num", text="Серийный номер", anchor=ctk.W, command=lambda: self.__sort(4, False))
      self.drive_tree.heading("approved", text="Одобренный", anchor=ctk.W, command=lambda: self.__sort(5, False))
      

      self.drive_tree.column("#1", stretch=ctk.NO, width=60, minwidth=60)
      self.drive_tree.column("#2", stretch=ctk.YES, width=250, minwidth=250)
      self.drive_tree.column("#3", stretch=ctk.NO, width=60, minwidth=60)
      self.drive_tree.column("#4", stretch=ctk.YES, width=100, minwidth=100)
      self.drive_tree.column("#5", stretch=ctk.YES, width=250, minwidth=250)
      self.drive_tree.column("#6", stretch=ctk.YES, width=150, minwidth=100)
      
      self.drive_tree.bind("<<TreeviewSelect>>", self.__drive_selected)
      self.drive_tree.bind("<Double-Button-1>", lambda event: self.__full_info())

   def __update_drives(self):
      self.drive_tree.delete(*self.drive_tree.get_children())
      self.__load_drives()
      rows = db.get_data_from_database()
      counter = 1
      for row in rows:
         mem = None
         for drive in self.drives:
            if row[0] == drive.serial_num:
               mem = drive.capacity
         self.drive_tree.insert("", ctk.END, values=(counter, row[1], row[2], self.__human_size(mem) if mem is not None else "Not connected", row[0], "Да"))
         counter+=1
      for drive in self.drives:
         if not(db.check(drive.serial_num, "ser_num")):
            self.drive_tree.insert("", ctk.END, values=(
               counter, drive.name, drive.disk_type, self.__human_size(drive.capacity), drive.serial_num, "Нет"))
            counter+=1
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
      ctkMBox.CTkMessagebox(title="Ошибка", message=text)
         
         
         
   def __insert_data(self):
      def extract_string(value):
         if value is None:
            return ""
         return str(value)
      if self.selected is None:
         self.__show_warning("Выберите носитель информации, который хотите добавить в базу")
         return
      
      elif self.selected[4] == 'None' or self.selected[1] == 'None' or self.selected[2] == 'None':
         self.__show_warning("Устройство неисправно, некоторые параметры не считываются")
         return

      else:
         if db.check(str(self.selected[4]), "ser_num"):
            self.__show_warning("Данный носитель информации уже есть в базе")
            return
         else:
            for drive in self.drives:
               if self.selected[4] == drive.serial_num:
                  str_drive = "".join([extract_string(drive.serial_num), extract_string(drive.block_size), extract_string(drive.capacity), extract_string(drive.name), extract_string(drive.total_sectors), extract_string(drive.total_cylinders)])
                  print(str_drive)
                  m = GOST34112012(bytes(str_drive, "utf-8"), digest_size=256)
                  name = drive.name
                  ser_num = drive.serial_num
                  interface_type = drive.disk_type
                  db.insert_data(ser_num, name, m.hexdigest(), str(interface_type))
                  self.__show_warning("Носитель добавлен в базу")

            if self.OS_TYPE == "Windows":
               import wmi
               ws = wmi.WMI(namespace='root/Microsoft/Windows/Storage') 
               for disk in ws.MSFT_Disk():
                  if disk.SerialNumber == self.selected[4]:
                     for partition in disk.associators("MSFT_DiskToPartition"):
                        partition.DiskNumber, partition.PartitionNumber, partition.AccessPaths, chr(partition.DriveLetter), disk.SerialNumber, disk.NumberOfPartitions
                        partition.AddAccessPath(None, True) 

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
         self.__show_warning("Выберите носитель информации, который хотите удалить из БД")
         return
      else:
         if db.check(self.selected[4], "ser_num"):
            db.delete_data(self.selected[4])
            self.__show_warning("Носитель удален из базы")
            self.__update_drives()
         else:
            self.__show_warning("Такого носителя нет в базе")
            return


         
   def __qrcode_make(self):
      if self.selected is None:
         self.__show_warning("Выберите носитель информации, для которого необходимо создать QR-код")
      else:
            if db.check(self.selected[4], "ser_num"):
               qrcode_img = qrcode.make(self.selected[4])
               qrcode_name = f"{self.selected[1]}({self.selected[4]}).png"
               filename = ctk.filedialog.askdirectory()
               if len(filename) == 0:
                  return
               qrcode_path = filename+"/"
               qrcode_img.save(qrcode_path + qrcode_name)
               ctkMBox.CTkMessagebox(title="QR-код", message="QR-код создан и размещен по пути:\n" + qrcode_path)
            else:
               self.__show_warning("Невозможно создать QR-код. Носителя нет в базе")
               return
      
   def __qrcode_check(self):
      qr_name = ctk.filedialog.askopenfilename()
      extensions = ['png', 'jpg', 'jpeg', 'svg']
      qr_png = (qr_name.split('.'))[-1].lower()
      if qr_name !="" and (qr_png in extensions):
         img = cv2.imread(qr_name)
         detect = cv2.QRCodeDetector()
         value, _, _ = detect.detectAndDecode(img)
         if db.check(value, "ser_num"):
            ctkMBox.CTkMessagebox(title="QR-код", message="Носитель есть в базе")
         else:
            ctkMBox.CTkMessagebox(title="QR-код", message="Такого носителя нет в базе")
      else: self.__show_warning("Неверный формат файла или файл не выбран")


   def __make_admin(self):
      self.tk.destroy()
      if self.OS_TYPE == "Windows":
         if ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f"{os.path.dirname(os.path.realpath(__file__))}/../main.py", None, 1)==42:
            os._exit(1)
         else:
            App()
      elif self.OS_TYPE == "Linux":
         os.execlp('sudo', 'sudo', sys.executable, *sys.argv)

      
   def __full_info(self):
      self.OS_TYPE = platform.system()

      def make_window_info(substring):
         ctk.set_default_color_theme("dark-blue")
         ctk.set_appearance_mode("dark")

         window = ctk.CTkToplevel()
         
         window.geometry("800x650")
         window.minsize(800, 650)   
         window.maxsize(800, 650)
         window.title("Полная информация о носителе") 
         
         
         window.textbox = ctk.CTkTextbox(master=window, width=800, height=650, corner_radius=0, text_color='white', fg_color="#212121")
         window.textbox.grid(row=0, column=0, sticky="nsew")
         window.textbox.insert("0.0", substring)
         return window

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
                     if self.window_info is not None:
                        self.window_info.destroy()
                     self.window_info = make_window_info(substring)
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
                  if self.window_info is not None:
                     self.window_info.destroy()
                  self.window_info = make_window_info(substring)
                  check = 1   
         if check == 0:
            self.__show_warning("Просмотр полной информации возможен только для подключенного носителя")                        