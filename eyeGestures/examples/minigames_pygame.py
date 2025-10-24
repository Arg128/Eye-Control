"""
EyeGestures Native Pygame Minigames
Collection of native minigames controlled by eye tracking
"""

import os
import sys
import cv2
import warnings
import numpy as np
import random
from enum import Enum

# Suppress pygame and setuptools warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='pygame')
warnings.filterwarnings('ignore', category=UserWarning, module='pygame')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

dir_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(f'{dir_path}/..')

from eyeGestures.utils import VideoCapture
from eyeGestures import EyeGestures_v2

pygame.init()
pygame.font.init()

# Screen setup
screen_info = pygame.display.Info()
SCREEN_WIDTH = screen_info.current_w
SCREEN_HEIGHT = screen_info.current_h
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("EyeGestures - Minijuegos Nativos")

# Fonts
title_font = pygame.font.Font(None, 72)
header_font = pygame.font.Font(None, 48)
body_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Colors
COLOR_PRIMARY = (45, 85, 255)
COLOR_SECONDARY = (138, 43, 226)
COLOR_SUCCESS = (34, 197, 94)
COLOR_WARNING = (251, 191, 36)
COLOR_DANGER = (239, 68, 68)
COLOR_BG_DARK = (17, 24, 39)
COLOR_BG_LIGHT = (31, 41, 55)
COLOR_TEXT_PRIMARY = (243, 244, 246)
COLOR_TEXT_SECONDARY = (156, 163, 175)
COLOR_ACCENT = (99, 102, 241)

def draw_rounded_rect(surface, color, rect, radius=15):
    """Draw a rounded rectangle"""
    pygame.draw.rect(surface, color, rect, border_radius=radius)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3

# Base Game Class
class MiniGame:
    def __init__(self, name, gestures):
        self.name = name
        self.gestures = gestures
        self.score = 0
        self.running = True
        self.state = GameState.PLAYING
    
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        return True
    
    def update(self, gaze_point, fixation):
        pass
    
    def draw(self, screen):
        pass

