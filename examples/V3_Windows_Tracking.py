import os
import sys
import time
import warnings
import cv2
import ctypes
import mouse
from eyeGestures import EyeGestures_v3
from eyeGestures.utils import VideoCapture
import numpy as np

context_tag = "eye_Tracker_v3"

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

cap = VideoCapture(0)

# debug info del calibrador cargado
clb = gestures.clb.get(context_tag) if hasattr(gestures,'clb') else None
print("clb keys:", getattr(gestures,'clb',None))
if clb:
    print("fitted:", clb.fitted)
    print("algorithm:", clb.current_algorithm)
    print("len X:", len(clb.X), "len tmp X:", len(clb.__tmp_X) if hasattr(clb,'__tmp_X') else 'n/a')
    print("calib radius, acc radius:", clb.calibration_radius, clb.acceptance_radius)
    print("matrix points:", clb.matrix.points.shape, "iterator:", clb.matrix.iterator)

# ---------- 3-point quick calibration (left-center-right) ----------
def sample_mean_prediction(duration=1.5, max_samples=80):
    samples = []
    t0 = time.time()
    while time.time() - t0 < duration and len(samples) < max_samples:
        ret, frame = cap.read()
        if not ret or frame is None:
            continue
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        evt, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        if evt is not None and evt.point is not None:
            samples.append(evt.point)
    if not samples:
        return None
    return np.mean(np.array(samples), axis=0)

print("\nInicia calibración rápida de 3 puntos para corregir bias/scale.")
print("Sigue instrucciones: mira cada objetivo y pulsa Enter para capturar (o espera la captura automática).")

# puntos objetivo en pantalla (ajusta según preferencia)
left_target   = np.array([int(screen_w*0.10), int(screen_h*0.5)])
center_target = np.array([int(screen_w*0.50), int(screen_h*0.5)])
right_target  = np.array([int(screen_w*0.90), int(screen_h*0.5)])

def capture_point(prompt, target_coord):
    input(f"{prompt} (target en pantalla {target_coord}). Pulsa Enter para empezar captura breve...")
    print("Capturando muestras...")
    mean_pred = sample_mean_prediction(duration=1.8)
    if mean_pred is None:
        raise RuntimeError("No se obtuvieron muestras válidas. Repite en mejor iluminación o estabilidad.")
    print("Mean prediction:", mean_pred)
    return mean_pred

try:
    pred_left = capture_point("Mirar IZQUIERDA", left_target)
    #   pred_left[1] += screen_h
    pred_center = capture_point("Mirar CENTRO", center_target)
    #   pred_center[1] += screen_h
    pred_right = capture_point("Mirar DERECHA", right_target)
    #   pred_right[1] += screen_h
except Exception as e:
    print("Captura fallida:", e)
    pred_left = pred_center = pred_right = None

# calcular escala y offset por eje usando pred_left/center/right
if pred_left is not None:
    # evitar divisiones por 0
    denom_x = (pred_right[0] - pred_left[0]) if (pred_right is not None and pred_left is not None) else 0
    denom_y = (pred_right[1] - pred_left[1]) if (pred_right is not None and pred_left is not None) else 0
    scale_x = (right_target[0] - left_target[0]) / denom_x if denom_x != 0 else 1.0
    scale_y = (right_target[1] - left_target[1]) / denom_y if denom_y != 0 else 1.0
    offset_x = center_target[0] - scale_x * pred_center[0]
    offset_y = center_target[1] - scale_y * pred_center[1]
    print(f"Calibration transform: scale_x={scale_x:.4f}, scale_y={scale_y:.4f}, offset_x={offset_x:.1f}, offset_y={offset_y:.1f}")
else:
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
        evt, _ = gestures.step(frame_rgb, False, screen_w, screen_h, context=context_tag)
        if evt and evt.point is not None:
            raw = np.array(evt.point)
            corrected = np.array([scale_x * raw[0] + offset_x, scale_y * raw[1] + offset_y])
            x, y = int(np.clip(corrected[0], 0, screen_w-1)), int(np.clip(corrected[1], 0, screen_h-1)) 
            # para debug:
            print(f"raw=({int(raw[0])},{int(raw[1])}) -> corrected=({x},{y})")
           
            #   x, y = int(evt.point[0]), int(evt.point[1])
            mouse.move(x, int(evt.point[1]), absolute=True, duration=0.01)

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