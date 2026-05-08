# Implementação de Algoritmos para Resolução do Problema das 8 Rainhas

**Caetano A. de Matos, Ruan Vasconcelos**

Instituto Federal de Educação, Ciência e Tecnologia do Rio Grande do Sul — Campus Ibirubá
Rua Nelsi Ribas Fritsch, 1111 – CEP: 98200-000 – Ibirubá – RS – Brasil

---

***Abstract.** This article presents the implementation and comparative analysis of three search and optimization algorithms — Hill Climbing with Random Restart, Simulated Annealing, and Genetic Algorithm — applied to solving the classic 8 Queens problem. Beyond describing the computational modeling and one-dimensional board representation, this work presents an extensive empirical study (1,000 executions per algorithm) with randomly sampled parameters, systematically quantifying the individual impact of each hyperparameter on success rate, execution time, and solution quality.*

***Resumo.** Este artigo apresenta a implementação e análise comparativa de três algoritmos de busca e otimização — Subida de Encosta com Reinício Aleatório, Têmpera Simulada e Algoritmo Genético — aplicados à resolução do clássico problema das 8 rainhas. Além de descrever a modelagem computacional utilizada, este trabalho apresenta um estudo empírico extenso (1,000 execuções por algoritmo) com parâmetros amostrados aleatoriamente, quantificando sistematicamente o impacto isolado de cada hiperparâmetro sobre a taxa de sucesso, o tempo de execução e a qualidade da solução.*

---

## 1. Introdução

Este artigo apresenta o desenvolvimento e a análise de um sistema computacional voltado para a resolução do clássico problema das 8 rainhas. O desafio consiste em encontrar uma disposição para oito rainhas em um tabuleiro de xadrez 8×8 de forma que nenhuma delas esteja sob ataque mútuo, respeitando estritamente as restrições de linhas, colunas e diagonais. O código-fonte completo do projeto pode ser acessado em <https://github.com/RuanVasco/ai-projects/tree/main/8-queens-solver>.

Para solucionar este problema de otimização combinatória, foram implementadas e avaliadas três abordagens algorítmicas distintas: Subida de Encosta (*Hill Climbing*) acoplada ao mecanismo de Reinício Aleatório, Têmpera Simulada (*Simulated Annealing*) e um Algoritmo Genético. O trabalho detalha a modelagem matemática adotada — especificamente a redução do tabuleiro a vetores unidimensionais para ganho de performance — e o impacto do ajuste fino de parâmetros no comportamento de exploração e convergência de cada método.

## 2. Desenvolvimento

O problema das 8 rainhas consiste em posicionar oito rainhas em um tabuleiro de xadrez 8×8 de modo que nenhuma delas ataque outra (mesma linha, coluna ou diagonal). O espaço de busca para este problema, considerando a restrição de uma rainha por coluna, é de 8⁸ combinações. Para solucioná-lo, foram implementados três algoritmos de busca e otimização, cujas abordagens, configurações e resultados empíricos são detalhados a seguir.

### 2.1. Subida de Encosta (Hill Climbing)

Este algoritmo é uma heurística de busca local de natureza estritamente gulosa. A partir de um estado de tabuleiro atual, o algoritmo gera sua vizinhança completa — totalizando 56 vizinhos possíveis a cada passo — e transita iterativamente para o estado que apresenta a maior redução no número de ataques. Ao detectar um ótimo local, a técnica de **Reinício Aleatório** descarta o estado atual e reinicia a busca a partir de um novo estado estocástico.

#### Análise de parâmetros

Para quantificar o impacto individual de cada hiperparâmetro, foram realizadas 1,000 execuções com parâmetros sorteados aleatoriamente.

**Tabela 1.** Impacto de `max_reinicios` sobre o desempenho da Subida de Encosta.

