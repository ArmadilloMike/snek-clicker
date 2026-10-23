import json
import os
import sys
from pathlib import Path
from random import randint
import pygame
import random

def resource_path(relative_path: str) -> Path:
    if hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS) / relative_path
    return Path(__file__).resolve().parent / relative_path
# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("Snek Clicker")
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(None, 64)
GAME_NAME = "snek-clicker"

# icon
icon_path = resource_path("assets/snek.ico")
icon = pygame.image.load(icon_path).convert_alpha()
pygame.display.set_icon(pygame.transform.smoothscale(icon, (32,32)))
# sprites
SNEK_SPRITE_PATH = resource_path("assets/snek.png")
snek_image = pygame.image.load(SNEK_SPRITE_PATH).convert_alpha()
snek_image = pygame.transform.scale(snek_image, (200,200))

# game info
scales = 0
click_amount = 1
bought_times = {}
item_defs = []
win_scales_amount = 10
game_won = False

# Shop stuff
SHOP_X = 800
SHOP_START_Y = 100
ITEM_W, ITEM_H = 470, 50
ITEM_GAP = 10
last_used_id = 0
shop_items = []

# auto click
auto_click = 0
AUTO_CLICK_EVENT = pygame.USEREVENT + 1
pygame.time.set_timer(AUTO_CLICK_EVENT, 1000)

# bonus stuff
GOLDEN_SPRITE_PATH = resource_path("assets/scale_gold.png")
SCALE_SPRITE_PATH = resource_path("assets/scale.png")
golden = 0
SPAWN_BONUS_SCALE = pygame.USEREVENT + 2
bonus_scales = []
BONUS_SCALE_LIFETIME = 5000
BONUS_SIZE = 40
BONUS_MIN_X = 0
BONUS_MAX_X = SHOP_X - BONUS_SIZE
BONUS_MIN_Y = 60
BONUS_MAX_Y = 720 - BONUS_SIZE
SNEK_X = 300
SNEK_Y = 220
SNEK_W = 200
SNEK_H = 200
SNEK_RECT = pygame.Rect(SNEK_X, SNEK_Y, SNEK_W, SNEK_H)
golden_scale_image = pygame.image.load(GOLDEN_SPRITE_PATH).convert_alpha()
golden_scale_image = pygame.transform.scale(golden_scale_image, (BONUS_SIZE, BONUS_SIZE))
scale_image = pygame.image.load(SCALE_SPRITE_PATH).convert_alpha()
scale_image = pygame.transform.scale(scale_image, (BONUS_SIZE, BONUS_SIZE))
def get_bonus_spawn():
    while True:
        x = random.randint(BONUS_MIN_X, BONUS_MAX_X)
        y = random.randint(BONUS_MIN_Y, BONUS_MAX_Y)
        bonus_rect = pygame.Rect(x, y, BONUS_SIZE, BONUS_SIZE)

        if not SNEK_RECT.colliderect(bonus_rect):
            return x, y
def schedule_scale_spawn():
    delay = random.randint(20000, 60000)
    pygame.time.set_timer(SPAWN_BONUS_SCALE, delay)

# ghost snek things
ghost_image = pygame.image.load(SNEK_SPRITE_PATH).convert_alpha()
ghost_sneks = []
min_x = 0
max_x = SHOP_X - 1
min_y = 0
max_y = 719

def spawn_ghost(x=300, y=220, speed=30, size=30):
    ghost_sneks.append({"x": float(x), "y": float(y), "speed": float(speed), "size": int(size)})
def draw_ghost_snek(surface, x, y, size=30):
    ghost_sprite = pygame.transform.smoothscale(ghost_image, (size, size))
    ghost_sprite.set_alpha(180)
    surface.blit(ghost_sprite, (int(x), int(y)))
    return pygame.Rect(int(x), int(y), size, size)

schedule_scale_spawn()

# draw functions
def draw_snek(surface):
    surface.blit(snek_image, (300, 220))
    return pygame.Rect(300,220, snek_image.get_width(), snek_image.get_height())
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
    shop_items.append({"id": id, "name": name, "cost": cost, "rect": rect, "uses": uses})
    item_defs.append({"id": id, "name": name, "cost": cost, "uses": uses})
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
    surface.blit(scale_image, (x, y))
    rect = pygame.Rect(x, y, BONUS_SIZE, BONUS_SIZE)
    if gold:
        surface.blit(golden_scale_image, (x, y))
    else:
        surface.blit(scale_image, (x, y))
    return rect
