import subprocess
import pyautogui
import time
from keyboard import press

class ProgramHandler():
    def __init__(self, program_name, program_wd) -> None:
        self.name = program_name
        self.program_wd = program_wd
        self.process = None
        self.opened = False
        self.busy = False
    
    def open(self):
        self.process = subprocess.Popen(["cmd", "/c", "start", "/max", self.name], cwd=self.program_wd, shell=True)
        self.opened = True
    
    def click(self, pos):
        print("cliking")
        
        pyautogui.moveTo(pos)
        pyautogui.click()

    def type_and_return(self, msg):
        print("typing")
        pyautogui.typewrite(msg)
        press('enter')
    
    def close(self):
        kill = "TaskKill /IM {} /F".format(self.name + ".exe")
        res = subprocess.run(kill)
        self.opened = False
    
    def is_opened(self):
        return self.opened

