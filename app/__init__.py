import imp
from customtkinter import *
from CTkMenuBar import *
from CTkMessagebox import *
from tkinter import ttk
import platform
from typing import List

from app.disks import *

class App():
   def __init__(self):
      set_default_color_theme("dark-blue")
      set_appearance_mode("dark")
      
      self.tk = CTk()
      self.tk.title("Device monitoring")
      self.tk.geometry("800x300")
      self.tk.minsize(800, 300)
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

      method_label = CTkLabel(master=self.bottom_frame, text="Метод: ")
      method_label.pack(padx=5, side=RIGHT)

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
      columns = ("index", "name", "type", "capacity", "serial_num")
      self.drive_tree = ttk.Treeview(
         columns=columns, show="headings", selectmode="browse")
      self.drive_tree.pack(fill=BOTH, expand=1, side=TOP)

      # определяем заголовки
      self.drive_tree.heading("index", text="ID", anchor=W, command=lambda: self.__sort(0, False))
      self.drive_tree.heading("name", text="Имя", anchor=W, command=lambda: self.__sort(1, False))
      self.drive_tree.heading("type", text="Тип", anchor=W, command=lambda: self.__sort(2, False))
      self.drive_tree.heading("capacity", text="Объем", anchor=W, command=lambda: self.__sort(3, False))
      self.drive_tree.heading("serial_num", text="Серийный номер", anchor=W, command=lambda: self.__sort(4, False))

      self.drive_tree.column("#1", stretch=NO, width=60, minwidth=60)
      self.drive_tree.column("#2", stretch=YES, width=150, minwidth=120)
      self.drive_tree.column("#3", stretch=NO, width=100, minwidth=100)
      self.drive_tree.column("#4", stretch=YES, width=150, minwidth=100)
      self.drive_tree.column("#5", stretch=YES, width=150, minwidth=100)

      self.drive_tree.bind("<<TreeviewSelect>>", self.__drive_selected)

   def __update_drives(self):
      self.drive_tree.delete(*self.drive_tree.get_children())
      self.__load_drives()
      for drive in self.drives:
         self.drive_tree.insert("", END, values=(
            drive.index, drive.name, drive.disk_type, #self.__human_size(drive.capacity),
            drive.serial_num))
      self.selected = None
      
   def __drive_selected(self, event):
      for selected_item in self.drive_tree.selection():
         item = self.drive_tree.item(selected_item)
         self.selected = item["values"]