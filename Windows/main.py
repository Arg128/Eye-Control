#!/usr/bin/python3.11
import sys, os
import tkinter as tk
from src import EyeControlApp_TK

## Check if running as a frozen exe or a standard script
if getattr(sys, 'frozen', False):
    application_path = os.path.dirname(sys.executable)
    os.chdir('..')
else:
    application_path = os.path.dirname(__file__)

sys.path.append(os.path.dirname(application_path))
sys.path.append((os.path.join(application_path, "src")))
sys.path.append((os.path.join(application_path, "EyeGesturesLite")))
sys.path.append((os.path.join(application_path, "assets")))

the_main = 'main.exe'

config_path = os.path.join(application_path, the_main)
print("Corriendo aplicativo en : " , config_path)

def main():
    EyeControlApp_TK()

if __name__ == "__main__":
    main()