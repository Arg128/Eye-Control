from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2
import pygame
import mouse
# Initialize gesture engine and video capture

gestures = EyeGestures_v2()
cap = VideoCapture(0)  
calibrate = True
#   Pygame menu init main
clock = pygame.time.Clock()
""" pygame.init()
pygame.font.init()
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height= screen_info.current_h
screen = pygame.display.set_mode((screen_width, screen_height)) """

pygame.init()
pygame.font.init()
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height= screen_info.current_h

mapa = [[0, 0], [0, 1], [1, 0], [1, 1]]
gestures.uploadCalibrationMap(mapa)


# Process each frame
while True:
  ret, frame = cap.read()
  event, cevent = gestures.step(frame,
    calibrate,
    screen_width,
    screen_height,
    context="my_context")

  if event:
    cursor_x, cursor_y = event.point[0], event.point[1]
    fixation = event.fixation
    print("X: " +  str(cursor_x))
    print("Y: " + str(cursor_y))
    mouse.move(cursor_x, cursor_y, absolute=True, duration=0.2)
    # calibration_radius: radius for data collection during calibration
    clock.tick(120)