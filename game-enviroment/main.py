"""
main.py — Loop de teste Odisseia Orbital (Pixel Art Retro).
Tela de titulo estilo arcade + controle manual do jogador.
"""

import math
import random
import sys
import pygame
from orbital_env import OrbitalEnv, PixelFont


RENDER_W = 400
RENDER_H = 300
SCREEN_W = 800
SCREEN_H = 600


def _generate_stars():
    stars = []
    for _ in range(50):
        stars.append({
            "x": random.randint(0, RENDER_W - 1),
            "y": random.randint(0, RENDER_H - 1),
            "color": random.choice([
                (120, 130, 160), (240, 240, 255), (255, 220, 0), (0, 220, 220),
            ]),
            "phase": random.randint(0, 60),
            "period": random.randint(30, 80),
        })
    return stars


def show_title_screen(screen, canvas):
    stars = _generate_stars()
    clock = pygame.time.Clock()
    start_time = pygame.time.get_ticks()

    while True:
        dt = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                if event.key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER):
                    for alpha in range(0, 255, 12):
                        fade = pygame.Surface((RENDER_W, RENDER_H))
                        fade.fill((0, 0, 0))
                        fade.set_alpha(alpha)
                        canvas.blit(fade, (0, 0))
                        scaled = pygame.transform.scale(canvas, (SCREEN_W, SCREEN_H))
                        screen.blit(scaled, (0, 0))
                        pygame.display.flip()
                        clock.tick(60)
                    return True

        canvas.fill((8, 12, 32))

        for star in stars:
            frame = (dt // 16) % star["period"]
            visible = frame < star["period"] * 0.7
            if visible:
                if 0 <= star["x"] < RENDER_W and 0 <= star["y"] < RENDER_H:
                    canvas.set_at((star["x"], star["y"]), star["color"])

        for x in range(0, RENDER_W, 50):
            for y in range(0, RENDER_H, 4):
                if (y // 4) % 2 == 0 and x < RENDER_W and y < RENDER_H:
                    canvas.set_at((x, y), (40, 50, 70))

        frame_w = 260
        frame_h = 140
        frame_x = (RENDER_W - frame_w) // 2
        frame_y = (RENDER_H - frame_h) // 2

        pygame.draw.rect(canvas, (0, 0, 0), (frame_x, frame_y, frame_w, frame_h))
        pygame.draw.rect(canvas, (0, 220, 220), (frame_x, frame_y, frame_w, frame_h), 2)
        pygame.draw.rect(canvas, (0, 0, 0),
                         (frame_x + 2, frame_y + 2, frame_w - 4, frame_h - 4), 1)

        title1 = PixelFont.render("ODISSEIA", (0, 220, 220))
        canvas.blit(title1, (frame_x + (frame_w - title1.get_width()) // 2, frame_y + 14))

        title2 = PixelFont.render("ORBITAL", (220, 40, 220))
        canvas.blit(title2, (frame_x + (frame_w - title2.get_width()) // 2, frame_y + 32))

        sub = PixelFont.render("SPACE SIMULATOR", (255, 220, 0))
        canvas.blit(sub, (frame_x + (frame_w - sub.get_width()) // 2, frame_y + 52))

        pygame.draw.line(canvas, (0, 220, 220),
                         (frame_x + 20, frame_y + 68),
                         (frame_x + frame_w - 20, frame_y + 68), 1)
        pygame.draw.line(canvas, (220, 40, 220),
                         (frame_x + 20, frame_y + 86),
                         (frame_x + frame_w - 20, frame_y + 86), 1)

        blink = (dt // 500) % 2
        if blink:
            hint = PixelFont.render("PRESS ENTER", (0, 220, 220))
            canvas.blit(hint, (frame_x + (frame_w - hint.get_width()) // 2, frame_y + 95))

        ctrl = PixelFont.render("WASD=MOVE R=RESET ESC=QUIT", (120, 130, 160))
        canvas.blit(ctrl, (RENDER_W // 2 - ctrl.get_width() // 2, RENDER_H - 16))

        scaled = pygame.transform.scale(canvas, (SCREEN_W, SCREEN_H))
        screen.blit(scaled, (0, 0))
        pygame.display.flip()
        clock.tick(60)


def _read_action():
    keys = pygame.key.get_pressed()
    if keys[pygame.K_w] or keys[pygame.K_UP]:
        return 1
    if keys[pygame.K_s] or keys[pygame.K_DOWN]:
        return 2
    if keys[pygame.K_a] or keys[pygame.K_LEFT]:
        return 3
    if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
        return 4
    return 0


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
    pygame.display.set_caption("Odisseia Orbital")
    canvas = pygame.Surface((RENDER_W, RENDER_H))

    play = show_title_screen(screen, canvas)
    if not play:
        pygame.quit()
        sys.exit()

    env = OrbitalEnv(render_mode="human")
    env.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    env.reset()

        if not env.done:
            action = _read_action()
            env.step(action)

        env.render()

    env.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
