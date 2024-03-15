from tkinter import mainloop
from app import App
import ctypes
import sys

if ctypes.windll.shell32.IsUserAnAdmin():
   if __name__ == "__main__":
      app = App(True)  
         
else:
   app = App(False)  