# 1. Space Shooter Game
class SpaceShooter(MiniGame):
    def __init__(self, gestures):
        super().__init__("Space Shooter", gestures)
        self.player_x = SCREEN_WIDTH // 2
        self.player_y = SCREEN_HEIGHT - 100
        self.player_size = 40
        self.bullets = []
        self.enemies = []
        self.last_shot = 0
        self.last_enemy_spawn = 0
        self.shoot_cooldown = 300
        self.enemy_spawn_rate = 1000
        
    def update(self, gaze_point, fixation):
        if gaze_point:
            self.player_x = gaze_point[0]
        
        # Shoot on fixation
        current_time = pygame.time.get_ticks()
        if fixation > 0.8 and current_time - self.last_shot > self.shoot_cooldown:
            self.bullets.append({
                'x': self.player_x,
                'y': self.player_y - self.player_size,
                'speed': 10
            })
            self.last_shot = current_time
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['y'] -= bullet['speed']
            if bullet['y'] < 0:
                self.bullets.remove(bullet)
        
        # Spawn enemies
        if current_time - self.last_enemy_spawn > self.enemy_spawn_rate:
            self.enemies.append({
                'x': random.randint(50, SCREEN_WIDTH - 50),
                'y': 0,
                'size': 30,
                'speed': random.uniform(2, 5)
            })
            self.last_enemy_spawn = current_time
        
        # Update enemies
        for enemy in self.enemies[:]:
            enemy['y'] += enemy['speed']
            if enemy['y'] > SCREEN_HEIGHT:
                self.enemies.remove(enemy)
                self.score = max(0, self.score - 5)
        
        # Check collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                dx = bullet['x'] - enemy['x']
                dy = bullet['y'] - enemy['y']
                distance = (dx**2 + dy**2)**0.5
                
                if distance < enemy['size']:
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                    self.score += 10
                    break
    
    def draw(self, screen):
        screen.fill(COLOR_BG_DARK)
        
        # Draw stars background
        for i in range(50):
            x = (i * 37) % SCREEN_WIDTH
            y = (i * 73 + pygame.time.get_ticks() // 10) % SCREEN_HEIGHT
            pygame.draw.circle(screen, COLOR_TEXT_SECONDARY, (x, y), 2)
        
        # Draw player
        player_points = [
            (self.player_x, self.player_y - self.player_size),
            (self.player_x - self.player_size, self.player_y + self.player_size),
            (self.player_x + self.player_size, self.player_y + self.player_size)
        ]
        pygame.draw.polygon(screen, COLOR_PRIMARY, player_points)
        pygame.draw.polygon(screen, COLOR_TEXT_PRIMARY, player_points, 3)
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(screen, COLOR_WARNING, (int(bullet['x']), int(bullet['y'])), 5)
        
        # Draw enemies
        for enemy in self.enemies:
            pygame.draw.circle(screen, COLOR_DANGER, (int(enemy['x']), int(enemy['y'])), enemy['size'])
            pygame.draw.circle(screen, COLOR_TEXT_PRIMARY, (int(enemy['x']), int(enemy['y'])), enemy['size'], 2)
        
        # Draw score
        score_text = header_font.render(f"Score: {self.score}", True, COLOR_TEXT_PRIMARY)
        screen.blit(score_text, (20, 20))
        
        # Draw instruction
        instruction = small_font.render("Mueve la nave con tu mirada | Mantén la mirada fija para disparar", True, COLOR_TEXT_SECONDARY)
        screen.blit(instruction, (20, SCREEN_HEIGHT - 40))

# 2. Maze Runner
class MazeRunner(MiniGame):
    def __init__(self, gestures):
        super().__init__("Maze Runner", gestures)
        self.player_x = 100
        self.player_y = SCREEN_HEIGHT // 2
        self.player_radius = 20
        self.speed = 3
        self.walls = []
        self.score = 0
        self.wall_gap = 150
        self.wall_width = 80
        self.generate_walls()
    
    def generate_walls(self):
        for i in range(5):
            gap_y = random.randint(100, SCREEN_HEIGHT - 200)
            wall_x = SCREEN_WIDTH + i * 400
            
            # Top wall
            self.walls.append({
                'x': wall_x,
                'y': 0,
                'width': self.wall_width,
                'height': gap_y,
                'passed': False
            })
            
            # Bottom wall
            self.walls.append({
                'x': wall_x,
                'y': gap_y + self.wall_gap,
                'width': self.wall_width,
                'height': SCREEN_HEIGHT - (gap_y + self.wall_gap),
                'passed': False
            })
    
    def update(self, gaze_point, fixation):
        if gaze_point:
            # Move player towards gaze
            target_y = gaze_point[1]
            if abs(target_y - self.player_y) > self.speed:
                if target_y > self.player_y:
                    self.player_y += self.speed
                else:
                    self.player_y -= self.speed
        
        # Move walls
        for wall in self.walls:
            wall['x'] -= self.speed
            
            # Check if passed
            if not wall['passed'] and wall['x'] + wall['width'] < self.player_x:
                wall['passed'] = True
                self.score += 1
        
        # Remove off-screen walls and generate new ones
        self.walls = [w for w in self.walls if w['x'] > -self.wall_width]
        
        if len(self.walls) < 10:
            gap_y = random.randint(100, SCREEN_HEIGHT - 200)
            wall_x = max([w['x'] for w in self.walls]) + 400
            
            self.walls.append({
                'x': wall_x,
                'y': 0,
                'width': self.wall_width,
                'height': gap_y,
                'passed': False
            })
            
            self.walls.append({
                'x': wall_x,
                'y': gap_y + self.wall_gap,
                'width': self.wall_width,
                'height': SCREEN_HEIGHT - (gap_y + self.wall_gap),
                'passed': False
            })
        
        # Check collisions
        for wall in self.walls:
            if self.check_collision(wall):
                self.state = GameState.GAME_OVER
    
    def check_collision(self, wall):
        if (self.player_x + self.player_radius > wall['x'] and
            self.player_x - self.player_radius < wall['x'] + wall['width']):
            if (self.player_y - self.player_radius < wall['y'] + wall['height'] and
                self.player_y + self.player_radius > wall['y']):
                return True
        return False
    
    def draw(self, screen):
        screen.fill(COLOR_BG_DARK)
        
        # Draw walls
        for wall in self.walls:
            draw_rounded_rect(screen, COLOR_ACCENT, (wall['x'], wall['y'], wall['width'], wall['height']), 10)
        
        # Draw player
        pygame.draw.circle(screen, COLOR_SUCCESS, (int(self.player_x), int(self.player_y)), self.player_radius)
        pygame.draw.circle(screen, COLOR_TEXT_PRIMARY, (int(self.player_x), int(self.player_y)), self.player_radius, 3)
        
        # Draw score
        score_text = header_font.render(f"Score: {self.score}", True, COLOR_TEXT_PRIMARY)
        screen.blit(score_text, (20, 20))
        
        # Draw instruction
        instruction = small_font.render("Mueve la bola con tu mirada | Evita los obstáculos", True, COLOR_TEXT_SECONDARY)
        screen.blit(instruction, (20, SCREEN_HEIGHT - 40))
        
        # Game over
        if self.state == GameState.GAME_OVER:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
            overlay.set_alpha(200)
            overlay.fill(COLOR_BG_DARK)
            screen.blit(overlay, (0, 0))
            
            game_over_text = title_font.render("GAME OVER", True, COLOR_DANGER)
            text_rect = game_over_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
            screen.blit(game_over_text, text_rect)
            
            final_score_text = header_font.render(f"Puntuación Final: {self.score}", True, COLOR_TEXT_PRIMARY)
            score_rect = final_score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            screen.blit(final_score_text, score_rect)

def show_calibration_screen(screen, progress, total):
    """Show calibration progress screen"""
    screen.fill(COLOR_BG_DARK)
    
    # Title
    title = title_font.render("Calibrando Eye Tracking...", True, COLOR_PRIMARY)
    title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(title, title_rect)
    
    # Progress bar
    bar_width = 600
    bar_height = 40
    bar_x = (SCREEN_WIDTH - bar_width) // 2
    bar_y = SCREEN_HEIGHT // 2
    
    # Background bar
    draw_rounded_rect(screen, COLOR_BG_LIGHT, (bar_x, bar_y, bar_width, bar_height), 20)
    
    # Progress bar
    progress_width = int((progress / total) * bar_width)
    if progress_width > 0:
        draw_rounded_rect(screen, COLOR_SUCCESS, (bar_x, bar_y, progress_width, bar_height), 20)
    
    # Progress text
    progress_text = header_font.render(f"{progress}/{total}", True, COLOR_TEXT_PRIMARY)
    progress_rect = progress_text.get_rect(center=(SCREEN_WIDTH // 2, bar_y + bar_height + 50))
    screen.blit(progress_text, progress_rect)
    
    # Instructions
    instructions = [
        "1. Asegúrate de estar frente a la cámara",
        "2. Mantén tu cabeza estable",
        "3. Mira a la cámara naturalmente",
        "4. La calibración es automática..."
    ]
    
    y_offset = SCREEN_HEIGHT // 2 + 150
    for instruction in instructions:
        text = small_font.render(instruction, True, COLOR_TEXT_SECONDARY)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, y_offset))
        screen.blit(text, text_rect)
        y_offset += 35
    
    pygame.display.flip()

def show_error_screen(screen, error_message):
    """Show error screen"""
    screen.fill(COLOR_BG_DARK)
    
    # Error icon
    error_text = title_font.render("⚠️", True, COLOR_DANGER)
    error_rect = error_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 3))
    screen.blit(error_text, error_rect)
    
    # Error message
    message = header_font.render(error_message, True, COLOR_TEXT_PRIMARY)
    message_rect = message.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    screen.blit(message, message_rect)
    
    # Instructions
    instruction = body_font.render("Presiona ESC para salir", True, COLOR_TEXT_SECONDARY)
    instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 80))
    screen.blit(instruction, instruction_rect)
    
    pygame.display.flip()

