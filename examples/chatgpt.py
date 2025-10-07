import cv2
import time
from eyeGestures import EyeGestures_v2
from eyeGestures.utils import VideoCapture

# Inicializa
gestures = EyeGestures_v2()
cap = VideoCapture(0)

# Resolución de pantalla virtual (puedes ajustar a la real)
WIDTH, HEIGHT = 1280, 720

# Puntos de calibración (normalizados)
calib_points = [
    (0.1, 0.1),  # top-left
    (0.9, 0.1),  # top-right
    (0.5, 0.5),  # center
    (0.1, 0.9),  # bottom-left
    (0.9, 0.9),  # bottom-right
]

# Tiempo a esperar en cada punto
POINT_HOLD_TIME = 2.0

# Fase de calibración
for idx, (nx, ny) in enumerate(calib_points):
    print(f"💡 Mira al punto {idx + 1}/{len(calib_points)}...")

    start = time.time()
    while time.time() - start < POINT_HOLD_TIME:
        ret, frame = cap.read()
        if not ret:
            break

        # Coordenadas reales
        px, py = int(nx * WIDTH), int(ny * HEIGHT)

        # Mostrar punto
        cv2.circle(frame, (px, py), 20, (0, 255, 0), -1)

        # Paso de calibración
        gestures.step(frame, calibrate=True, screen_width=WIDTH, screen_height=HEIGHT)

        cv2.imshow("Calibración", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    print(f"✔ Punto {idx + 1} capturado.")

print("✅ Calibración completada.")
time.sleep(1)

# Seguimiento en tiempo real
while True:
    ret, frame = cap.read()
    if not ret:
        break

    # Estimar mirada
    event, _ = gestures.step(frame, calibrate=False, screen_width=WIDTH, screen_height=HEIGHT)

    if event:
        x, y = int(event.point[0]), int(event.point[1])
        cv2.circle(frame, (x, y), 15, (255, 0, 0), -1)
        cv2.putText(frame, f"Gaze: ({x}, {y})", (30, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

    cv2.imshow("Seguimiento", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()