def draw_congratulations():
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
    overlay.fill((0,0,0,180))
    screen.blit(overlay, (0,0))

    title_font = pygame.font.Font(None, 90)
    text_font = pygame.font.Font(None, 40)

    title = title_font.render("You Win!", True, (255, 215, 0))
    subtitle = text_font.render("Close the game to reset your progress", True, (255, 255, 255))

    screen.blit(title, title.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 30)))
    screen.blit(subtitle, subtitle.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 40)))

# shop items
SAVE_GAME_EVENT = pygame.USEREVENT + 3
save_enabled = True
pygame.time.set_timer(SAVE_GAME_EVENT, 10000)
add_shop_item("+1 Click Power", 5, 5) #1
add_shop_item("+0.1 Auto Click", 10, 10) #2
add_shop_item("2x Click Power", 100, 2) #3
add_shop_item("+1 Auto Click", 150, 15) #4
add_shop_item("+5 Click Power", 200, 10) #5
add_shop_item("3x Auto Click", 500, 3) #6
add_shop_item("+10 Click Power", 300, 5) #7
add_shop_item("4x Click Power", 400, 2) #8

snek = draw_snek(screen)

# save file stuff
def get_save_dir() -> Path:
    if sys.platform == "win32":
        base = Path(os.environ.get("APPDATA", Path.home() / "AppData" / "Roaming"))
    elif sys.platform == "darwin":
        base = Path.home() / "Library" / "Application Support"
    else:
        base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    save_dir = base / GAME_NAME
    save_dir.mkdir(parents=True, exist_ok=True)
    return save_dir
SAVE_PATH = get_save_dir() / "save_file.json"

