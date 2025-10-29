import os
import sys
import time
import warnings
import subprocess
import cv2
import ctypes
import mouse
from eyeGestures import EyeGestures_v3
from eyeGestures.utils import VideoCapture
import numpy as np


prox = subprocess.Popen(["py", "-3.11", os.path.join(os.path.dirname(__file__),"face_check.py"), "--show", "--frames","40","--threshold","0.9"], creationflags=subprocess.CREATE_NEW_CONSOLE)
time.sleep(12)
if prox.returncode != 0:
    print("Face check failed. Exiting.")
    #   sys.exit(1)

context_tag = "eye_Tracker_v3"


from check import ensure_face_present, open_video_source

# screen size
user32 = ctypes.windll.user32
screen_w = user32.GetSystemMetrics(0)
screen_h = user32.GetSystemMetrics(1)

MODEL_PATH = os.path.join(os.path.dirname(__file__), ".pkl", "calibration_model_v3.pkl")
if not os.path.exists(MODEL_PATH):
    print("No model found. Run run_calibration_v3_pygame.py first.")
    sys.exit(1)


gestures = EyeGestures_v3()
# ensure context exists
if hasattr(gestures, "addContext"):
    try:
        gestures.addContext(context_tag)
        print("Contexto añadido correctamente.")
    except Exception:
        pass
else:
    # fallback minimal map
    gestures.uploadCalibrationMap(np.array([[0.5, 0.5]]), context=context_tag)
    print("Fallback")

# load model bytes
with open(MODEL_PATH, "rb") as f:
    data = f.read()
gestures.loadModel(data, context=context_tag)

cap = open_video_source(0)

print("Comprobando rostro antes de tracking...")
ok, frac, dets, tot = ensure_face_present(cap, frames=25, threshold=0.8)
print(f"Face check: {dets}/{tot} -> frac={frac:.2f}")
if not ok:
    print("Advertencia: rostro inestable. El tracking puede fallar.")


scale_x = scale_y = 1.0
offset_x = offset_y = 0.0
print("No se calculó transform. Usando identidad.")

# ---------- Opcional: ejemplo rápido de integración Arduino (comentado) ----------
# Idea: Arduino envía "BTN\n" cuando el usuario pulsa un botón del joystick.
# Puedes leer por serial y usarlo en lugar del input() para capturar.
# from serial import Serial
# ser = Serial('COM3', 115200, timeout=0.1)
# while True:
#     line = ser.readline().decode(errors='ignore').strip()
#     if line == 'BTN':
#         # trigger capture

# ---------- Loop principal de tracking (aplica corrección) ----------

#   scale_x = scale_y = 1.0
#offset_x = offset_y = 0.0
print("No se calculó transform. Usando identidad.")

try:
    print("Iniciando tracking con corrección. Ctrl-C para salir.")
    while True:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_rgb = np.rot90(frame_rgb)
        evt, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        if evt and evt.point is not None:
            raw = np.array(evt.point)
            #   x, y = int(evt.point[0]), int(evt.point[1])
            mouse.move(int(evt.point[0]), int(evt.point[1]), absolute=True, duration=0.01)

        # evitar busy-loop
        time.sleep(0.01)
except KeyboardInterrupt:
    pass
finally:
    # cleanup
    try:
        cap.close()
        sys.exit("Salida del todo el programa python")
        pygame.quit()
    except Exception:
        warnings.warn("No se pudo cerrar de forma correcta")