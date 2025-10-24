import os
import sys
import cv2
import warnings

# Suppress pygame and setuptools warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='pygame')
warnings.filterwarnings('ignore', category=UserWarning, module='pygame')

import pygame
import numpy as np
from datetime import datetime

# Suppress pygame support prompt
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("EyeGestures v2 - Professional Eye Tracking Interface")

# Professional fonts
title_font = pygame.font.Font(None, 56)
header_font = pygame.font.Font(None, 42)
body_font = pygame.font.Font(None, 32)
small_font = pygame.font.Font(None, 24)

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2

gestures = EyeGestures_v2()
cap = VideoCapture(0)

x = np.arange(0, 1.1, 0.2)
y = np.arange(0, 1.1, 0.2)

xx, yy = np.meshgrid(x, y)

calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
np.random.shuffle(calibration_map)
gestures.uploadCalibrationMap(calibration_map,context="my_context")
gestures.setClassicalImpact(2)
gestures.setFixation(1.0)

# Professional color scheme
COLOR_PRIMARY = (45, 85, 255)  # Modern blue
COLOR_SECONDARY = (138, 43, 226)  # Purple accent
COLOR_SUCCESS = (34, 197, 94)  # Green
COLOR_WARNING = (251, 191, 36)  # Amber
COLOR_DANGER = (239, 68, 68)  # Red
COLOR_BG_DARK = (17, 24, 39)  # Dark background
COLOR_BG_LIGHT = (31, 41, 55)  # Light background
COLOR_TEXT_PRIMARY = (243, 244, 246)  # Light gray text
COLOR_TEXT_SECONDARY = (156, 163, 175)  # Medium gray text
COLOR_ACCENT = (99, 102, 241)  # Indigo
COLOR_HIGHLIGHT = (236, 72, 153)  # Pink highlight

# Legacy colors for compatibility
RED = COLOR_DANGER
BLUE = COLOR_PRIMARY
GREEN = COLOR_SUCCESS
BLANK = (0, 0, 0)
WHITE = COLOR_TEXT_PRIMARY

