import json
import os
import sys
from pathlib import Path
from random import randint
import pygame
import random

# pygame setup
pygame.init()
screen = pygame.display.set_mode((1280, 720))
clock = pygame.time.Clock()
running = True
font = pygame.font.Font(None, 64)
GAME_NAME = "snek-clicker"

# game info
scales = 0
click_amount = 1
bought_times = {}

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
BONUS_SCALE_LIFETIME = 5000
BONUS_SIZE = 40
BONUS_MIN_X = 0
BONUS_MAX_X = SHOP_X - BONUS_SIZE
BONUS_MIN_Y = 60
BONUS_MAX_Y = 720 - BONUS_SIZE
def schedule_scale_spawn():
    delay = random.randint(2000, 6000)
    pygame.time.set_timer(SPAWN_BONUS_SCALE, delay)

# ghost snek things
ghost_sneks = []
min_x = 0
max_x = SHOP_X - 1
min_y = 0
max_y = 719

def spawn_ghost(x=300, y=220, speed=30, size=30):
    ghost_sneks.append({"x": float(x), "y": float(y), "speed": float(speed), "size": int(size)})
def draw_ghost_snek(surface, x, y, size=30):
    ghost_surface = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.rect(ghost_surface, (180, 255, 200, 100), pygame.Rect(0, 0, 30, 30))
    surface.blit(ghost_surface, (int(x), int(y)))
    return pygame.Rect(int(x), int(y), size, size)

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
SAVE_GAME_EVENT = pygame.USEREVENT + 3
pygame.time.set_timer(SAVE_GAME_EVENT, 10000)
add_shop_item("+1 cp", 50, 2,)
add_shop_item("+1 auto click", 1, 10)
add_shop_item("times 2 cp", 100, 1)

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

while running:
    dt = clock.get_time() / 1000.0
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        # check if mouse clicked on a shop item or the snek
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1 and snek.collidepoint(event.pos):
                scales += click_amount
                spawn_ghost(randint(min_x, max_x), randint(min_y, max_y), randint(40, 100), randint(15, 30))

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
                elif item["id"] == 3:
                    click_amount *= 2

                bought_times[item["id"]] = bought_times.get(item["id"], 0) + 1
        # autoclicking things
        if event.type == AUTO_CLICK_EVENT:
            scales += auto_click
            scales = round(scales, 1)
        # scale
        if event.type == SPAWN_BONUS_SCALE:
            scale_x = random.randint(BONUS_MIN_X, BONUS_MAX_X)
            scale_y = random.randint(BONUS_MIN_Y, BONUS_MAX_Y)
            gold = golden == 5
            bonus_scales.append({"rect": pygame.Rect(scale_x, scale_y, 40, 40), "gold": gold, "expires_at": pygame.time.get_ticks() + BONUS_SCALE_LIFETIME})
            golden += 1
            since = randint(5,10)
            if golden >= since:
                golden = 0
            schedule_scale_spawn()
        # save
        if event.type == SAVE_GAME_EVENT:
            data = build_save_file(scales, click_amount, auto_click, bought_times)
            save_game(data)

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

    pygame.display.flip()
    clock.tick(60)

pygame.quit()