"""
watch.py — Carrega a Q-table treinada e exibe o agente jogando.
Uso: python watch.py [--episodios N]
"""

import argparse
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game-enviroment'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game-enviroment', 'agents'))

from orbital_env import OrbitalEnv
from discretizer import DiscretizadorEstado
from q_learning_agent import AgenteQLearning

MAX_PASSOS = 2000

ICONES = {
    "docked": "ATRACOU", "crashed_planet": "COLIDIU",
    "out_of_bounds": "FORA", "no_fuel": "SEM COMB.",
    "timeout": "TIMEOUT",
}


def main():
    parser = argparse.ArgumentParser(description="Assiste o agente Q-Learning treinado.")
    parser.add_argument("--episodios", type=int, default=1,
                        help="Numero de episodios para exibir (padrao: 1)")
    args = parser.parse_args()

    print("=" * 50)
    print("  ODISSEIA ORBITAL — Assistindo Agente Treinado")
    print("=" * 50)

    env = OrbitalEnv(render_mode="human")
    disc = DiscretizadorEstado(
        checkpoints=env.checkpoints,
        posicao_estacao=env.station_pos,
        planetas=env.planets,
    )

    agente = AgenteQLearning(n_acoes=5)
    ckpt = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'q_table_odisseia.pkl')
    agente.carregar(ckpt)
    agente.epsilon = 0.0

    print(f"  Q-table carregada: {len(agente.tabela_q)} estados")
    print(f"  Exibindo {args.episodios} episodio(s)...")
    print("-" * 50)

    for ep in range(args.episodios):
        obs = env.reset()
        estado = disc.discretizar(obs)
        terminal = False
        ep_rec = 0.0
        ep_pas = 0
        info = {}
        ep_cps = 0

        while not terminal and ep_pas < MAX_PASSOS:
            acao = agente.selecionar_acao(estado)
            prox_obs, recompensa, terminal, info = env.step(acao)
            estado = disc.discretizar(prox_obs)
            if info.get("checkpoint_collected"):
                ep_cps += 1
            ep_rec += recompensa
            ep_pas += 1
            env.render()

        icone = ICONES.get(info.get("status", "timeout"), "???")
        print(f"  Ep {ep + 1:2d} | {icone:10s} | Rec: {ep_rec:8.1f} | Passos: {ep_pas:4d} | CPs: {ep_cps}")

    env.close()
    print("-" * 50)
    print("  Fim da exibicao.")
    print("=" * 50)


if __name__ == '__main__':
    main()