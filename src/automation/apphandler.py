from __future__ import annotations
import subprocess
import pyautogui
import time
from keyboard import press
from win32 import win32gui
from utils.math import sum_tuples
import win32process as wproc
import win32api as wapi


class AppHandler():
    def __init__(self, program_name, program_wd) -> None:
        self.name = program_name
        self.program_wd = program_wd
        self.process = None
        self.opened = False
        self.busy = False

    def open(self):
        self.process = subprocess.Popen(["cmd", "/c", "start", "/max", self.name], cwd=self.program_wd, shell=True)
        self.opened = True

    def get_window(self, window_name:str) -> AppHandler.Window:
        return AppHandler.Window(window_name)
    
    def close(self):
        kill = "TaskKill /IM {} /F".format(self.name + ".exe")
        res = subprocess.run(kill)
        self.opened = False
    
    def is_opened(self):
        return self.opened
    
    class Window:
        def __init__(self, name) -> None:
            self.name = name
        
        @property
        def _handler(self):
            try:
                return win32gui.FindWindow(None, self.name)
            except:
                raise Exception(f"window with the name {self.name} was not found")

        @property
        def position(self):
            rect = win32gui.GetWindowRect(self._handler)
            x = rect[0]
            y = rect[1]
            return x, y
        
        def click(self, relative_position):
            position = sum_tuples([relative_position, self.position])
            pyautogui.click(position)
        
        def type_and_return(self, msg):

            pyautogui.typewrite(msg)
            press('enter')
        