def draw_rounded_rect(surface, color, rect, radius=15):
    """Draw a rounded rectangle"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

def draw_progress_bar(surface, x, y, width, height, progress, bg_color, fill_color):
    """Draw a modern progress bar"""
    # Background
    draw_rounded_rect(surface, bg_color, (x, y, width, height), radius=height//2)
    # Fill
    if progress > 0:
        fill_width = int(width * progress)
        draw_rounded_rect(surface, fill_color, (x, y, fill_width, height), radius=height//2)

def draw_panel(surface, x, y, width, height, title=None):
    """Draw a modern panel with optional title"""
    # Shadow effect
    shadow_offset = 5
    draw_rounded_rect(surface, (0, 0, 0, 50), 
                     (x + shadow_offset, y + shadow_offset, width, height), radius=20)
    # Main panel
    draw_rounded_rect(surface, COLOR_BG_LIGHT, (x, y, width, height), radius=20)
    # Border
    pygame.draw.rect(surface, COLOR_ACCENT, (x, y, width, height), 2, border_radius=20)
    
    if title:
        title_surface = header_font.render(title, True, COLOR_TEXT_PRIMARY)
        surface.blit(title_surface, (x + 20, y + 15))
        # Title underline
        pygame.draw.line(surface, COLOR_ACCENT, (x + 20, y + 55), (x + width - 20, y + 55), 2)
    
    return y + (70 if title else 20)

def draw_metric(surface, x, y, label, value, color=COLOR_TEXT_PRIMARY):
    """Draw a metric with label and value"""
    label_surface = small_font.render(label, True, COLOR_TEXT_SECONDARY)
    value_surface = body_font.render(str(value), True, color)
    surface.blit(label_surface, (x, y))
    surface.blit(value_surface, (x, y + 25))

def draw_gaze_indicator(surface, position, size, color, algorithm_name):
    """Draw an enhanced gaze indicator with outer ring and label"""
    # Outer glow ring
    for i in range(3):
        alpha_color = (*color, 100 - i * 30)
        pygame.draw.circle(surface, color, position, size + 10 + i * 5, 2)
    
    # Main circle with gradient effect
    pygame.draw.circle(surface, color, position, size)
    pygame.draw.circle(surface, (255, 255, 255, 180), position, size - 10)
    pygame.draw.circle(surface, color, position, size, 3)
    
    # Center dot
    pygame.draw.circle(surface, WHITE, position, 8)
    
    # Algorithm label with background
    label = body_font.render(algorithm_name, True, WHITE)
    label_bg = pygame.Surface((label.get_width() + 20, label.get_height() + 10))
    label_bg.fill(color)
    label_bg.set_alpha(200)
    
    label_x = position[0] - label.get_width() // 2 - 10
    label_y = position[1] + size + 20
    surface.blit(label_bg, (label_x, label_y))
    surface.blit(label, (label_x + 10, label_y + 5))

clock = pygame.time.Clock()
fps_history = []
start_time = pygame.time.get_ticks()

# Main game loop
running = True
iterator = 0
prev_x = 0
prev_y = 0

while running:
    # Event handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                running = False
            elif event.key == pygame.K_ESCAPE:
                running = False

    # Generate new random position for the cursor
    ret, frame = cap.read()
    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    calibrate = (iterator <= 25)  # calibrate 25 points

    event, calibration = gestures.step(frame, calibrate, screen_width, screen_height, context="my_context")

    if event is None:
        continue

    # Fill background with modern dark color
    screen.fill(COLOR_BG_DARK)
    
    # Calculate FPS
    current_fps = clock.get_fps()
    fps_history.append(current_fps)
    if len(fps_history) > 60:
        fps_history.pop(0)
    avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
    
    # Calculate elapsed time
    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000

    # Prepare camera frame
    frame = np.rot90(frame)
    frame_surface = pygame.surfarray.make_surface(frame)
    frame_surface = pygame.transform.scale(frame_surface, (480, 480))

    if event is not None or calibration is not None:
        # ===== LEFT PANEL: Camera Feed =====
        panel_x = 30
        panel_y = 30
        panel_width = 520
        panel_height = 600
        
        content_y = draw_panel(screen, panel_x, panel_y, panel_width, panel_height, "Live Camera Feed")
        screen.blit(frame_surface, (panel_x + 20, content_y + 10))
        
        # Fixation indicator below camera
        fixation_text = small_font.render(f"Fixation: {event.fixation:.3f}", True, COLOR_TEXT_SECONDARY)
        screen.blit(fixation_text, (panel_x + 20, content_y + 500))
        
        # ===== CENTER PANEL: Calibration Status =====
        center_panel_x = 580
        center_panel_y = 30
        center_panel_width = 400
        center_panel_height = 280
        
        content_y = draw_panel(screen, center_panel_x, center_panel_y, center_panel_width, center_panel_height, 
                              "Calibration" if calibrate else "Tracking Active")
        
        if calibrate:
            # Calibration progress
            progress = iterator / 25
            draw_metric(screen, center_panel_x + 20, content_y + 20, 
                       "Progress", f"{iterator}/25", COLOR_WARNING)
            
            draw_progress_bar(screen, center_panel_x + 20, content_y + 90, 
                            center_panel_width - 40, 30, progress, 
                            COLOR_BG_DARK, COLOR_WARNING)
            
            # Instructions
            instruction = small_font.render("Look at the blue circle", True, COLOR_TEXT_SECONDARY)
            screen.blit(instruction, (center_panel_x + 20, content_y + 140))
            
            # Draw calibration point on main screen
            if calibration.point[0] != prev_x or calibration.point[1] != prev_y:
                iterator += 1
                prev_x = calibration.point[0]
                prev_y = calibration.point[1]
            
            # Animated calibration circle
            time_factor = pygame.time.get_ticks() / 200
            pulse_size = int(5 * np.sin(time_factor))
            pygame.draw.circle(screen, COLOR_PRIMARY, calibration.point, 
                             calibration.acceptance_radius + pulse_size, 3)
            pygame.draw.circle(screen, (255, 255, 255, 100), calibration.point, 15)
            
            # Progress text at calibration point
            progress_surface = title_font.render(f"{iterator}/25", True, WHITE)
            progress_rect = progress_surface.get_rect(center=calibration.point)
            
            # Background for text
            bg_surface = pygame.Surface((progress_rect.width + 20, progress_rect.height + 10))
            bg_surface.fill(COLOR_PRIMARY)
            bg_surface.set_alpha(200)
            screen.blit(bg_surface, (progress_rect.x - 10, progress_rect.y - 5))
            screen.blit(progress_surface, progress_rect)
        else:
            # Tracking mode - show algorithm info
            algorithm = gestures.whichAlgorithm(context="my_context")
            
            draw_metric(screen, center_panel_x + 20, content_y + 20, 
                       "Algorithm", algorithm, COLOR_SUCCESS)
            
            status_text = small_font.render("● Active", True, COLOR_SUCCESS)
            screen.blit(status_text, (center_panel_x + 20, content_y + 90))
            
            # Draw gaze point on main screen
            gaze_color = COLOR_DANGER if algorithm == "Ridge" else COLOR_PRIMARY
            draw_gaze_indicator(screen, event.point, 40, gaze_color, algorithm)
        
        # ===== RIGHT PANEL: System Info =====
        info_panel_x = center_panel_x
        info_panel_y = 340
        info_panel_width = 400
        info_panel_height = 290
        
        content_y = draw_panel(screen, info_panel_x, info_panel_y, info_panel_width, info_panel_height, 
                              "System Information")
        
        # FPS Metric
        fps_color = COLOR_SUCCESS if avg_fps > 50 else COLOR_WARNING if avg_fps > 30 else COLOR_DANGER
        draw_metric(screen, info_panel_x + 20, content_y + 20, "FPS", f"{avg_fps:.1f}", fps_color)
        
        # Elapsed Time
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        draw_metric(screen, info_panel_x + 220, content_y + 20, 
                   "Time", f"{minutes:02d}:{seconds:02d}", COLOR_TEXT_PRIMARY)
        
        # Resolution
        draw_metric(screen, info_panel_x + 20, content_y + 110, 
                   "Resolution", f"{screen_width}x{screen_height}", COLOR_TEXT_PRIMARY)
        
        # Points tracked
        draw_metric(screen, info_panel_x + 220, content_y + 110, 
                   "Points", f"{max(0, iterator - 1)}/25", COLOR_TEXT_PRIMARY)
        
        # ===== TOP BAR: Title and Status =====
        top_bar_x = 1010
        top_bar_y = 30
        top_bar_width = screen_width - top_bar_x - 30
        top_bar_height = 100
        
        draw_rounded_rect(screen, COLOR_BG_LIGHT, (top_bar_x, top_bar_y, top_bar_width, top_bar_height), radius=20)
        pygame.draw.rect(screen, COLOR_ACCENT, (top_bar_x, top_bar_y, top_bar_width, top_bar_height), 2, border_radius=20)
        
        app_title = header_font.render("EyeGestures v2", True, COLOR_PRIMARY)
        screen.blit(app_title, (top_bar_x + 20, top_bar_y + 20))
        
        status = "CALIBRATING" if calibrate else "TRACKING"
        status_color = COLOR_WARNING if calibrate else COLOR_SUCCESS
        status_surface = body_font.render(status, True, status_color)
        screen.blit(status_surface, (top_bar_x + 20, top_bar_y + 60))
        
        # ===== BOTTOM: Instructions =====
        instructions_y = screen_height - 60
        instructions = small_font.render("Press ESC or Ctrl+Q to exit", True, COLOR_TEXT_SECONDARY)
        instructions_rect = instructions.get_rect(center=(screen_width // 2, instructions_y))
        screen.blit(instructions, instructions_rect)
        
    pygame.display.flip()

    # Cap the frame rate
    clock.tick(60)

# Quit Pygame
pygame.quit()
