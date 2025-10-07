import pygame

pygame.init()  
pygame.font.init()
# initialize the pygame window
window_screen = pygame.display.set_mode((700, 450))
# for borderless window use pygame.Noframe
# size of the pygame window will be of width 700 and height 450
# Create a surface
surface = pygame.Surface((800, 600))
surface.set_alpha(0)  # Set transparency (0 = fully transparent, 255 = fully opaque)
surface.fill((255, 0, 0))  # Fill the surface with a color

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    window_screen.fill((0, 0, 0))  # Fill the screen with black
    window_screen.blit(surface, (0, 0))  # Blit the transparent surface onto the screen
    pygame.display.flip()

pygame.quit()

""" # This will set the opacity and transparency color key of a layered window
font = pygame.font.SysFont("Times New Roman", 54)
# declare the size and font of the text for the window
text = []
# Declaring the array for storing the text
text.append((font.render("Transparent Window", 0, (255, 100, 0)), (20, 10)))   
text.append((font.render("Press Esc to close the window", 0, (255, 100, 100)), (20, 250)))


while True:
    window_screen.fill((0, 0, 0, 0))
    pygame.draw.rect(window_screen, pygame.Color(255, 255, 255, 128), pygame.Rect(0, 0, 1000, 750))

    s = pygame.Surface((1000,750), pygame.SRCALPHA)   # per-pixel alpha
    s.fill((255,255,255,128))                         # notice the alpha value in the color
    window_screen.blit(s, (0,0)) """