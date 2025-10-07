import os
import sys
import cv2
import numpy as np
from eyeGestures import EyeGestures_v3


import pygame
# Ajusta si tu repo no está en sys.path 
dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

gestures = EyeGestures_v3(cevent_radius=1000)
cap = cv2.VideoCapture(0)

# Build cevent map (normalizado 0..1)
x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)
xx, yy = np.meshgrid(x, y)
cevent_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(cevent_map)
gestures.uploadceventMap(cevent_map, context="calib")
pygame.init()  
pygame.font.init()
# initialize the pygame window
screen = pygame.display.set_mode((700, 450))
# Ajusta umbral de fijación si quieres
gestures.setFixation(1.0)

width = 1280  # ancho de pantalla donde vas a mapear (ajusta)
height = 720  # alto de pantalla donde vas a mapear (ajusta)

n_points = min(len(cevent_map), 50)
iterator = 0
prev_pt = (0,0)

while True:
    ret, frame = cap.read()
    # El ejemplo usa BGR -> RGB y voltea internamente en getLandmarks/step.
    calibrate = (iterator <= n_points)
    event, cevent = gestures.step(frame, calibrate, width, height, context="calib")

    if event is None:
        continue
    # Mostrar info simple
    if cevent is not None:
        print("Current calib point:", cevent.point, "acc_radius:", cevent.acceptance_radius)
        if calibrate:
            if cevent.point[0] != prev_pt[0] or cevent.point[1] != prev_pt[1]:
                iterator += 1
                prev_pt = (cevent.point[0], cevent.point[1])
                print("Progress:", iterator, "/", n_points)

        if event is not None or cevent is not None:
            # Display frame on Pygame screen
            screen.blit(frame, (0, 0))
            my_font = pygame.font.SysFont('Comic Sans MS', 30)
            text_surface = my_font.render(f'{event.fixation}', False, (0, 0, 0))
            screen.blit(text_surface, (0,0))
            if calibrate:
                if cevent.point[0] != prev_x or cevent.point[1] != prev_y:
                    iterator += 1
                    prev_x = cevent.point[0]
                    prev_y = cevent.point[1]
                # pygame.draw.circle(screen, GREEN, fit_point, cevent_radius)
                pygame.draw.circle(screen, BLUE, cevent.point, cevent.acceptance_radius)
                text_surface = bold_font.render(f"{iterator}/{25}", True, WHITE)
                text_square = text_surface.get_rect(center=cevent.point)
                screen.blit(text_surface, text_square)
            else:
                pass
            if gestures.whichAlgorithm(context="my_context") == "Ridge":
                pygame.draw.circle(screen, RED, event.point, 50)
            if gestures.whichAlgorithm(context="my_context") == "LassoCV":
                pygame.draw.circle(screen, BLUE, event.point, 50)
            my_font = pygame.font.SysFont('Comic Sans MS', 30)
            text_surface = my_font.render(f'{gestures.whichAlgorithm(context="my_context")}', False, (0, 0, 0))
            screen.blit(text_surface, event.point)
    # Puedes agregar una tecla para salir
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Guardar modelo
model_bytes = gestures.saveModel(context="calib")
if model_bytes:
    with open("cevent_model.pkl", "wb") as f:
        f.write(model_bytes)
    print("Modelo guardado en cevent_model.pkl")
else:
    print("No se generó modelo para guardar.")

cap.release()
cv2.destroyAllWindows()
pygame.quit()