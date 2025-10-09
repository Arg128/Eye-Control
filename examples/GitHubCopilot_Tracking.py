# Script headless: carga modelo y mueve el cursor (sin Pygame)
from eyeGestures import EyeGestures_v2
from eyeGestures.utils import VideoCapture
import cv2
import mouse
import os
import ctypes
import numpy as np
import sys
import cv2


context_tag = "eye_Tracker"

# obtener resolución de pantalla en Windows
import ctypes
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

screen_w = 1920
screen_h = 1080

print(f"Resolución de pantalla: {screen_w}x{screen_h}")

MODEL_PATH = os.path.join(os.path.dirname(__file__), ".pkl/calibration_model_eye_tracker.pkl")

gestures = EyeGestures_v2()

# --- ensure context is initialized before loading model or calling step() ---
# Try to call addContext if available, otherwise upload a minimal calibration map
if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
        print("Has entrado aquí jijiiji")
    except Exception:
        # fallback to uploadCalibrationMap
        gestures.uploadCalibrationMap(np.array([[0.5, 0.5]]), context=context_tag)
else:
    gestures.uploadCalibrationMap(np.array([[0.5, 0.5]]), context=context_tag)
    print("Con razon no calibra nada xde")

# intentar cargar modelo guardado
if os.path.exists(MODEL_PATH):
    print(MODEL_PATH)
    with open(MODEL_PATH, "rb") as f:
        data = f.read()
    gestures.loadModel(data, context=context_tag)
else:
    print("No se encontró modelo de calibración. Ejecuta primero GitHubCopilot.py para calibrar.")
    raise SystemExit(1)

cap = VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        # convertir a RGB si la librería lo espera (consistente con calibración)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        event, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        if event:
            x, y = int(event.point[0]), int(event.point[1])
            mouse.move(x, y, absolute=True, duration=0.01)
except KeyboardInterrupt:
    print("Cancelado a travez del teclado")
    pass
except TypeError:
    print("Se ha pausado o anulado los gestos de la cara, cancelando tracking.")
finally:
    try:
        cap.close()  
    except Exception:
        raise Warning("Ni idea gausa")
    print("Tracking finalizado.")
    sys.exit("Salida del todo el programa python")