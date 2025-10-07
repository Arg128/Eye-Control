# Script headless: carga modelo y mueve el cursor (sin Pygame)
from eyeGestures import EyeGestures_v2
from eyeGestures.utils import VideoCapture
import cv2
import mouse
import os
import ctypes

# obtener resolución de pantalla en Windows
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

MODEL_PATH = os.path.join(os.path.dirname(__file__), "calibration_model_eye_tracker.pkl")

gestures = EyeGestures_v2()
# intentar cargar modelo guardado
if os.path.exists(MODEL_PATH):
    with open(MODEL_PATH, "rb") as f:
        data = f.read()
    gestures.loadModel(data, context="eye_Tracker")
else:
    print("No se encontró modelo de calibración. Ejecuta primero control_by_eyes.py para calibrar.")
    raise SystemExit(1)

cap = VideoCapture(0)

try:
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        # convertir a RGB si la librería lo espera (consistente con calibración)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        event, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context="eye_Tracker")
        if event:
            x, y = int(event.point[0]), int(event.point[1])
            mouse.move(x, y, absolute=True, duration=0.01)
except KeyboardInterrupt:
    pass
finally:
    try:
        cap.release()
    except Exception:
        pass
    print("Tracking finalizado.")