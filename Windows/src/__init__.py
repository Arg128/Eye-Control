# ...existing code...
import subprocess
import ctypes
import os
import sys
import tkinter as tk
from tkinter import ttk
import math
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

user32 = ctypes.windll.user32
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "../", "assets")

points = 0

def run_subprocess(path, argv=None, version="3.11"):
    """     try:
        subprocess.Popen([sys.executable, "py -3.11 -m" + path], creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception:
        
        subprocess.Popen([sys.executable, "py -3.11 -m" + path]) """
    if argv != None:
        exe = ["py", f"-{version}", path] + argv
    else:
        exe = ["py", f"-{version}", path]

    print(exe)

    process = subprocess.Popen(exe, creationflags=subprocess.CREATE_NEW_CONSOLE)
"""     stdout, stderr = process.communicate()
    if process.returncode == 0:
        print("Salida del script secundario:", stdout)
    else:
        print("Error:", stderr) """

class EyeControlApp_TK:
    def __init__(self, master):
        self.master = master
        self.w = int(WIDTH / 2)
        self.h = int(HEIGHT / 2) + 40
        master.geometry(f"{self.w}x{self.h}")
        master.title("Eye Motion - V2 (Tk)")

        # Main layout frame
        main = ttk.Frame(master, padding=8)
        main.pack(fill="both", expand=True)

        # Top label
        header = ttk.Label(main, text="Eye Motion", anchor="center", font=("Arial", 20))
        header.pack(fill="x", pady=(0,8))

        # Canvas with background image (if available)
        canvas = tk.Canvas(main, width=self.w, height=int(self.h*0.55), highlightthickness=0)
        self._load_background_on_canvas(canvas, self.w, int(self.h*0.55))
        canvas.pack(fill="both", expand=True, anchor=tk.CENTER)
        useThisFrameToCanvas = tk.Frame(canvas, bg="#0b3c1d")
        canvas.create_window(50, 50, window=useThisFrameToCanvas, anchor="nw")

        # Buttons frame
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="both", expand=True, pady=10)

        # Play V2 (tracking)
        btn_play_v2 = ttk.Button(btn_frame, text="Play V2 (Tracking)", command=self.play_v2)
        btn_play_v2.grid(row=0, column=0, padx=4, pady=6, sticky="ew", rowspan=1)

        # Calibrate V2 (open calibration script)
        btn_calibrate_v2 = ttk.Button(btn_frame, text="Play V2 (Calibrar)", command=self.calibrate_v2)
        btn_calibrate_v2.grid(row=0, column=1, padx=4, pady=6, sticky="ew", rowspan=1)

        # Play V3
        btn_play_v3 = ttk.Button(btn_frame, text="Play V3 (Tracking)", command=self.play_v3)
        btn_play_v3.grid(row=1, column=0, padx=4, pady=6, sticky="ew", rowspan=1)

        # Calibrate V3 (open calibration script)
        btn_calibrate_v3 = ttk.Button(btn_frame, text="Play V3 (Calibrar)", command=self.calibrate_v3)
        btn_calibrate_v3.grid(row=1, column=1, padx=4, pady=6, sticky="ew", rowspan=1)

        # Heatmap / Stats
        btn_stats = ttk.Button(btn_frame, text="Estadisticas", command=self.open_stats)
        btn_stats.grid(row=2, column=0, padx=4, pady=6, sticky="ew", rowspan=1)

        # Data export
        btn_data = ttk.Button(btn_frame, text="Mis Datos", command=self.download_data)
        btn_data.grid(row=2, column=1, columnspan=2, padx=6, pady=6, sticky="ew")

        # make columns expand evenly
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        # footer
        import sys    
        print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
        footer = ttk.Label(main, text="Versión: V2-V3 · EyeGestures", anchor="center")
        footer.pack(fill="x", pady=(6,0))

    def sub_menu(self, Ver=None):
        win = tk.Toplevel(self.master)
        x = math.floor((self.w - (self.w)/2))
        y = math.floor((self.h - (self.h)*0.23))
        win.geometry(f"{x}x{y}")
        win.title("Calibración - Opciones")

        ttk.Label(win,text="Aviso:").pack(padx=7, pady=7)
        info = tk.Text(win, width=50, height=7, wrap="word")
        info.insert('1.0', '1) Asegúrate de estar en un entorno bien iluminado\n2) Mirar directamente a la cámara durante la calibración para obtener mejores resultados.\n3) Recomendable no usar ningun accesorio o impedimento en el lugar de los ojos.\n\nFinalmente teclé \'CTRL + Q\' para salir y mire fijamente la camara para escanear ultimamente su rostro.')
        info.pack(padx=7, pady=7)
        ttk.Label(win,text="Número de puntos:").pack(padx=7, pady=7)

        # guardar widget en la instancia para que calibrate_v3_action lo lea
        self.pointsObject = tk.Text(win, width=10, height=1)
        self.pointsObject.insert('1.0', '20')
        self.pointsObject.pack(padx=7, pady=10)

        ttk.Label(win,text="¿Crear nueva calibración?:").pack(padx=7, pady=7)
        self.newCalibrationVar = tk.BooleanVar(value=True)
        ttk.Checkbutton(win, variable=self.newCalibrationVar).pack(padx=7, pady=7)

        subprocess.Popen(["py", "-3.11", os.path.join(os.path.dirname(__file__),"face_check.py"), "--show", "--frames","40","--threshold","0.9"], creationflags=subprocess.CREATE_NEW_CONSOLE)
        if (Ver == "V2"):
            btn_start_calibration = ttk.Button(win, text="Iniciar calibración", command=lambda: self.calibrate_v2(val=True, win=win))
        elif Ver == "V3":
            btn_start_calibration = ttk.Button(win, text="Iniciar calibración", command=lambda: self.calibrate_v3(val=True, win=win))

        btn_start_calibration.pack(padx=10, pady=(0,10))

        return win

    def _load_background_on_canvas(self, canvas, w, h):
        path = os.path.join(ASSETS_DIR, "aBackground.jpg")
        if Image and os.path.exists(path):
            try:
                img = Image.open(path).convert("RGB")
                img = img.resize((w, h), Image.LANCZOS)
                self.bg_imgtk = ImageTk.PhotoImage(img)
                canvas.create_image(0, 0, anchor="nw", image=self.bg_imgtk)
            except Exception:
                canvas.create_rectangle(0,0,w,h,fill="#0b3c1d")
        else:
            canvas.create_rectangle(0,0,w,h,fill="#0b3c1d")

    # button callbacks
    def play_v2(self):
        # ejecuta V2_Tracking.py en nueva consola
        run_subprocess(os.path.join(os.path.dirname(__file__),"V2_Tracking.py"))

    def play_v3(self):
        # placeholder: ejecutar V3 app si existe
        run_subprocess(os.path.join(os.path.dirname(__file__),"V3_Windows_Tracking.py"))

    def calibrate_v2(self, val=False, win=None):
        # usar Toplevel en vez de crear otra raíz Tk()
        if not win:
            win = self.sub_menu("V2")
        
        if self.pointsObject.get("1.0",'end-1c') and val:
            points = int(self.pointsObject.get("1.0", 'end-1c'))
            bol = self.newCalibrationVar.get()
            win.destroy()
            print(os.path.join(os.path.dirname(__file__), "V2_Windows_Calibrate"))
            run_subprocess(os.path.join(os.path.dirname(__file__), "V2_Windows_Calibrate.py"), [str(points), str(bol)])
            
        win.mainloop()

    def calibrate_v3(self, val=False, win=None):
# usar Toplevel en vez de crear otra raíz Tk()
        if not win:
            win = self.sub_menu("V3")
        
        if self.pointsObject.get("1.0",'end-1c') and val:
            bol = self.newCalibrationVar.get()
            points = int(self.pointsObject.get("1.0", 'end-1c'))
            win.destroy()
            print(os.path.join(os.path.dirname(__file__), "V3_Windows_Calibrate"))
            run_subprocess(os.path.join(os.path.dirname(__file__), "V3_Windows_Calibrate.py"), [str(points), str(bol)])
            
        win.mainloop()

    def check_face(self):
        pass

    def open_stats(self):
        run_subprocess(os.path.join(os.path.dirname(__file__), "Stats", "learn_All_Stats.py"))

    def download_data(self):
        # placeholder para abrir gestor de datos
        run_subprocess("explorer", os.path.join(os.path.dirname(__file__), "Stats"))
    


# ...existing code...