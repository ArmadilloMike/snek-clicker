# Snek Clicker
![hackatime stats for this project](https://hackatime.hackclub.com/api/v1/badge/U08FNN5D9PC/snek-clicker)

Snek Clicker is a clicker game where you click a snek to gain points (scales). 

Once you have enough scales you can buy items from the shop that increase your click power or auto click

I made this game using Python & Pygame

The art was designed in LibreSprite.

![screenhot of the game](https://cdn.hackclub.com/01a16a05-50c8-7773-9a8d-bb4988c4cf66/Screenshot%202026-10-23%20132759.png)

## How to run

1. Download the release for your OS from the [releases tab](https://github.com/ArmadilloMike/snek-clicker/releases). 
2. Open the file
3. Play the game

## How to play

TL;DR: Click the snek, buy stuff from shop, get a ton of scales

To start playing the game you have to click the green snek on the left of the screen.

Once you have enough scales (points) you can buy stuff rom the shop

Some things you can buy are increases to your click power
 and increases to auto clicking

To win the game you have to get to 100 million points

## Setup with uv

This project needs Python 3.12.10

### 1. Create the environment
```shell
uv python install 3.12.10
uv venv --python 3.12.10
uv sync --group dev
```

### 2. Run the game
```shell
uv run python main.py
```