| `max_reinicios` | N | Taxa de Sucesso | Tempo médio (ms) | Iters. médias | Reinícios médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 5 | 162 | 61.1% | 5.14 | 17.60 | 3.60 |
| 10 | 184 | 75.5% | 7.71 | 25.60 | 5.40 |
| 25 | 175 | 95.4% | 10.36 | 31.30 | 6.50 |
| 50 | 169 | 100.0% | 9.14 | 30.40 | 6.20 |
| 100 | 156 | 100.0% | 8.74 | 29.60 | 6.00 |
| 200 | 154 | 100.0% | 10.16 | 34.20 | 7.10 |

**Tabela 2.** Impacto de `max_passos_por_reinicio` sobre o desempenho da Subida de Encosta.

| `max_passos_por_reinicio` | N | Taxa de Sucesso | Tempo médio (ms) | Iters. médias | Reinícios médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 25 | 226 | 88.9% | 8.98 | 28.90 | 5.90 |
| 50 | 272 | 89.7% | 8.08 | 27.60 | 5.70 |
| 100 | 243 | 84.8% | 8.07 | 27.30 | 5.60 |
| 200 | 259 | 90.0% | 9.07 | 28.40 | 5.90 |

- **Configuração adotada:** Máximo de 100 reinícios e 200 passos por reinício.
- **Justificativa:** O comportamento de "serra" no gráfico de convergência indica que a estagnação é comum, mas o reinício rápido permite encontrar a solução global com baixo custo computacional. Com 100 reinícios, garante-se 100% de taxa de sucesso com ampla margem de segurança.

### 2.2. Têmpera Simulada (Simulated Annealing)

Inspirada no processo termodinâmico de recozimento físico de metais, esta meta-heurística permite transições ocasionais para estados piores segundo a probabilidade de Boltzmann P = e^(−Δ/T). Nas iterações iniciais, com T elevado, há ampla exploração do espaço de busca. Conforme T decresce, o algoritmo assume comportamento progressivamente mais guloso.

#### Análise de parâmetros

**Tabela 3.** Impacto de `temp_inicial` sobre o desempenho da Têmpera Simulada.

| `temp_inicial` | N | Taxa de Sucesso | Tempo médio (ms) | Iters. médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 10.0 | 193 | 45.6% | 7.39 | 1074.80 | 0.78 |
| 50.0 | 197 | 48.7% | 10.47 | 1538.30 | 0.79 |
| 100.0 | 216 | 42.1% | 8.76 | 1262.00 | 0.87 |
| 200.0 | 199 | 47.2% | 12.14 | 1781.20 | 0.78 |
| 500.0 | 195 | 44.1% | 14.43 | 2087.80 | 0.80 |

**Tabela 4.** Impacto de `taxa_resfriamento` sobre o desempenho da Têmpera Simulada.

| `taxa_resfriamento` | N | Taxa de Sucesso | Tempo médio (ms) | Iters. médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.9 | 203 | 2.0% | 0.61 | 87.00 | 1.92 |
| 0.95 | 181 | 11.0% | 1.20 | 174.80 | 1.25 |
| 0.99 | 201 | 45.8% | 5.47 | 803.40 | 0.54 |
| 0.995 | 213 | 77.0% | 9.78 | 1406.00 | 0.23 |
| 0.999 | 202 | 86.6% | 35.10 | 5120.80 | 0.16 |

**Tabela 5.** Impacto de `max_iteracoes` sobre o desempenho da Têmpera Simulada.

| `max_iteracoes` | N | Taxa de Sucesso | Tempo médio (ms) | Iters. médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 5000 | 251 | 34.7% | 8.76 | 1269.10 | 0.90 |
| 10000 | 252 | 50.4% | 10.32 | 1510.10 | 0.73 |
| 25000 | 249 | 49.4% | 12.35 | 1801.40 | 0.78 |
| 50000 | 248 | 47.6% | 11.04 | 1600.80 | 0.82 |

