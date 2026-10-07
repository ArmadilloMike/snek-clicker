import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
scales = 0

def draw_snek(surface):
    pygame.draw.rect(surface, (50, 200, 100), pygame.Rect(300, 220, 40, 40))
    return pygame.Rect(300,220,40,40)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((100,100,100))

    snek = draw_snek(screen)

    mouse_pressed = pygame.mouse.get_pressed(num_buttons=3) == (True, False, False)
    mouse_pos = pygame.mouse.get_pos()

    if mouse_pressed and snek.collidepoint(mouse_pos):
        scales += 1
        print(scales)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()