# ...existing code...
import subprocess
import ctypes
import os
import sys
import tkinter as tk
from tkinter import PhotoImage, StringVar, ttk, messagebox
import math
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

user32 = ctypes.windll.user32
WIDTH = user32.GetSystemMetrics(0)
HEIGHT = user32.GetSystemMetrics(1)

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "..", "assets")
ASSETS_DIR2 = os.path.join(os.path.dirname(__file__), "assets")
points = 0

def run_subprocess2(path, argv=None, version="3.11"):
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

def run_subprocess(path, argv=None, python=True, wait=False):
    """
    Run a subprocess.
    - If python=True, runs [sys.executable, path, *argv].
    - If python=False and path is list/str, runs it directly (useful for explorer).
    - If wait=True, blocks until completion and returns CompletedProcess.
    """
    if python:
        cmd = [sys.executable, path]
        if argv:
            cmd += list(map(str, argv))
    else:
        # allow path to be a list or string
        if isinstance(path, (list, tuple)):
            cmd = list(path)
            if argv:
                cmd += list(map(str, argv))
        else:
            cmd = [path] + (list(map(str, argv)) if argv else [])

    print("Running:", cmd)
    try:
        if wait:
            return subprocess.run(cmd, check=False)
        else:
            return subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    except Exception as e:
        print("Failed to spawn process:", e)
        raise

