import pygame

pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
scales = 0

def draw_snek(surface):
    pygame.draw.rect(surface, (50, 200, 100), pygame.Rect(300, 220, 40, 40))
    return pygame.Rect(300,220,40,40)

def draw_scales(screen):
    if pygame.font:
        font = pygame.font.Font(None, 64)
        text = font.render(f"Scales: {scales}", True, (0,0,0))
        textpos = text.get_rect(centerx=screen.get_width() / 2, y=10)
        screen.blit(text, textpos)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and snek.collidepoint(event.pos):
                scales += 1
                print(scales)

    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((100,100,100))
    screen.blit(background, (0,0))

    snek = draw_snek(screen)
    draw_scales(screen)

    pygame.display.flip()

    clock.tick(60)

pygame.quit()