import customtkinter as ctk
from customtkinter import *

class App(ctk.CTk):
   def __init__(self):
      super().__init__()

      self.title("Device monitoring")
      self.geometry("800x300")
      self.minsize(800, 300)
      self.__load_menus()
      self.__init_table()
      self.__update_drives()
      self.mainloop()
      
      set_default_color_theme("dark-blue")
      set_appearance_mode("dark")