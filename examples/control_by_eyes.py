from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2
import cv2
import pygame
import mouse
import numpy as np
# Initialize gesture engine and video capture

gestures = EyeGestures_v2()
cap = VideoCapture(0)  
calibrate = True

""" pygame.init()
pygame.font.init()
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height= screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height)) """

x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)

xx, yy = np.meshgrid(x, y)

calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map,context="eye_Tracker")
gestures.setClassicalImpact(2)
gestures.setFixation(1.0)

iterator = 0
# Main game loop
running = True
iterator = 0
prev_x = 0
prev_y = 0

# Initialize Pygame
# Set up colors
RED = (255, 0, 100)
BLUE = (100, 0, 255)
GREEN = (0, 255, 0)
BLANK = (0,0,0)
WHITE = (255, 255, 255)

pygame.init()
pygame.font.init()
clock = pygame.time.Clock()

screen = pygame.display.set_mode((1920, 1080))
screen_info = pygame.display.Info()
pygame.display.set_caption("EyeGestures v2 example")
font_size = 48
bold_font = pygame.font.Font(None, font_size)
bold_font.set_bold(True)  # Set the font to bold
screen_width = 1920
screen_height= 1080


# Process each frame
while running:
    # Event handling
    #   Salirse con Ctrl+Q o con X de la ventana del pygame
    for pyevent in pygame.event.get():
        if pyevent.type == pygame.QUIT:
            running = False
        elif pyevent.type == pygame.KEYDOWN:
            if pyevent.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False

    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    if not ret:
        continue
    event, cevent = gestures.step(frame,
        calibrate,
        screen_width,
        screen_height,
        context="eye_Tracker")
    if event is None:
        continue
    frame = np.rot90(frame)
    frame = pygame.surfarray.make_surface(frame)
    frame = pygame.transform.scale(frame, (400, 400))
    frame = np.rot90(frame)
    frame = np.flip(frame, axis=1)
    calibrate = (iterator <= 35) # calibrate 35 points
    screen.fill((0, 0, 0))

    if event:
        cursor_x, cursor_y = event.point[0], event.point[1]
        fixation = event.fixation
        print("X: " +  str(cursor_x))
        print("Y: " + str(cursor_y))
        mouse.move(cursor_x, cursor_y, absolute=True, duration=0.01)
        # calibration_radius: radius for data collection during calibration

    if event is not None or calibration is not None:
        # Display frame on Pygame screen
        screen.blit(frame, (0, 0))
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(f'{event.fixation}', False, (0, 0, 0))
        screen.blit(text_surface, (0,0))
        if calibrate:
            if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
                iterator += 1
                prev_x = calibration.point[0]
                prev_y = calibration.point[1]
            calibration_radius = int(calibration.acceptance_radius) - 7
            fit_point = (int(calibration.point[0]), int(calibration.point[1]))
            pygame.draw.circle(screen, GREEN, fit_point, calibration_radius)
            #   pygame.draw.circle(screen, BLUE, calibration.point, calibration.acceptance_radius)
            text_surface = bold_font.render(f"{iterator}/{25}", True, WHITE)
            text_square = text_surface.get_rect(center=calibration.point)
            screen.blit(text_surface, text_square)
        else:
            cursor_x, cursor_y = event.point[0], event.point[1]
            fixation = event.fixation
            print("X: " +  str(cursor_x))
            print("Y: " + str(cursor_y))
            mouse.move(cursor_x, cursor_y, absolute=True, duration=0.01)
        if gestures.whichAlgorithm(context="eye_Tracker") == "Ridge":
            pygame.draw.circle(screen, RED, event.point, 50)
        if gestures.whichAlgorithm(context="eye_Tracker") == "LassoCV":
            pygame.draw.circle(screen, BLUE, event.point, 50)
        my_font = pygame.font.SysFont('Comic Sans MS', 30)
        text_surface = my_font.render(f'{gestures.whichAlgorithm(context="eye_Tracker")}', False, (0, 0, 0))
        screen.blit(text_surface, event.point)
        
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(120)

pygame.quit()