def main():
    """Main game loop"""
    print("="*60)
    print("Inicializando EyeGestures Minijuegos...")
    print("="*60)
    
    # Initialize eye tracking
    try:
        print("1. Inicializando sistema de eye tracking...")
        gestures = EyeGestures_v2()
        print("   ✓ Eye tracking inicializado")
        
        print("2. Conectando con la cámara...")
        cap = VideoCapture(0)
        
        # Test camera
        ret, test_frame = cap.read()
        if not ret:
            raise Exception("No se pudo acceder a la cámara")
        print("   ✓ Cámara conectada")
        
    except Exception as e:
        print(f"   ✗ Error: {e}")
        print("\nSolución:")
        print("1. Verifica que tu cámara esté conectada")
        print("2. Cierra otras aplicaciones que usen la cámara")
        print("3. Ejecuta: python troubleshooting_camera.py")
        
        # Show error screen
        show_error_screen(screen, "Error: No se detectó cámara")
        
        waiting = True
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    waiting = False
        
        pygame.quit()
        return
    
    print("3. Configurando calibración...")
    x = np.arange(0, 1.1, 0.2)
    y = np.arange(0, 1.1, 0.2)
    xx, yy = np.meshgrid(x, y)
    calibration_map = np.column_stack([xx.ravel(), yy.ravel()])
    np.random.shuffle(calibration_map)
    
    gestures.uploadCalibrationMap(calibration_map, context="pygame_context")
    gestures.setClassicalImpact(2)
    gestures.setFixation(1.0)
    print("   ✓ Calibración configurada")
    
    print("\n4. Calibrando (esto toma ~3 segundos)...")
    
    # Calibration phase
    calibration_frames = 50  # Increased for better accuracy
    calibration_counter = 0
    
    while calibration_counter < calibration_frames:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            event, calibration = gestures.step(frame, True, SCREEN_WIDTH, SCREEN_HEIGHT, context="pygame_context")
            
            if event is not None:
                calibration_counter += 1
                show_calibration_screen(screen, calibration_counter, calibration_frames)
                
                # Check for quit
                for pygame_event in pygame.event.get():
                    if pygame_event.type == pygame.QUIT or (pygame_event.type == pygame.KEYDOWN and pygame_event.key == pygame.K_ESCAPE):
                        cap.release()
                        pygame.quit()
                        return
        else:
            print("   ✗ Error leyendo frame de cámara")
    
    print("   ✓ Calibración completada!")
    print("\n5. Iniciando juego...")
    print("="*60)
    print("\nControles:")
    print("- Mueve tu mirada para controlar el juego")
    print("- ESPACIO: Cambiar de juego")
    print("- ESC: Salir")
    print("="*60)
    
    # Game selection
    games = [SpaceShooter, MazeRunner]
    current_game_index = 0
    current_game = games[current_game_index](gestures)
    
    clock = pygame.time.Clock()
    running = True
    frames_without_detection = 0
    fps_history = []
    
    while running:
        # Get eye tracking data
        ret, frame = cap.read()
        gaze_point = None
        fixation = 0
        
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            eye_event, calibration = gestures.step(frame, False, SCREEN_WIDTH, SCREEN_HEIGHT, context="pygame_context")
            
            if eye_event is not None:
                gaze_point = eye_event.point
                fixation = eye_event.fixation
                frames_without_detection = 0
            else:
                frames_without_detection += 1
        else:
            frames_without_detection += 1
        
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Switch game
                    current_game_index = (current_game_index + 1) % len(games)
                    current_game = games[current_game_index](gestures)
                    print(f"Cambiando a: {current_game.name}")
        
        # Update and draw
        if current_game.state != GameState.GAME_OVER:
            current_game.update(gaze_point, fixation)
        
        current_game.draw(screen)
        
        # Draw gaze indicator
        if gaze_point:
            color = COLOR_SUCCESS if fixation > 0.7 else COLOR_PRIMARY
            pygame.draw.circle(screen, color, (int(gaze_point[0]), int(gaze_point[1])), 15, 3)
            # Draw crosshair
            cross_size = 25
            pygame.draw.line(screen, color, 
                           (int(gaze_point[0]) - cross_size, int(gaze_point[1])),
                           (int(gaze_point[0]) + cross_size, int(gaze_point[1])), 2)
            pygame.draw.line(screen, color,
                           (int(gaze_point[0]), int(gaze_point[1]) - cross_size),
                           (int(gaze_point[0]), int(gaze_point[1]) + cross_size), 2)
        
        # Draw FPS
        current_fps = clock.get_fps()
        fps_history.append(current_fps)
        if len(fps_history) > 30:
            fps_history.pop(0)
        avg_fps = sum(fps_history) / len(fps_history) if fps_history else 0
        
        fps_color = COLOR_SUCCESS if avg_fps > 50 else COLOR_WARNING if avg_fps > 30 else COLOR_DANGER
        fps_text = small_font.render(f"FPS: {avg_fps:.1f}", True, fps_color)
        screen.blit(fps_text, (SCREEN_WIDTH - 120, 20))
        
        # Draw detection warning
        if frames_without_detection > 30:
            warning_text = body_font.render("⚠ No se detectan ojos", True, COLOR_WARNING)
            warning_rect = warning_text.get_rect(center=(SCREEN_WIDTH // 2, 50))
            screen.blit(warning_text, warning_rect)
            
            hint_text = small_font.render("Mira a la cámara", True, COLOR_TEXT_SECONDARY)
            hint_rect = hint_text.get_rect(center=(SCREEN_WIDTH // 2, 85))
            screen.blit(hint_text, hint_rect)
        
        pygame.display.flip()
        clock.tick(60)
    
    print("\nCerrando juego...")
    cap.release()
    pygame.quit()
    print("¡Gracias por jugar!")

if __name__ == "__main__":
    main()
