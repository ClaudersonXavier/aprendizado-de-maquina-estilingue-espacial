"""
Q-Learning Tabular — Odisseia Orbital

Recompensas originais do ambiente + reward shaping por aproximacao.
Discretizador de 36720 estados (6 dimensoes).

Treino longo: 40000 episodios headless.
Showcase: 1 episodio visual greedy a cada 1000 ep + 5 no final.
"""

import os
import sys
import time

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game-enviroment'))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'game-enviroment', 'agents'))

from orbital_env import OrbitalEnv
from discretizer import DiscretizadorEstado
from q_learning_agent import AgenteQLearning

N_EPISODIOS = 80000
LOG_INTERVALO = 500
SHOWCASE_INTERVALO = 5000
N_SHOWCASE = 5
MAX_PASSOS = 2000

ICONES = {
    "docked": "ATRACOU", "crashed_planet": "COLIDIU",
    "out_of_bounds": "FORA", "no_fuel": "SEM COMB.",
    "timeout": "TIMEOUT",
}


def main():
    print("=" * 60)
    print("  ODISSEIA ORBITAL — Q-Learning Tabular")
    print("=" * 60)
    print(f"  Estados        : {DiscretizadorEstado.TOTAL_ESTADOS}")
    print(f"  Episodios      : {N_EPISODIOS}")
    print(f"  Recompensa     : ambiente + reward shaping (aproximacao)")
    print(f"  alpha=0.05  gamma=0.97  eps_min=0.03  eps_decay=0.99996")
    print(f"  Eq. Bellman    : Q(S,A) += a * [R + g * max Q(S',a) - Q(S,A)]")
    print("=" * 60)

    env = OrbitalEnv(render_mode=None)
    disc = DiscretizadorEstado(
        checkpoints=env.checkpoints,
        posicao_estacao=env.station_pos,
        planetas=env.planets,
    )
    agente = AgenteQLearning(
        n_acoes=5,
        alpha=0.05,
        gamma=0.97,
        epsilon=1.0,
        epsilon_min=0.03,
        epsilon_decay=0.99996,
        valor_otimista=5.0,
    )

    print(f"\n[Treinando {N_EPISODIOS} episodios...]")
    print("-" * 60)

    t0 = time.time()
    sucessos_janela = 0
    recs_janela = []
    max_cps = 0

    for ep in range(N_EPISODIOS):
        obs = env.reset()
        estado = disc.discretizar(obs)
        terminal = False
        ep_rec = 0.0
        ep_pas = 0
        info = {}
        ep_cps = 0

        while not terminal and ep_pas < MAX_PASSOS:
            # 1. ANTES DA ACAO: calcula distancia ate o alvo atual
            pos_nave_atual = np.array([obs[0], obs[1]], dtype=np.float64)
            alvo_atual = disc._encontrar_alvo(pos_nave_atual)
            dist_antiga = float(np.linalg.norm(pos_nave_atual - alvo_atual))

            # 2. SELECIONA E EXECUTA A ACAO
            acao = agente.selecionar_acao(estado)
            prox_obs, recompensa_ambiente, terminal, info = env.step(acao)

            # 3. DEPOIS DA ACAO: calcula nova distancia em relacao ao MESMO alvo
            pos_nave_nova = np.array([prox_obs[0], prox_obs[1]], dtype=np.float64)
            dist_nova = float(np.linalg.norm(pos_nave_nova - alvo_atual))

            # 4. REWARD SHAPING: bonus por se aproximar do alvo
            delta_distancia = dist_antiga - dist_nova
            bonus_aproximacao = delta_distancia * 2.0
            recompensa_total = recompensa_ambiente + bonus_aproximacao

            # 5. ATUALIZACAO E APRENDIZADO
            prox_estado = disc.discretizar(prox_obs)
            agente.aprender(estado, acao, recompensa_total, prox_estado, terminal)

            if info.get("checkpoint_collected"):
                ep_cps += 1

            estado = prox_estado
            obs = prox_obs
            ep_rec += recompensa_total
            ep_pas += 1

        if ep_pas >= MAX_PASSOS:
            info = {"status": "timeout"}

        if ep_cps > max_cps:
            max_cps = ep_cps
        recs_janela.append(ep_rec)
        if info.get("status") == "docked":
            sucessos_janela += 1
        agente.decair_epsilon()

        if (ep + 1) % LOG_INTERVALO == 0:
            tx = sucessos_janela / LOG_INTERVALO * 100
            max_rec = max(recs_janela)
            decorrido = time.time() - t0
            print(
                f"  Ep {ep + 1:5d} | Sucesso: {tx:5.1f}% | "
                f"maxRec: {max_rec:9.1f} | Eps: {agente.epsilon:.4f} | "
                f"maxCPs: {max_cps:1d} | Q:{len(agente.tabela_q):4d} | {decorrido:.0f}s"
            )
            sucessos_janela = 0
            recs_janela = []

        if (ep + 1) % SHOWCASE_INTERVALO == 0:
            epsilon_salvo = agente.epsilon
            agente.epsilon = 0.0
            env_show = OrbitalEnv(render_mode="human")
            disc_show = DiscretizadorEstado(
                checkpoints=env_show.checkpoints,
                posicao_estacao=env_show.station_pos,
                planetas=env_show.planets,
            )
            obs = env_show.reset()
            estado = disc_show.discretizar(obs)
            terminal = False
            ep_rec = 0.0
            ep_pas = 0
            info = {}
            ep_cps = 0
            while not terminal and ep_pas < MAX_PASSOS:
                acao = agente.selecionar_acao(estado)
                prox_obs, recompensa, terminal, info = env_show.step(acao)
                prox_estado = disc_show.discretizar(prox_obs)
                if info.get("checkpoint_collected"):
                    ep_cps += 1
                estado = prox_estado
                ep_rec += recompensa
                ep_pas += 1
                env_show.render()
            icone = ICONES.get(info.get("status", "timeout"), "???")
            print(f"\n  >>> Showcase Ep {ep + 1} (greedy) <<<")
            print(f"      {icone:10s} | Rec: {ep_rec:8.1f} | Passos: {ep_pas:4d} | CPs: {ep_cps}\n")
            env_show.close()
            agente.epsilon = epsilon_salvo

    tempo_total = time.time() - t0
    env.close()

    print("-" * 60)
    print(f"[Treino concluido em {tempo_total:.0f}s]")
    print(f"  Epsilon final: {agente.epsilon:.4f}")
    print(f"  Estados Q: {len(agente.tabela_q)} de {DiscretizadorEstado.TOTAL_ESTADOS}")
    print(f"  Recorde de CPs: {max_cps}")

    # Showcase
    print(f"\n[SHOWCASE] epsilon=0, visual...")
    print("-" * 60)

    agente.epsilon = 0.0
    env_show = OrbitalEnv(render_mode="human")

    for ep in range(N_SHOWCASE):
        obs = env_show.reset()
        estado = disc.discretizar(obs)
        terminal = False
        ep_rec = 0.0
        ep_pas = 0
        info = {}
        ep_cps = 0

        while not terminal and ep_pas < MAX_PASSOS:
            acao = agente.selecionar_acao(estado)
            prox_obs, recompensa, terminal, info = env_show.step(acao)
            prox_estado = disc.discretizar(prox_obs)
            if info.get("checkpoint_collected"):
                ep_cps += 1
            estado = prox_estado
            ep_rec += recompensa
            ep_pas += 1
            env_show.render()

        icone = ICONES.get(info.get("status", "timeout"), "???")
        print(f"  {ep + 1}/{N_SHOWCASE} {icone:10s} | Rec: {ep_rec:8.1f} | Passos: {ep_pas:4d} | CPs: {ep_cps}")

    env_show.close()

    ckpt = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'q_table_odisseia.pkl')
    agente.salvar(ckpt)
    print("-" * 60)
    print(f"[SALVO] {ckpt}")
    print("=" * 60)


if __name__ == '__main__':
    main()