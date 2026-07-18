# Especificação Técnica: Agente de Aprendizado por Reforço (Q-Learning Tabular)

## 1. Contexto e Objetivo do Agente
Desenvolver um agente de Aprendizado por Reforço clássico (Tabela Q) para o ambiente "Odisséia Orbital". O ambiente opera em espaço contínuo e retorna um vetor de observação com 7 elementos[cite: 3]. O espaço de ações é discreto (5 ações, de 0 a 4)[cite: 3].

Para evitar a explosão combinatória de estados, o agente implementará um **State Wrapper (Discretizador)** que reduzirá a percepção do mundo a apenas 432 situações possíveis.

## 2. A Bússola Dinâmica e Discretização de Estado (State Wrapper)
Crie uma classe `StateDiscretizer` que receberá o vetor contínuo do ambiente e a lista de entidades (planetas, checkpoints e estação)[cite: 3, 4]. O discretizador deve processar a lógica em etapas:

### 2.1. Definição do Alvo (Bússola Dinâmica)
* O sistema deve escanear a lista de checkpoints.
* O alvo atual será sempre o **checkpoint não coletado mais próximo**.
* Se todos os checkpoints já estiverem coletados, o alvo passa a ser a **Estação Espacial**.
* Como a recompensa de checkpoint é alta (`100.0`)[cite: 1], isso garante que o agente varra o mapa pelo ganho de pontuação.

### 2.2. As 4 Variáveis de Estado
O método principal do wrapper deve retornar uma tupla discreta com os seguintes valores:
1. **Direção do Alvo (0 a 7):** Calcule o ângulo da nave para o alvo dinâmico (definido acima) e divida em 8 quadrantes de 45 graus.
2. **Direção do Movimento (0 a 8):** Se a velocidade absoluta for quase zero, retorne `8`. Caso contrário, calcule o ângulo do vetor velocidade e divida nos mesmos 8 quadrantes (0 a 7).
3. **Alerta de Perigo (0 a 1):** Verifique a distância para o centro de todos os planetas. Se a distância for menor que o raio do planeta mais uma margem de segurança (ex: 40 pixels), retorne `1` (Perigo). Senão, `0` (Seguro).
4. **Nível de Combustível (0 a 2):** Converta o combustível atual em três faixas: `0` (Vazio/Crítico), `1` (Médio), `2` (Alto).

## 3. O Cérebro: Q-Learning e Hiperparâmetros
Implemente a classe `QLearningAgent` que gerenciará um dicionário (a Tabela Q).
* As chaves do dicionário serão as tuplas de estado geradas pelo wrapper.
* Os valores serão arrays de 5 posições (os Q-values para as ações 0 a 4).

### Hiperparâmetros Recomendados:
* **Alpha (Taxa de Aprendizado):** `0.1`
* **Gamma (Fator de Desconto):** `0.99`
* **Epsilon (Taxa de Exploração):** Inicia em `1.0`. Multiplique por `0.999` ao fim de cada episódio, até atingir um mínimo de `0.05`.

### Equação de Atualização:
Implemente o método `learn` utilizando a Equação de Bellman:
$$Q(S, A) = Q(S, A) + \alpha [R + \gamma \max Q(S', a) - Q(S, A)]$$

## 4. Loop de Treinamento e Visualização (O Efeito Timelapse)
O bloco principal (`__main__`) deve ser dividido em duas etapas para permitir o treinamento rápido e a apresentação visual.

### Fase 1: Treinamento Bruto (Em Background)
* Instancie o ambiente sem renderização: `OrbitalEnv(render_mode=None)`[cite: 3].
* Execute um loop de **3.000 a 5.000 episódios**. 
* Como não há renderização de tela, isso será processado em segundos.
* Imprima logs no terminal a cada 500 episódios (Taxa de sucesso e valor atual de Epsilon).

### Fase 2: A Demonstração (Showcase)
* Após o treinamento, fixe `epsilon = 0.0` (exploração desativada, pura inteligência).
* Recrie o ambiente com a interface ativada: `OrbitalEnv(render_mode="human")`[cite: 2, 3].
* Execute de 3 a 5 episódios para gravar o vídeo da apresentação. O agente executará o planejamento perfeito, utilizando a física contínua para navegar até os checkpoints e atracar na estação espacial.
* Ao final de tudo, salve a Tabela Q treinada utilizando a biblioteca `pickle`.