- **Configuração adotada:** Temperatura inicial 100,0 e taxa de resfriamento de 0,995.
- **Justificativa:** A taxa de 0,995 garante um resfriamento lento o suficiente para que o algoritmo explore o espaço antes de convergir. A taxa 0.999 oferece desempenho superior (86.6%), porém com custo temporal substancialmente maior; a taxa 0.9 resulta em apenas 2.0% de sucesso.

### 2.3. Algoritmo Genético

Baseado nos princípios da teoria da evolução, este método opera sobre uma população de soluções candidatas através de três operadores: **Seleção** por torneio, **Cruzamento** (*Crossover*) de ponto único e **Mutação** aleatória por gene. O elitismo preserva os melhores indivíduos entre gerações.

#### Análise de parâmetros

**Tabela 6.** Impacto de `tamanho_populacao` sobre o desempenho do Algoritmo Genético.

| `tamanho_populacao` | N | Taxa de Sucesso | Tempo médio (ms) | Gerações médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 20 | 256 | 25.4% | 161.02 | 314.90 | 0.98 |
| 50 | 253 | 45.8% | 380.15 | 292.50 | 0.60 |
| 100 | 247 | 55.9% | 552.72 | 211.00 | 0.48 |
| 200 | 244 | 63.1% | 888.15 | 170.80 | 0.37 |

**Tabela 7.** Impacto de `taxa_mutacao` sobre o desempenho do Algoritmo Genético.

| `taxa_mutacao` | N | Taxa de Sucesso | Tempo médio (ms) | Gerações médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.01 | 189 | 28.6% | 762.44 | 349.10 | 0.94 |
| 0.05 | 208 | 36.5% | 597.19 | 284.60 | 0.72 |
| 0.1 | 200 | 48.0% | 419.05 | 231.30 | 0.60 |
| 0.2 | 208 | 53.8% | 440.55 | 222.90 | 0.49 |
| 0.5 | 195 | 69.2% | 240.34 | 156.90 | 0.31 |

**Tabela 8.** Impacto de `taxa_cruzamento` sobre o desempenho do Algoritmo Genético.

| `taxa_cruzamento` | N | Taxa de Sucesso | Tempo médio (ms) | Gerações médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 0.5 | 249 | 49.8% | 472.70 | 256.50 | 0.61 |
| 0.7 | 242 | 43.0% | 546.20 | 283.30 | 0.67 |
| 0.9 | 251 | 43.0% | 503.41 | 247.20 | 0.66 |
| 1.0 | 258 | 53.1% | 443.36 | 209.00 | 0.51 |

**Tabela 9.** Impacto de `max_geracoes` sobre o desempenho do Algoritmo Genético.

| `max_geracoes` | N | Taxa de Sucesso | Tempo médio (ms) | Gerações médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 100 | 232 | 37.5% | 145.80 | 71.50 | 0.78 |
| 250 | 298 | 44.0% | 323.68 | 162.80 | 0.65 |
| 500 | 236 | 51.7% | 532.02 | 281.10 | 0.55 |
| 1000 | 234 | 56.8% | 1003.36 | 499.80 | 0.45 |

**Tabela 10.** Impacto de `n_elites` sobre o desempenho do Algoritmo Genético.

| `n_elites` | N | Taxa de Sucesso | Tempo médio (ms) | Gerações médias | Conflitos médios |
| :---: | :---: | :---: | :---: | :---: | :---: |
| 1 | 330 | 47.0% | 471.65 | 228.80 | 0.60 |
| 2 | 332 | 52.7% | 470.74 | 252.10 | 0.53 |
| 5 | 338 | 42.3% | 528.69 | 263.90 | 0.70 |

- **Configuração adotada:** População de 100 indivíduos, 90% de cruzamento e 5% de mutação.
- **Justificativa:** Esses valores garantem recombinação eficiente de boas características e evitam a convergência prematura. Os dados empíricos indicam que taxas de mutação maiores (0.5) oferecem desempenho superior (69.2% vs. 28.6% com taxa 0.01).

