"""
main.py — Loop de teste do ambiente Odisseia Orbital.
Controle manual (player) para validar a fisica e a renderizacao.

Controles:
    W / Seta Cima     — impulso para cima
    S / Seta Baixo    — impulso para baixo
    A / Seta Esquerda — impulso para esquerda
    D / Seta Direita  — impulso para direita
    R                 — reiniciar episodio
    ESC               — sair
"""
import sys
import pygame
from orbital_env import OrbitalEnv


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
