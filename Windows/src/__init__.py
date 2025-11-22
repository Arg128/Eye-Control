# ...existing code...
import subprocess
import ctypes
import os
import sys
import tkinter as tk
from .settings import Settings
from tkinter import PhotoImage, StringVar, ttk, messagebox
from .dictio import Dictionary
from screeninfo import get_monitors
import math
import shutil
import time
from PIL import ImageTk, Image
import threading
try:
    from PIL import Image, ImageTk
except Exception:
    Image = None
    ImageTk = None

if os.name == "nt":
    user32 = ctypes.windll.user32
    WIDTH = user32.GetSystemMetrics(0)
    HEIGHT = user32.GetSystemMetrics(1)
else:
    monitors = get_monitors()
    for moni in monitors:
        WIDTH = moni.width
        HEIGHT = moni.height
        break

## Check if running as a frozen exe or a standard script
if getattr(sys, 'frozen', False):
    RUNNING_PATH = os.path.dirname(sys.executable)
else:
    RUNNING_PATH = os.path.dirname(__file__)

ASSETS_DIR = os.path.join(RUNNING_PATH, "..", "assets")
ASSETS_DIR2 = os.path.join(RUNNING_PATH, "assets")
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

    def _reset(self):
        self.master.destroy()
        self = EyeControlApp_TK()

    def __init__(self):
        self.settings = Settings()
        self._dictio = Dictionary()
        self.isWindowEnable = False
        self.master = tk.Tk()
        self.node_server = None
        self.win = None
        self.w = int(WIDTH / 2)
        self.h = int(HEIGHT / 1.7) + 210

        #LOAD SETTINGS
        self.load_configuration()
        #LOADING WINDOW
        self.master.withdraw()

        self.master.geometry(f"{self.w}x{self.h}")
        self.master.title("Eye Motion - V2 (Tk)")
        if "nt" == os.name:
            print(os.path.join('../', 'assets', "favicon.ico"))
            self.master.wm_iconbitmap(bitmap = os.path.join('assets', "favicon.ico"))
        else:
            self.master.wm_iconbitmap(bitmap = "@myicon.xbm")

        self.master.configure(bg=self.settings.background_color)
        #Images:
        image = Image.open('./assets/calibrate2.png')
        image = image.resize((70, 70))
        self.calibrate_img = ImageTk.PhotoImage(image)

        image = Image.open('./assets/clickable.png')
        image = image.resize((210, 70))
        self.button_img = ImageTk.PhotoImage(image)

        image = Image.open('./assets/eye-track2.png')
        image = image.resize((105, 70))
        self.eye_track_image = ImageTk.PhotoImage(image)

        image = Image.open('./assets/loading_image.gif')
        image = image.resize((105, 70))
        self.loading_gif = ImageTk.PhotoImage(image)
        # Main layout frame
        main = ttk.Frame(self.master, padding=8)
        main.pack(fill="both", expand=True)

        # Top label
        header = ttk.Label(main, text="Eye Motion", anchor="center", font=("Arial", 20))
        header.pack(fill="x", pady=(0,8))

        # Canvas with background image (if available)
        canvas = tk.Canvas(main, width=self.w, height=int(self.h*0.55), highlightthickness=0)
        self._load_background_on_canvas(canvas, self.w, int(self.h*0.49))
        canvas.pack(fill="both", expand=True, anchor=tk.CENTER)
        useThisFrameToCanvas = tk.Frame(canvas, bg="#181918")
        canvas.create_window(50, 50, window=useThisFrameToCanvas, anchor=tk.CENTER)

        # Buttons frame
        btn_frame = ttk.Frame(main)
        btn_frame.pack(fill="both", expand=True, pady=2)
        #   IMAGES
        placeholder2 = ttk.Label(btn_frame, image=self.eye_track_image, anchor="center")
        placeholder2.grid(row=0, column=0, padx=0, pady=0, sticky="nsew")

        placeholder = ttk.Label(btn_frame, image=self.calibrate_img, anchor="center")
        placeholder.grid(row=0, column=1, padx=0, pady=0, sticky="nsew")

        # Play V2 (tracking)
        btn_play_v2 = ttk.Button(btn_frame, text="Control Suave", command=lambda: self.play(ver="V2"))
        self._dictio.add_object(btn_play_v2)
        btn_play_v2.grid(row=1, column=0, padx=7, pady=2, ipady=12, sticky="ew", rowspan=1)

        btn_calibrate_v2 = ttk.Button(btn_frame, text="Calibrar Suave", command=lambda: self.calibrate(ver="V2"))
        self._dictio.add_object(btn_calibrate_v2)
        btn_calibrate_v2.grid(row=1, column=1, padx=7, pady=2,ipady=12, sticky="ew", rowspan=1)

        # Play V3
        btn_play_v3 = ttk.Button(btn_frame, text="Controlar Rapido", command=lambda: self.play(ver="V3"))
        self._dictio.add_object(btn_play_v3)
        btn_play_v3.grid(row=2, column=0, padx=7, pady=2,ipady=12, sticky="ew", rowspan=1)

        # Calibrate V3 (open calibration script)
        btn_calibrate_v3 = ttk.Button(btn_frame, text="Calibrar Rapido", command=lambda: self.calibrate(ver="V3"))
        self._dictio.add_object(btn_calibrate_v3)
        btn_calibrate_v3.grid(row=2, column=1, padx=7, pady=2,ipady=12, sticky="ew", rowspan=1)
        # Heatmap / Stats
        btn_stats = ttk.Button(btn_frame, text="Data", command=self.generate_stats)
        self._dictio.add_object(btn_stats)
        btn_stats.grid(row=3, column=0, padx=7, pady=4,ipady=12, sticky="ew", rowspan=1)

        # Data export
        btn_galery = ttk.Button(btn_frame, text="Mi Galería", command=self.download_data)
        self._dictio.add_object(btn_galery)
        btn_galery.grid(row=3, column=1, columnspan=1, padx=7, pady=4,ipady=12, sticky="ew")

        # Levantar servidor JS
        btn_data = ttk.Button(btn_frame, text="Probar Juegos", command=self.upgrate_server)
        self._dictio.add_object(btn_data)
        btn_data.grid(row=2, column=3, rowspan=8, padx=7, pady=2,ipady=12, sticky="ew")

        #Settings
        btn_settings = ttk.Button(btn_frame, text="Configuración", command=self.show_configuration)
        self._dictio.add_object(btn_settings)
        btn_settings.grid(row=1, column=3, rowspan=2, padx=7, pady=2,ipady=12, sticky="ew")

        # make columns expand evenly
        btn_frame.columnconfigure(0, weight=3)
        btn_frame.columnconfigure(1, weight=3)
        btn_frame.columnconfigure(2, weight=1)


        # footer
        import sys    
        print("In module products sys.path[0], __package__ ==", sys.path[0], __package__)
        footer = ttk.Label(main, text="Versión: V2-V3 · EyeGestures", anchor="center")
        footer.pack(fill="x", pady=(6,0))

        #   self.translate.translate()
        if self.settings.enable_translation:
            self.master.after(100, self._load_window(self._dictio.translate_acync))

        self.master.deiconify()
        self.master.focus_force()
        self.master.mainloop()
    def sub_menu(self, ver=None):
        if self.isWindowEnable:
            return
        self.isWindowEnable = True
        win = tk.Toplevel(self.master)
        x = math.floor((self.w - (self.w)/2))
        y = math.floor((self.h - (self.h)*0.14))
        win.geometry(f"{x}x{y}")
        win.title("Calibración - Opciones")
        #   crg canll
        win.withdraw()
        elem_1 = ttk.Label(win,text="Aviso:")
        info = tk.Text(win, width=50, height=7, wrap="word")
        info.insert('1.0', '1) Asegúrate de estar en un entorno bien iluminado\n' \
        '2) Mirar directamente a la cámara durante la calibración para obtener mejores resultados.\n' \
        '3) Recomendable no usar ningun accesorio o impedimento en el lugar de los ojos.\n' \
        '4) Asegurarse de tener el rostro durante todo el momento de execución' \
        '\n\nFinalmente teclé \'CTRL\' para salir y mire fijamente la camara para escanear ultimamente su rostro.')
        self._dictio.add_object(info)
        elem_2 = ttk.Label(win,text="Número de puntos:")
        
        self._dictio.add_object(elem_1)
        self._dictio.add_object(elem_2)

        # guardar widget en la instancia para que calibrate_v3_action lo lea
        self.pointsObject = tk.Text(win, width=10, height=1)
        self.pointsObject.insert('1.0', '20')
        self._dictio.add_object(self.pointsObject)

        elem_3 = ttk.Label(win,text="¿Crear nueva calibración?:")
        self.newCalibrationVar = tk.BooleanVar(value=True)
        check_box = ttk.Checkbutton(win, variable=self.newCalibrationVar)
        self._dictio.add_object(elem_3)

        elem_4 = ttk.Label(win,text="Radio de aceptación (px):")
        options = ["70", "210", "400", "700"]
        self._dictio.add_object(elem_4)

        selected_option = StringVar()
        selected_option.set(options[0])  # Set default value
        options.append("70")
        option_menu = ttk.OptionMenu(win, selected_option, *options)

        btn_start_calibration = ttk.Button(win, text="Iniciar calibración", command=lambda: self.calibrate(ver=ver, points=self.pointsObject.get("1.0",'end-1c'), bool=self.newCalibrationVar.get(), radio=selected_option.get()))
        self._dictio.add_object(btn_start_calibration)


        if self.settings.enable_translation:
            self.master.after(100, self._load_window(self._dictio.translate_acync))
        pross = None
        if self.settings.check_face:
            pross = subprocess.Popen(["py", "-3.11", os.path.join(RUNNING_PATH,"face_check.py"), "--show", "--frames","40","--threshold","0.9"], creationflags=subprocess.CREATE_NEW_CONSOLE)

        if pross is not None and pross.wait() == 0 or not self.settings.check_face:
            elem_1.pack(padx=7, pady=7)
            info.pack(padx=7, pady=7)
            elem_2.pack(padx=7, pady=7, side=tk.LEFT)
            self.pointsObject.pack(padx=7, pady=10)
            elem_3.pack(padx=7, pady=7, side=tk.LEFT)
            check_box.pack(padx=7, pady=7)
            elem_4.pack(padx=7, pady=7, side=tk.LEFT)
            option_menu.pack(padx=7, pady=7)
            btn_start_calibration.pack(padx=10, pady=(0,10))
            print("Face check passed. You can proceed to calibration.")
                
            win.deiconify()
            win.focus_force()
            self.master.wait_window(win)    #Avrg
            
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


    def play(self, ver="V2"):
        # face check: run and wait (use sys.executable so the same Python is used)
        face_check_path = os.path.join(RUNNING_PATH, "face_check.py")
        try:
            if not self.settings.check_face:
                return
            cp = subprocess.run([sys.executable, face_check_path, "--show", "--frames", "40", "--threshold", "0.9"], check=False)
            if cp.returncode != 0:
                print("Face check returned non-zero. Continuing but warning: detection may be unstable.")
        except Exception as e:
            print("Could not run face_check.py:", e)
        if ver == "V2":
            run_subprocess(os.path.join(RUNNING_PATH,"V2_Tracking.py"), [str(WIDTH), str(HEIGHT)])
        elif ver == "V3":
            run_subprocess(os.path.join(RUNNING_PATH,"V3_Tracking_2.1.py"), [str(WIDTH), str(HEIGHT)])
        else:
            print("WTH")
        

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

            if not ver == "V2" and not ver == "V3":
                raise NameError().add_note("No version alvariable to: " + ver)
        
            run_subprocess(os.path.join(RUNNING_PATH, f"{ver}_Windows_Calibrate.py"), [str(points), str(bool), str(radio), str(WIDTH), str(HEIGHT)])
            
    def check_face(self):
        pass

    def generate_stats(self):
        """
        Generate stats (heatmap + PDF) and open the Stats folder.
        This launches the Stats/generate_stats.py script (blocks until finished),
        then opens the folder so the user can download PNG/PDF.
        """
        
        stats_dir = os.path.join(RUNNING_PATH)
        print(stats_dir)
        #   os.makedirs(stats_dir, exist_ok=True)
        script_path = os.path.join(stats_dir, "generate_stats.py")
        if not os.path.exists(script_path):
            messagebox.showerror("ERROR", f"No se encontró {script_path}")
            return

        # run generator and wait
        try:
            res = run_subprocess(script_path, argv=["--screen-w", WIDTH, "--screen-h", HEIGHT],
                                  python=True, wait=True)
            if res.returncode == 0:
                # abrir carpeta con resultados
                stats_dir = os.path.join(stats_dir, 'saved', 'output')
                subprocess.Popen(["explorer", stats_dir])
            else:
                messagebox.showwarning("Stats", "La generación de estadísticas devolvió error.")
        except Exception as e:
            messagebox.showerror("Stats", f"Error ejecutando generador: {e}")

    def download_data(self):
        """
        SHOW DATA INTO EYE GESTURES APLICATION.
        """
        stats_dir = os.path.join(RUNNING_PATH, "saved", "output")
        #   os.makedirs(stats_dir, exist_ok=True)
        try:
            subprocess.Popen(["explorer", stats_dir])
        except Exception as e:
            tk.messagebox.showerror("Download", f"No se pudo abrir la carpeta: {e}")

    def upgrate_server(self):
        import psutil
        def close_server(load_win, process):
            process = psutil.Process(process.pid)
            children = process.children(recursive=True)
            for c in children:
                c.terminate()
            if load_win is not None:
                load_win.destroy()
            if process.is_running():
                if os.name == 'nt':
                    process.terminate()
                    print("Why is still running waaaa....")
                    #   print(process)
                else:
                    process.kill()
            
            print("CERRRANDO")
        def running_server(process):
            load_winw = tk.Toplevel(self.master)
            load_winw.title("Server")
            load_winw.geometry("200x80")
            load_winw.protocol("WM_DELETE_WINDOW", lambda: close_server(load_winw, process))
            elem_1 = tk.Label(load_winw, text="Servidor en Marcha", font=("Courier", 21))
            self._dictio.add_object(elem_1)
            elem_1.pack()
            
            info = tk.Text(load_winw, width=50, height=7, wrap="word")
            self._dictio.add_object(info)
            info.pack()
            info.insert('1.0', 'Los juegos se están cargando actualmente. \n' \
            'Si ya no los va a usar porfavor darle al boton de abajo.')
            btn = tk.Button(load_winw, text="Cancelar", font=("Roboto", 14), command=lambda: close_server(load_winw, process))
            self._dictio.add_object(btn)
            btn.pack()

            if self.settings.enable_translation:
                self.master.after(100, self._load_window(self._dictio.translate_acync))
        #   try:
        # build normalized path to EyeGesturesLite directory
        server_dir = os.path.normpath(os.path.join(os.curdir, "EyeGesturesLite"))
        print("Server dir resolved to:", server_dir)
        if not os.path.exists(server_dir) or not os.path.isdir(server_dir):
            tk.messagebox.showerror("Server", f"No se encontró la carpeta del servidor: {server_dir}")
            return

        # check package.json to ensure it's a Node project
        pkg = os.path.join(server_dir, "package.json")
        if not os.path.exists(pkg):
            tk.messagebox.showerror("Server", f"No se encontró package.json en: {server_dir}")
            return
        
        server_dir = fr'{server_dir}'
        print(server_dir)
        #   os.chdir('EyeGesturesLite')
        os.path.abspath(os.curdir)
        os.chdir(RUNNING_PATH)
        os.chdir('..')
        print(os.getcwd())
        os.chdir(os.path.join(os.path.abspath(os.curdir), 'EyeGesturesLite'))
        print(os.getcwd())
        server_dir = os.path.abspath(os.curdir)
        os.chdir('..')
        print(server_dir)
        npm_path = shutil.which("npm") or shutil.which("npm.cmd")
        #   text.pack()
        try:
            loading = self._load_window2()
            process = subprocess.Popen([npm_path, 'start'], cwd=server_dir, shell=False,creationflags=subprocess.CREATE_NEW_CONSOLE)
            loading.destroy()
            running_server(process)
            # Leer la salida en tiempo real
            #   while process.poll() is None:
                
            self.node_server = None
            print("Algo paso?")
        except FileNotFoundError:
            tk.messagebox.showerror("Server", "npm no está disponible en PATH. Instala Node.js y npm.")
        except Exception as e:
            tk.messagebox.showerror("Server", f"No se pudo iniciar el servidor: {e}")

        #   self.node_server.wait()
        print(os.getcwd())
        print("YA ESTA DESTRUIDA")
        #   .destroy()

    def _load_window(self, function):
        from .GifPlayer import GifPlayer
        auxiliar_win = tk.Toplevel()
        auxiliar_win.protocol("WM_DELETE_WINDOW", auxiliar_win.update)
        auxiliar_win.title("Loading")
        auxiliar_win.geometry("400x300")
        loading_img = GifPlayer(auxiliar_win, './assets/loading_image.gif',
                                 width=int((auxiliar_win.winfo_vrootwidth() * 0.3)),    #No sirven estos coeficientes al parecer
                                   height=int((auxiliar_win.winfo_vrootheight()* 0*1)))
        loading_img.pack(pady=7)
        loading_img.start_animation()
        """         process = threading.Thread(target=function, args=(self.master, ), daemon=True)
        process.start()
        while process.is_alive():
            #   self.master.update_idletasks()
            self.master.update()
        process.join() """
        #                   Acyncr. Function
        function(self.master)
        print("DESTROY?")
        auxiliar_win.destroy()

    def _load_window2(self):
        from .GifPlayer import GifPlayer
        auxiliar_win = tk.Toplevel()
        auxiliar_win.protocol("WM_DELETE_WINDOW", auxiliar_win.update)
        auxiliar_win.title("Loading")
        auxiliar_win.geometry("400x300")
        loading_img = GifPlayer(auxiliar_win, './assets/loading_image.gif',
                                 width=int((auxiliar_win.winfo_vrootwidth() * 0.3)),    #No sirven estos coeficientes al parecer
                                   height=int((auxiliar_win.winfo_vrootheight()* 0*1)))
        loading_img.pack(pady=7)
        loading_img.start_animation()
        """         process = threading.Thread(target=function, args=(self.master, ), daemon=True)
        process.start()
        while process.is_alive():
            #   self.master.update_idletasks()
            self.master.update()
        process.join() """
        #                   Acyncr. Function
        return auxiliar_win
        #print("DESTROY?")
        #auxiliar_win.destroy()

    def load_configuration(self):
        data = Settings.load()
        if data is not None:
            self.settings = data

        #   CUSTOM LOADERS
        if self.settings.enable_translation:
            self._dictio.change_language(self.settings.language)
        
        #   self.master.configure(bg=data["background"])
        #   self.enable_checkout = data["checkout"]

    def show_configuration(self):
        if self.isWindowEnable:
            return
        self.isWindowEnable = True
        win = tk.Toplevel(self.master)
        x = math.floor((self.w - (self.w)/2))
        y = math.floor((self.h - (self.h)*0.14))
        win.geometry(f"{x}x{y}")
        win.title("Configuración")
        
        win.withdraw()

        #RECUERDA, SON LOS VALORES QUE TENEMOS QUE IMPORTAR
        #NO LOS TKK
        #   Running options
        elem_1 = ttk.Label(win,text="Opciones de Arranque: ", font=("Franklin Gothic Medium Cond", 14))
        elem_1.pack(padx=7,pady=7)
        self._dictio.add_object(elem_1)
        
        elem_2 = ttk.Label(win,text="Iniciar una nueva calibración: ", justify=tk.LEFT)
        self._dictio.add_object(elem_2)
        nesstedCalibrationVar = tk.BooleanVar(value=True)
        elem_2.pack(padx=7,pady=7)
        ttk.Checkbutton(win, variable=nesstedCalibrationVar).pack(padx=7,pady=7)

        elem_3 = ttk.Label(win,text="Comprobar rostro al probar control: ",  justify=tk.LEFT)
        self._dictio.add_object(elem_3)
        newCalibrationVar = tk.BooleanVar(value=True)
        elem_3.pack(padx=7,pady=7)
        ttk.Checkbutton(win, variable=newCalibrationVar).pack(padx=7,pady=7)

        elem_4 = ttk.Label(win,text="Puntos de Calibración: ",  justify=tk.LEFT)
        self._dictio.add_object(elem_4)
        newCalibrationPoints = tk.IntVar(value=20)
        elem_4.pack(padx=7,pady=7)
        ttk.Entry(win, textvariable=newCalibrationPoints).pack(padx=7,pady=7)

        #   Visual customization settings
        elem_5 = ttk.Label(win,text="Ajustes Visuales: ", font=("Franklin Gothic Medium Cond", 14))
        elem_5.pack(padx=7,pady=7)
        self._dictio.add_object(elem_5)

        elem_6 = ttk.Label(win,text="Traducción Activada: ",  justify=tk.LEFT)
        elem_6.pack(padx=7,pady=7)
        translateVar = tk.BooleanVar(value=True)
        ttk.Checkbutton(win, variable=translateVar).pack(padx=7,pady=7)
        self._dictio.add_object(elem_6)

        elem_7 = ttk.Label(win,text="Traducir al lenguaje: ", justify=tk.LEFT)
        elem_7.pack(padx=7,pady=7)
        languages = self._dictio.translator.get_supported_languages()
        selected_language = StringVar(value=languages[0])
        ttk.OptionMenu(win, selected_language, *languages).pack(padx=7,pady=7)
        self._dictio.add_object(elem_7)

        elem_8 = ttk.Label(win,text="Color de fondo: ", justify=tk.LEFT)
        elem_8.pack(padx=7,pady=7)
        colors = ["red", "blue", "lightblue", "cyan", "lemongreen", "green", "yellow", "black"]
        selected_color = StringVar(value=colors[2])
        ttk.OptionMenu(win, selected_color, *colors).pack(padx=7,pady=7)

        def save_these_things():
            settings_object = Settings()
            settings_object.background_color = selected_color.get()
            settings_object.calibration_points = newCalibrationPoints.get()
            settings_object.check_face = newCalibrationVar.get()
            settings_object.createCalibration = nesstedCalibrationVar.get()
            settings_object.language = selected_language.get()
            settings_object.enable_translation = translateVar.get()
            
            status = settings_object.save()
            print(status)
            if status:
                tk.messagebox.showinfo("Status", OK_MESSAGE)
                self._reset()
            else:
                tk.messagebox.showerror("Status", ERROR_MESSAGE)

        ok_button = ttk.Button(win, text="Guardar los cambios", command=save_these_things)
        self._dictio.add_object(ok_button)
        ok_button.pack(padx=7,pady=7)
        OK_MESSAGE = "El guardado se realizó con exito, reiniciando Eye-Motion"
        ERROR_MESSAGE = "Ups. Algo ocurrio mal, verifique el archivo 'settings.py'"
        self._dictio.add_object(elem_8)

        if self.settings.enable_translation:
            self.master.after(100, self._load_window(self._dictio.translate_acync))
            OK_MESSAGE = self._dictio.add_text(OK_MESSAGE)
            ERROR_MESSAGE = self._dictio.add_text(ERROR_MESSAGE)
            
        win.deiconify()
        win.focus_force()
        self.master.wait_window(win)

        self.isWindowEnable = False
        win.mainloop()
        
        
        


# ...existing code...