class EyeControlApp_TK:
    def __init__(self, master):
        self.isWindowEnable = False
        self.master = master
        self.win = None
        self.w = int(WIDTH / 2)
        self.h = int(HEIGHT / 2) + 140
        master.geometry(f"{self.w}x{self.h}")
        master.title("Eye Motion - V2 (Tk)")
        if "nt" == os.name:
            print(os.path.join('../', 'assets', "favicon.ico"))
            master.wm_iconbitmap(bitmap = os.path.join('assets', "favicon.ico"))
        else:
            master.wm_iconbitmap(bitmap = "@myicon.xbm")

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
        btn_calibrate_v2 = ttk.Button(btn_frame, text="Play V2 (Calibrar)", command=lambda: self.calibrate(ver="V2"))
        btn_calibrate_v2.grid(row=0, column=1, padx=4, pady=6, sticky="ew", rowspan=1)

        # Play V3
        btn_play_v3 = ttk.Button(btn_frame, text="Play V3 (Tracking)", command=self.play_v3)
        btn_play_v3.grid(row=1, column=0, padx=4, pady=6, sticky="ew", rowspan=1)

        # Calibrate V3 (open calibration script)
        btn_calibrate_v3 = ttk.Button(btn_frame, text="Play V3 (Calibrar)", command=lambda: self.calibrate(ver="V3"))
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

    def sub_menu(self, ver=None):
        if self.isWindowEnable:
            return
        self.isWindowEnable = True
        win = tk.Toplevel(self.master)
        x = math.floor((self.w - (self.w)/2))
        y = math.floor((self.h - (self.h)*0.23))
        win.geometry(f"{x}x{y}")
        win.title("Calibración - Opciones")

        elem_1 = ttk.Label(win,text="Aviso:")
        info = tk.Text(win, width=50, height=7, wrap="word")
        info.insert('1.0', '1) Asegúrate de estar en un entorno bien iluminado\n' \
        '2) Mirar directamente a la cámara durante la calibración para obtener mejores resultados.\n' \
        '3) Recomendable no usar ningun accesorio o impedimento en el lugar de los ojos.\n' \
        '4) Asegurarse de tener el rostro durante todo el momento de execución' \
        '\n\nFinalmente teclé \'CTRL\' para salir y mire fijamente la camara para escanear ultimamente su rostro.')
        elem_2 = ttk.Label(win,text="Número de puntos:")

        # guardar widget en la instancia para que calibrate_v3_action lo lea
        self.pointsObject = tk.Text(win, width=10, height=1)
        self.pointsObject.insert('1.0', '20')

        elem_3 = ttk.Label(win,text="¿Crear nueva calibración?:")
        self.newCalibrationVar = tk.BooleanVar(value=True)
        check_box = ttk.Checkbutton(win, variable=self.newCalibrationVar)

        elem_4 = ttk.Label(win,text="Radio de aceptación (px):")
        options = ["70", "210", "400", "700"]

        selected_option = StringVar()
        selected_option.set(options[0])  # Set default value

        option_menu = ttk.OptionMenu(win, selected_option, *options)

        btn_start_calibration = ttk.Button(win, text="Iniciar calibración", command=lambda: self.calibrate(ver=ver, points=self.pointsObject.get("1.0",'end-1c'), bool=self.newCalibrationVar.get(), radio=selected_option.get()))
        pross = subprocess.Popen(["py", "-3.11", os.path.join(os.path.dirname(__file__),"face_check.py"), "--show", "--frames","40","--threshold","0.9"], creationflags=subprocess.CREATE_NEW_CONSOLE)

        if pross.wait() == 0:
            elem_1.pack(padx=7, pady=7)
            info.pack(padx=7, pady=7)
            elem_2.pack(padx=7, pady=7)
            self.pointsObject.pack(padx=7, pady=10)
            elem_3.pack(padx=7, pady=7)
            check_box.pack(padx=7, pady=7)
            elem_4.pack(padx=7, pady=7)
            option_menu.pack(padx=7, pady=7)
            btn_start_calibration.pack(padx=10, pady=(0,10))
            print("Face check passed. You can proceed to calibration.")

            self.master.wait_window(win)

            self.isWindowEnable = False
            win.mainloop()
            return win
        else:  
            win.title("ERROR INESPERADO")
            ttk.Label(win,text="Por favor contantarse conmigo").pack(padx=7, pady=7)
            print("Ocurrio un error inesperado, por favor siga los requerimientos")
            self.isWindowEnable = False
            return


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
        run_subprocess(os.path.join(os.path.dirname(__file__),"V3_Windows_Tracking_2.1.py"))

    def calibrate(self, ver=None, points=None, bool=None, radio=None):
        # usar Toplevel en vez de crear otra raíz Tk()
        if points is None and bool is None and radio is None:
            if not self.isWindowEnable:
                self.sub_menu(ver=ver)
        else:
            if int(radio) < 70:
                radio = 70
            
            try:
                points = int(points)
            except ValueError:
                points = 20
            if int(points) < 0:
                points = 0

            if ver == "V2":
                run_subprocess(os.path.join(os.path.dirname(__file__), "V2_Windows_Calibrate.py"), [str(points), str(bool), str(radio)])
            elif ver == "V3":
                run_subprocess(os.path.join(os.path.dirname(__file__), "V3_Windows_Calibrate.py"), [str(points), str(bool), str(radio)])
            
    def check_face(self):
        pass

    def open_stats(self):
        """
        Generate stats (heatmap + PDF) and open the Stats folder.
        This launches the Stats/generate_stats.py script (blocks until finished),
        then opens the folder so the user can download PNG/PDF.
        """
        stats_dir = os.path.join(os.path.dirname(__file__), "Stats")
        os.makedirs(stats_dir, exist_ok=True)
        script_path = os.path.join(stats_dir, "generate_stats.py")
        if not os.path.exists(script_path):
            messagebox.showerror("Stats", f"No se encontró {script_path}")
            return

        # run generator and wait
        try:
            res = run_subprocess(script_path, argv=None, python=True, wait=True)
            if res.returncode == 0:
                # abrir carpeta con resultados
                subprocess.Popen(["explorer", stats_dir])
            else:
                messagebox.showwarning("Stats", "La generación de estadísticas devolvió error.")
        except Exception as e:
            messagebox.showerror("Stats", f"Error ejecutando generador: {e}")

    def download_data(self):
        """
        Open the Stats folder in Explorer so user can copy/download PNG/PDF.
        """
        stats_dir = os.path.join(os.path.dirname(__file__), "Stats")
        os.makedirs(stats_dir, exist_ok=True)
        try:
            subprocess.Popen(["explorer", stats_dir])
        except Exception as e:
            tk.messagebox.showerror("Download", f"No se pudo abrir la carpeta: {e}")


# ...existing code...