### 2.4. Resultados e Discussão

**Tabela 11.** Visão geral do desempenho médio dos algoritmos (1,000 execuções por algoritmo, parâmetros aleatórios).

| Algoritmo | Taxa de Sucesso | Tempo Médio (ms) |
|:---|:---:|:---:|
| Subida de Encosta | 88.4% | 8.54 |
| Têmpera Simulada | 45.5% | 10.61 |
| Algoritmo Genético | 47.3% | 490.63 |

A Subida de Encosta apresentou a maior taxa de sucesso média (88.4%), beneficiando-se fortemente de `max_reinicios` ≥ 50, que por si só garante 100% de taxa de sucesso. A Têmpera Simulada e o Algoritmo Genético apresentaram taxas similares no cenário de parâmetros aleatórios, reflexo da elevada sensibilidade desses algoritmos à qualidade do ajuste de hiperparâmetros.

### 2.5. Análise Comparativa: Vantagens e Desvantagens

**1. Subida de Encosta com Reinício Aleatório**

- **Vantagens:** Extremamente leve em termos de alocação de memória, mantendo e avaliando apenas um único estado ativo por vez. Com `max_reinicios` ≥ 50, atinge 100% de taxa de sucesso em tempo médio inferior a 10 ms. O mecanismo de reinício resolve a vulnerabilidade a ótimos locais de maneira simples e robusta para espaços de busca de pequeno a médio porte.
- **Desvantagens:** É um algoritmo "míope" e desprovido de memória sistêmica. Todo o progresso feito antes de um reinício é sumariamente descartado. Em problemas de dimensionalidade muito maior, os reinícios passariam a consumir tempo excessivo.

**2. Têmpera Simulada**

- **Vantagens:** Oferece um mecanismo matemático rigoroso para transitar pelas depressões do espaço de busca sem descartar o progresso alcançado. Com `taxa_resfriamento` = 0.999, alcança 86.6% de taxa de sucesso, mantendo a vantagem da busca local quanto ao baixo uso de memória.
- **Desvantagens:** Eficácia criticamente sensível à calibração de hiperparâmetros. Um ajuste inadequado da taxa de resfriamento pode arruinar a busca: com taxa de 0.9, a taxa de sucesso cai para 2.0%.

**3. Algoritmo Genético**

- **Vantagens:** Notável poder de exploração paralela, avaliando múltiplas regiões do espaço de busca simultaneamente. É a técnica mais resiliente contra ótimos locais, com desempenho crescente à medida que a população e o número de gerações aumentam.
- **Desvantagens:** Apresentou o maior custo computacional médio (490.63 ms), evidenciando o *overhead* de gerenciar populações inteiras a cada geração. Trata-se de uma ferramenta superdimensionada (*overkill*) para a escala do problema das 8 rainhas.

## 3. Conclusão

Para o problema das 8 rainhas, os métodos de busca local (Subida de Encosta e Têmpera Simulada) mostraram-se superiores em eficiência. O estudo empírico com 1,000 execuções por algoritmo revelou que a **Subida de Encosta com Reinício Aleatório** é a escolha mais equilibrada: com apenas 50 reinícios, garante 100% de taxa de sucesso em tempo médio inferior a 10 ms. A Têmpera Simulada demonstrou forte dependência da taxa de resfriamento — o parâmetro mais crítico do algoritmo —, com taxa de sucesso variando de 2.0% (resfriamento agressivo, 0.9) a 86.6% (resfriamento lento, 0.999). O Algoritmo Genético, embora melhore consistentemente com o aumento de população e número de gerações, permanece consideravelmente mais lento e, nesta escala de problema, superdimensionado. Conclui-se que a complexidade algorítmica deve ser proporcional à escala do problema: para as 8 rainhas, a simplicidade da Subida de Encosta com Reinício Aleatório supera em eficiência as abordagens mais sofisticadas.

## Referências
