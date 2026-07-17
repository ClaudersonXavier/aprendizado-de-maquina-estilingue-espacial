"""
main.py — Loop de teste do ambiente Odisseia Orbital.
Executa acoes aleatorias para validar a renderizacao e a fisica.
"""
import random
import sys
import pygame
from orbital_env import OrbitalEnv


def main():
    env = OrbitalEnv(render_mode="human")
    obs = env.reset()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r:
                    obs = env.reset()
                elif event.key == pygame.K_SPACE:
                    # Pausa/retoma — util para debug visual
                    pass

        if not env.done:
            action = random.randint(0, 4)
            obs, reward, done, info = env.step(action)

        env.render()

    env.close()
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
