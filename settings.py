import pygame

pygame.init()

info = pygame.display.Info()

# --- CORREÇÃO DE PAISAGEM ---
# Pega o maior valor para ser a largura (WIDTH) e o menor para altura (HEIGHT)
# Isso força o jogo a "pensar" deitado mesmo se o sensor falhar.
WIDTH = max(info.current_w, info.current_h)
HEIGHT = min(info.current_w, info.current_h)

# Fator de Escala
SCALE = WIDTH / 800 
if SCALE < 1: SCALE = 1

print(f"Resolução: {WIDTH}x{HEIGHT} | Escala: {SCALE:.2f}")

TITLE = "Super Pug Game"
FPS = 60

# --- FÍSICA ---
PLAYER_SPEED = 8 * SCALE
GRAVITY = 0.8 * SCALE
JUMP_FORCE = -18 * SCALE

# --- CORES ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
BROWN = (101, 67, 33)
