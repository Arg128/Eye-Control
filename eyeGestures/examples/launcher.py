"""
EyeGestures Professional Launcher
Main menu interface for accessing all EyeGestures features and minigames
"""

import os
import sys
import warnings
import subprocess
from enum import Enum

# Suppress pygame and setuptools warnings
warnings.filterwarnings('ignore', category=RuntimeWarning, module='pygame')
warnings.filterwarnings('ignore', category=UserWarning, module='pygame')
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = '1'

import pygame

pygame.init()
pygame.font.init()

# Get the display dimensions
screen_info = pygame.display.Info()
screen_width = screen_info.current_w
screen_height = screen_info.current_h

# Set up the screen
WINDOW_WIDTH = 1200
WINDOW_HEIGHT = 800
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("EyeGestures - Professional Launcher")

# Professional fonts
title_font = pygame.font.Font(None, 72)
subtitle_font = pygame.font.Font(None, 42)
menu_font = pygame.font.Font(None, 38)
small_font = pygame.font.Font(None, 24)

# Professional color scheme
COLOR_PRIMARY = (45, 85, 255)  # Modern blue
COLOR_SECONDARY = (138, 43, 226)  # Purple accent
COLOR_SUCCESS = (34, 197, 94)  # Green
COLOR_WARNING = (251, 191, 36)  # Amber
COLOR_DANGER = (239, 68, 68)  # Red
COLOR_BG_DARK = (17, 24, 39)  # Dark background
COLOR_BG_LIGHT = (31, 41, 55)  # Light background
COLOR_BG_HOVER = (55, 65, 81)  # Hover state
COLOR_TEXT_PRIMARY = (243, 244, 246)  # Light gray text
COLOR_TEXT_SECONDARY = (156, 163, 175)  # Medium gray text
COLOR_ACCENT = (99, 102, 241)  # Indigo
COLOR_HIGHLIGHT = (236, 72, 153)  # Pink highlight

def draw_rounded_rect(surface, color, rect, radius=15, border=0, border_color=None):
    """Draw a rounded rectangle with optional border"""
    if border > 0 and border_color:
        # Draw border
        pygame.draw.rect(surface, border_color, rect, border_radius=radius)
    # Draw fill
    inner_rect = (rect[0] + border, rect[1] + border, 
                  rect[2] - border * 2, rect[3] - border * 2)
    pygame.draw.rect(surface, color, inner_rect, border_radius=radius)

def draw_shadow(surface, rect, offset=5, radius=15):
    """Draw a shadow effect"""
    shadow_rect = (rect[0] + offset, rect[1] + offset, rect[2], rect[3])
    shadow_surface = pygame.Surface((rect[2], rect[3]), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surface, (0, 0, 0, 50), (0, 0, rect[2], rect[3]), border_radius=radius)
    surface.blit(shadow_surface, (shadow_rect[0], shadow_rect[1]))

