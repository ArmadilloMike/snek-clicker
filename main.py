import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(None, 64)

# game info
scales = 0
click_amount = 1

# Shop stuff
SHOP_X = 850
SHOP_START_Y = 100
ITEM_W, ITEM_H = 400, 50
ITEM_GAP = 10
last_used_id = 0
shop_items = []

# auto click
auto_click = 0
AUTO_CLICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(AUTO_CLICK_EVENT, 1000)

# bonus stuff
golden = 0
SPAWN_BONUS_SCALE = pygame.USEREVENT + 2
bonus_scales = []
BONUS_SIZE = 40
BONUS_MIN_X = 0
BONUS_MAX_X = SHOP_X - BONUS_SIZE
BONUS_MIN_Y = 60
BONUS_MAX_Y = 720 - BONUS_SIZE
def schedule_scale_spawn():
    delay = random.randint(2000, 6000)
    pygame.time.set_timer(SPAWN_BONUS_SCALE, delay)

schedule_scale_spawn()

# draw functions
def draw_snek(surface):
    pygame.draw.rect(surface, (50, 200, 100), pygame.Rect(300, 220, 40, 40))
    return pygame.Rect(300,220,40,40)
def draw_text(screen, font):
    if pygame.font:
        text = font.render(f"Scales: {scales} - CP: {click_amount} - Auto Click: {auto_click}", True, (0,0,0))
        textpos = text.get_rect(centerx=screen.get_width() / 2, y=10)
        screen.blit(text, textpos)
def add_shop_item(name, cost, uses):
    global last_used_id
    y = SHOP_START_Y + len(shop_items) * (ITEM_H + ITEM_GAP)
    rect = pygame.Rect(SHOP_X, y, ITEM_W, ITEM_H)
    id = last_used_id + 1
    last_used_id += 1
    shop_items.append({"name": name, "cost": cost, "rect": rect, "uses": uses, "id": id})
def draw_shop(surface, font):
    for item in shop_items:
        color = (80,160,255)
        pygame.draw.rect(surface, color, item["rect"])
        label = font.render(f"{item['name']} - {item['cost']}", True, (255,255,255))
        surface.blit(label, (item["rect"].x + 10, item["rect"].centery - label.get_height() // 2))
def get_click_item(pos):
    for item in shop_items:
        if item["rect"].collidepoint(pos):
            return item
    return None
def update_shop():
    for index, item in enumerate(shop_items):
        y = SHOP_START_Y + index * (ITEM_H + ITEM_GAP)
        item["rect"].y = y
def draw_scale(surface, gold, x, y):
    rect = pygame.Rect(x, y, 40, 40)
    color = (190, 210, 15) if gold else (40, 125, 5)
    pygame.draw.rect(surface, color, rect)
    return rect

# shop items
add_shop_item("more money", 50, 2,)
add_shop_item("+1 auto click", 1, 10)

snek = draw_snek(screen)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # check if mouse clicked on a shop item or the snek
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and snek.collidepoint(event.pos):
                scales += click_amount
                print(scales)

            for bonus in list(bonus_scales):
                if bonus["rect"].collidepoint(event.pos):
                    if bonus["gold"]: scales += 50
                    else: scales += 20
                    bonus_scales.remove(bonus)

            item = get_click_item(event.pos)
            if item and scales >= item["cost"]:
                scales -= item["cost"]

                # item usage
                item["uses"] -= 1
                if item['uses'] <= 0:
                    shop_items.remove(item)
                    update_shop()

                # check what to do for a shop item
                if item["id"] == 1:
                    click_amount += 1
                elif item["id"] == 2:
                    auto_click += 0.1
                    auto_click = round(auto_click, 1)

                print(f"bought {item['name']}")
        # autoclicking things
        if event.type == AUTO_CLICK_EVENT:
            scales += auto_click
            scales = round(scales, 1)
            print(f"{auto_click}, {scales}")
        # scale
        if event.type == SPAWN_BONUS_SCALE:
            scale_x = random.randint(BONUS_MIN_X, BONUS_MAX_X)
            scale_y = random.randint(BONUS_MIN_Y, BONUS_MAX_Y)
            gold = golden == 5
            bonus_scales.append({"rect": pygame.Rect(scale_x, scale_y, 40, 40), "gold": gold})
            golden += 1
            if golden > 5:
                golden = 0
            schedule_scale_spawn()

    # create background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((100,100,100))
    screen.blit(background, (0,0))

    #draw stuff
    snek = draw_snek(screen)
    for bonus in bonus_scales:
        draw_scale(screen, bonus["gold"], bonus["rect"].x, bonus["rect"].y)
    draw_text(screen, font)
    draw_shop(screen, font)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()