def save_game(data: dict) -> None:
    tmp = SAVE_PATH.with_suffix(".json.tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)
    os.replace(tmp, SAVE_PATH)

def load_game(default: dict | None = None) -> dict:
    try:
        with open(SAVE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return default if default is not None else {}

def extract_save_values(state: dict) -> dict:
    scales = state.get("scales", 0)
    click_amount = state.get("click_amount", 1)
    auto_click = state.get("auto_click", 0.0)

    if not isinstance(scales, (int, float)):
        scales = 0
    if not isinstance(click_amount, (int, float)):
        click_amount = 1
    if not isinstance(auto_click, (int, float)):
        auto_click = 0.0

    raw_bought = state.get("bought_times", {})
    if not isinstance(raw_bought, dict):
        raw_bought = {}

    bought_times = {}
    for key, count in raw_bought.items():
        try:
            item_id = int(key)
        except (ValueError, TypeError):
            continue
        if isinstance(count, int) and count > 0:
            bought_times[item_id] = count

    return {
        "scales": scales,
        "click_amount": click_amount,
        "auto_click": auto_click,
        "bought_times": bought_times
    }

def build_save_file(scales, click_amount, auto_click, bought_times) -> dict:
    return {
        "scales": scales,
        "click_amount": click_amount,
        "auto_click": auto_click,
        "bought_times": {str(k): v for k, v in bought_times.items() if v > 0}
    }

def apply_bought_times(click_amount, auto_click, bought_times):
    for item_id, count in bought_times.items():
        if item_id == 1:
            click_amount += count
        elif item_id == 2:
            auto_click += 0.1 * count
            auto_click = round(auto_click, 1)
        elif item_id == 3:
            click_amount *= 2 ** count
    return click_amount, auto_click

def rebuild_shop_from_bought_times(bought_times):
    global shop_items, last_used_id

    # reset the shop to a clean state
    shop_items = []
    last_used_id = 0
    global item_defs

    for item_def in item_defs:
        bought = bought_times.get(item_def["id"], 0)
        remaining_uses = item_def["uses"] - bought

        if remaining_uses <= 0:
            continue

        y = SHOP_START_Y + len(shop_items) * (ITEM_H + ITEM_GAP)
        rect = pygame.Rect(SHOP_X, y, ITEM_W, ITEM_H)
        shop_items.append({
            "name": item_def["name"],
            "cost": item_def["cost"],
            "uses": remaining_uses,
            "id": item_def["id"],
            "rect": rect,
        })
        last_used_id = max(last_used_id, item_def["id"])

def clear_save():
    data = {
        "scales": 0,
        "click_amount": 1,
        "auto_click": 0,
        "bought_times": {}
    }
    save_game(data)

data = load_game()
save_data = extract_save_values(data)

scales = save_data["scales"]
bought_times = save_data["bought_times"]

# rebuild the actual state from the saved purchased counts
click_amount = 1
auto_click = 0.0
click_amount, auto_click = apply_bought_times(click_amount, auto_click, bought_times)
rebuild_shop_from_bought_times(bought_times)

while running:
    dt = clock.get_time() / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            data = build_save_file(scales, click_amount, auto_click, bought_times)
            save_game(data)
            running = False

        if game_won:
            continue
        # check if mouse clicked on a shop item or the snek
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and snek.collidepoint(event.pos):
                scales += click_amount
                spawng = random.randint(1,10)
                if spawng == random.randint(1, 10):
                    spawn_ghost(randint(min_x, max_x), randint(min_y, max_y), randint(40, 100), randint(15, 30))

            for bonus in list(bonus_scales):
                if bonus["rect"].collidepoint(event.pos):
                    if bonus["gold"]:
                        amount = random.randint(40, 80)
                        scales += amount
                    else:
                        amount = random.randint(10,30)
                        scales += amount
                    bonus_scales.remove(bonus)

            item = get_click_item(event.pos)
            if item and scales >= item["cost"]:
                scales -= item["cost"]
                scales = round(scales, 1)

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
                elif item["id"] == 3:
                    click_amount *= 2
                elif item["id"] == 4:
                    auto_click += 1
                    auto_click = round(auto_click, 1)
                elif item["id"] == 5:
                    click_amount += 5
                elif item["id"] == 6:
                    auto_click = auto_click * 3
                    auto_click = round(auto_click, 1)
                elif item["id"] == 7:
                    click_amount += 10
                elif item["id"] == 8:
                    click_amount = click_amount * 4

                bought_times[item["id"]] = bought_times.get(item["id"], 0) + 1
        # autoclicking things
        if event.type == AUTO_CLICK_EVENT:
            scales += auto_click
            scales = round(scales, 1)
        # scale
        if event.type == SPAWN_BONUS_SCALE:
            x, y = get_bonus_spawn()
            gold = golden == 5
            bonus_scales.append({"rect": pygame.Rect(x, y, BONUS_SIZE, BONUS_SIZE), "gold": gold, "expires_at": pygame.time.get_ticks() + BONUS_SCALE_LIFETIME})
            golden += 1
            since = randint(5,10)
            if golden >= since:
                golden = 0
            schedule_scale_spawn()
        # save
        if event.type == SAVE_GAME_EVENT and save_enabled:
            data = build_save_file(scales, click_amount, auto_click, bought_times)
            save_game(data)

    if game_won:
        draw_congratulations()
        pygame.display.flip()
        clock.tick(60)
        continue

    # create background
    background = pygame.Surface(screen.get_size())
    background = background.convert()
    background.fill((100,100,100))
    screen.blit(background, (0,0))

    # remove bonus scales
    current_time = pygame.time.get_ticks()
    for bonus in list(bonus_scales):
        if current_time >= bonus["expires_at"]:
            bonus_scales.remove(bonus)

    #draw stuff
    snek = draw_snek(screen)
    for bonus in bonus_scales:
        draw_scale(screen, bonus["gold"], bonus["rect"].x, bonus["rect"].y)
    draw_text(screen, font)
    draw_shop(screen, font)

    # draw ghost sneks
    for ghost in list(ghost_sneks):
        ghost["y"] -= ghost["speed"] * dt
        if ghost["y"] + ghost["size"] <= 0:
            ghost_sneks.remove(ghost)
    for ghost in ghost_sneks:
        draw_ghost_snek(screen, ghost['x'], ghost['y'], ghost['size'])

    if scales >= win_scales_amount:
        game_won = True
        save_enabled = False
        clear_save()
        draw_congratulations()
        pygame.display.flip()
        continue

    pygame.display.flip()
    clock.tick(60)

pygame.quit()