class MenuOption:
    def __init__(self, title, description, icon, action, color=COLOR_PRIMARY):
        self.title = title
        self.description = description
        self.icon = icon
        self.action = action
        self.color = color
        self.rect = None
        self.hovered = False

    def draw(self, surface, x, y, width, height):
        """Draw the menu option"""
        self.rect = pygame.Rect(x, y, width, height)
        
        # Determine colors based on hover state
        bg_color = COLOR_BG_HOVER if self.hovered else COLOR_BG_LIGHT
        border_color = self.color if self.hovered else COLOR_ACCENT
        
        # Draw shadow
        draw_shadow(surface, (x, y, width, height))
        
        # Draw card
        draw_rounded_rect(surface, bg_color, (x, y, width, height), radius=20, 
                         border=3, border_color=border_color)
        
        # Draw icon/emoji
        icon_surface = subtitle_font.render(self.icon, True, self.color)
        surface.blit(icon_surface, (x + 30, y + 25))
        
        # Draw title
        title_surface = menu_font.render(self.title, True, COLOR_TEXT_PRIMARY)
        surface.blit(title_surface, (x + 100, y + 25))
        
        # Draw description
        desc_surface = small_font.render(self.description, True, COLOR_TEXT_SECONDARY)
        surface.blit(desc_surface, (x + 100, y + 65))
        
        # Draw arrow indicator if hovered
        if self.hovered:
            arrow = menu_font.render("→", True, self.color)
            surface.blit(arrow, (x + width - 50, y + height // 2 - 15))

    def check_hover(self, mouse_pos):
        """Check if mouse is hovering over this option"""
        if self.rect:
            self.hovered = self.rect.collidepoint(mouse_pos)
        return self.hovered

def run_script(script_name):
    """Run a Python script"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(dir_path, script_name)
    
    if os.path.exists(script_path):
        # Get the Python executable
        python_exe = sys.executable
        subprocess.Popen([python_exe, script_path])
        return True
    return False

def open_minigames_web():
    """Open minigames web interface"""
    dir_path = os.path.dirname(os.path.realpath(__file__))
    html_path = os.path.join(dir_path, "minigames_web", "index.html")
    
    if os.path.exists(html_path):
        import webbrowser
        import time
        
        # Start the eye tracking server first
        print("Iniciando servidor de eye-tracking...")
        server_started = run_script("minigames_server.py")
        
        if server_started:
            print("Servidor iniciado. Esperando 3 segundos antes de abrir el navegador...")
            time.sleep(3)  # Give server time to initialize
            
            # Open the web page
            print(f"Abriendo página web: {html_path}")
            webbrowser.open(f'file://{html_path}')
            
            print("\n" + "="*60)
            print("INSTRUCCIONES:")
            print("="*60)
            print("1. El servidor está corriendo en segundo plano")
            print("2. La página web debería abrirse automáticamente")
            print("3. Verifica que el indicador muestre 'Conectado' (verde)")
            print("4. Si no funciona, revisa TROUBLESHOOTING_WEB.md")
            print("="*60)
            return True
        else:
            print("Error: No se pudo iniciar el servidor")
            return False
    else:
        print(f"Web minigames not found at: {html_path}")
        return False

def open_pygame_minigames():
    """Open pygame minigames"""
    return run_script("minigames_pygame.py")

def open_calibration():
    """Open calibration demo"""
    return run_script("simple_example_v2.py")

def open_basic_demo():
    """Open basic demo"""
    return run_script("simple_example_v3.py")

def main():
    """Main launcher loop"""
    clock = pygame.time.Clock()
    
    # Create menu options
    menu_options = [
        MenuOption(
            "Calibration & Tracking",
            "Calibrate eye tracking and test gaze detection",
            "🎯",
            open_calibration,
            COLOR_PRIMARY
        ),
        MenuOption(
            "Web Minigames",
            "Play interactive eye-tracking games in your browser",
            "🌐",
            open_minigames_web,
            COLOR_SUCCESS
        ),
        MenuOption(
            "Pygame Minigames",
            "Native minigames with eye-tracking control",
            "🎮",
            open_pygame_minigames,
            COLOR_HIGHLIGHT
        ),
        MenuOption(
            "Basic Demo",
            "Simple eye tracking demonstration",
            "👁️",
            open_basic_demo,
            COLOR_WARNING
        ),
        MenuOption(
            "Exit",
            "Close the launcher",
            "🚪",
            lambda: False,
            COLOR_DANGER
        ),
    ]
    
    running = True
    particles = []  # For background animation
    
    while running:
        mouse_pos = pygame.mouse.get_pos()
        
        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_q and pygame.key.get_mods() & pygame.KMOD_CTRL:
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    for option in menu_options:
                        if option.hovered:
                            result = option.action()
                            if option.title == "Exit" or result == False:
                                running = False
        
        # Fill background
        screen.fill(COLOR_BG_DARK)
        
        # Draw animated background particles
        import random
        if len(particles) < 50:
            particles.append({
                'x': random.randint(0, WINDOW_WIDTH),
                'y': random.randint(0, WINDOW_HEIGHT),
                'size': random.randint(1, 3),
                'speed': random.uniform(0.1, 0.5)
            })
        
        for particle in particles[:]:
            particle['y'] -= particle['speed']
            if particle['y'] < 0:
                particles.remove(particle)
            else:
                alpha = 100
                pygame.draw.circle(screen, (*COLOR_ACCENT[:3], alpha), 
                                 (int(particle['x']), int(particle['y'])), 
                                 particle['size'])
        
        # Draw header
        header_y = 60
        title_surface = title_font.render("EyeGestures", True, COLOR_PRIMARY)
        title_rect = title_surface.get_rect(center=(WINDOW_WIDTH // 2, header_y))
        screen.blit(title_surface, title_rect)
        
        subtitle_surface = small_font.render("Professional Eye Tracking System", True, COLOR_TEXT_SECONDARY)
        subtitle_rect = subtitle_surface.get_rect(center=(WINDOW_WIDTH // 2, header_y + 60))
        screen.blit(subtitle_surface, subtitle_rect)
        
        # Draw decorative line
        line_y = header_y + 100
        pygame.draw.line(screen, COLOR_ACCENT, 
                        (WINDOW_WIDTH // 4, line_y), 
                        (WINDOW_WIDTH * 3 // 4, line_y), 2)
        
        # Draw menu options
        menu_start_y = 200
        option_height = 100
        option_spacing = 20
        option_width = 800
        option_x = (WINDOW_WIDTH - option_width) // 2
        
        for i, option in enumerate(menu_options):
            y = menu_start_y + i * (option_height + option_spacing)
            option.check_hover(mouse_pos)
            option.draw(screen, option_x, y, option_width, option_height)
        
        # Draw footer
        footer_y = WINDOW_HEIGHT - 40
        footer_text = small_font.render(
            "Use mouse to select • ESC or Ctrl+Q to exit", 
            True, COLOR_TEXT_SECONDARY
        )
        footer_rect = footer_text.get_rect(center=(WINDOW_WIDTH // 2, footer_y))
        screen.blit(footer_text, footer_rect)
        
        # Draw version
        version_text = small_font.render("v2.0", True, COLOR_TEXT_SECONDARY)
        screen.blit(version_text, (WINDOW_WIDTH - 60, WINDOW_HEIGHT - 30))
        
        pygame.display.flip()
        clock.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()
