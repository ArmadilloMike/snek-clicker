import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True

def draw_snek(surface):
    pygame.draw.rect(surface, (50, 200, 100), pygame.Rect(300, 220, 40, 40))

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    screen.fill("white")

    draw_snek(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()