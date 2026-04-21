# Algoritmos de Busca Local — 8 Rainhas

O problema das 8 rainhas consiste em posicionar 8 rainhas num tabuleiro 8×8 sem que nenhuma se ataque. Os algoritmos abaixo são técnicas de **busca local**: partem de um estado inicial e tentam melhorá-lo iterativamente, sem explorar o espaço inteiro de soluções.

---

## Representação do tabuleiro — `board.py`

O tabuleiro é uma **lista de 8 inteiros**, onde o índice é a coluna e o valor é a linha da rainha:

```
estado = [2, 0, 6, 4, 7, 1, 3, 5]
           c0 c1 c2 c3 c4 c5 c6 c7
```

Isso garante que nunca há duas rainhas na mesma coluna. Os conflitos verificados são apenas de **linha** e **diagonal**.

### `estado_aleatorio`

```python
def estado_aleatorio() -> list[int]:
    return [random.randint(0, 7) for _ in range(8)]
```

Gera um tabuleiro inicial aleatório — cada coluna recebe uma linha entre 0 e 7. Não garante ausência de conflitos; é só o ponto de partida.

---

### `contar_conflitos`

```python
def contar_conflitos(estado: list[int]) -> int:
    conflitos = 0
    n = len(estado)
    for i in range(n):
        for j in range(i + 1, n):
            if estado[i] == estado[j]:          # mesma linha
                conflitos += 1
            if abs(estado[i] - estado[j]) == abs(i - j):  # mesma diagonal
                conflitos += 1
    return conflitos
```

Compara cada par de rainhas `(i, j)` exatamente uma vez (laço triangular). Duas rainhas se atacam se:
- estão na **mesma linha**: `estado[i] == estado[j]`
- estão na **mesma diagonal**: a diferença de linhas igual à diferença de colunas

O número máximo de pares é **28** (C(8,2)), logo a solução perfeita tem `contar_conflitos == 0`.

---

### `obter_vizinhos` e `melhor_vizinho`

```python
def obter_vizinhos(estado: list[int]) -> list[list[int]]:
    vizinhos = []
    for col in range(8):
        for linha in range(8):
            if linha != estado[col]:        # não inclui o próprio estado
                novo_estado = estado[:]
                novo_estado[col] = linha
                vizinhos.append(novo_estado)
    return vizinhos
```

Gera todos os estados alcançáveis movendo **uma rainha** para qualquer outra linha da sua coluna: 8 colunas × 7 linhas possíveis = **56 vizinhos**.

```python
def melhor_vizinho(estado: list[int]) -> tuple[list[int], int]:
    vizinhos = obter_vizinhos(estado)
    conflitos_vizinhos = [(v, contar_conflitos(v)) for v in vizinhos]
    min_conflitos = min(c for _, c in conflitos_vizinhos)
    melhores = [v for v, c in conflitos_vizinhos if c == min_conflitos]
    escolhido = random.choice(melhores)
    return escolhido, min_conflitos
```

Avalia todos os 56 vizinhos e retorna o de **menor número de conflitos**. Se houver empate, escolhe aleatoriamente entre os melhores — isso evita que o algoritmo fique preso sempre no mesmo caminho.

---

### `vizinho_aleatorio`

```python
def vizinho_aleatorio(estado: list[int]) -> list[int]:
    novo_estado = estado[:]
    col = random.randint(0, 7)
    linha_atual = estado[col]
    nova_linha = random.choice([r for r in range(8) if r != linha_atual])
    novo_estado[col] = nova_linha
    return novo_estado
```

Escolhe **uma coluna aleatória** e move sua rainha para uma linha diferente também aleatória. Usado pela Têmpera Simulada, que não precisa avaliar todos os vizinhos.

---

## 1. Subida de Encosta — `hill_climbing.py`

### Ideia

Imagine que você está perdido numa montanha com neblina e quer chegar ao topo. Sem enxergar longe, você olha apenas os arredores imediatos e dá um passo para o lugar mais alto. Se todos os passos ao redor forem para baixo, você para — mesmo que não esteja no topo de verdade.

No problema das 8 rainhas, "subir" significa **reduzir conflitos**.

### Código completo

```python
def subida_encosta(
    max_reinicios: int = 100,
    max_passos_por_reinicio: int = 200,
    semente: int | None = None,
) -> dict:
    if semente is not None:
        random.seed(semente)

    inicio = time.perf_counter()
    reinicios = 0
    total_iteracoes = 0
    historico_conflitos = []

    melhor_global = estado_aleatorio()
    melhor_conflitos_global = contar_conflitos(melhor_global)

    for _ in range(max_reinicios + 1):
        estado_atual = estado_aleatorio()           # (1) novo ponto de partida
        conflitos_atual = contar_conflitos(estado_atual)

        for _ in range(max_passos_por_reinicio):
            historico_conflitos.append(conflitos_atual)
            total_iteracoes += 1

            if conflitos_atual == 0:                # (2) solução encontrada
                tempo_ms = (time.perf_counter() - inicio) * 1000
                return { "sucesso": True, ... }

            proximo_estado, conflitos_proximo = melhor_vizinho(estado_atual)  # (3)

            if conflitos_proximo >= conflitos_atual:   # (4) mínimo local
                break

            estado_atual = proximo_estado
            conflitos_atual = conflitos_proximo

        if conflitos_atual < melhor_conflitos_global:  # (5) guarda o melhor
            melhor_global = estado_atual
            melhor_conflitos_global = conflitos_atual

        reinicios += 1

    tempo_ms = (time.perf_counter() - inicio) * 1000
    return { "sucesso": False, "solucao": melhor_global, ... }
```

### Explicação passo a passo

| Passo | O que acontece |
|---|---|
| **(1)** `estado_aleatorio()` | Cada reinício gera um tabuleiro novo. Sem isso, o algoritmo travaria sempre no mesmo mínimo local. |
| **(2)** `conflitos_atual == 0` | Verifica a solução logo no início do laço interno — retorna imediatamente ao encontrar. |
| **(3)** `melhor_vizinho` | Avalia todos os 56 vizinhos e retorna o de menor conflito. Custo fixo por iteração: 56 avaliações. |
| **(4)** `conflitos_proximo >= conflitos_atual` | Se nenhum vizinho for melhor, estamos num mínimo local. O `break` sai do laço interno e dispara um reinício. |
| **(5)** guarda o melhor global | Mesmo sem encontrar solução, mantém o tabuleiro com menos conflitos entre todos os reinícios. |

### Problema: mínimos locais

```
conflitos
    |
  5 |  *
  4 |    *
  3 |      *  ← trava aqui (nenhum vizinho é melhor)
  2 |              *
  1 |                *
  0 |                  * ← solução real
    +-------------------→ iterações
```

A saída é reiniciar com `max_reinicios` tentativas diferentes.

### Parâmetros

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `max_reinicios` | 100 | Quantas vezes recomeça do zero |
| `max_passos_por_reinicio` | 200 | Limite de passos por tentativa |

---

## 2. Têmpera Simulada — `simulated_annealing.py`

### Ideia

Inspirado no processo metalúrgico de resfriar metal lentamente. Quando quente, os átomos se movem livremente (aceitam qualquer posição). Conforme esfria, ficam rígidos (só aceitam melhoras). No algoritmo: no começo aceita movimentos piores para **escapar de mínimos locais**; no fim, comporta-se como Hill Climbing.

### Código completo

```python
def tempera_simulada(
    temp_inicial: float = 100.0,
    taxa_resfriamento: float = 0.995,
    temp_min: float = 0.01,
    max_iteracoes: int = 50_000,
    semente: int | None = None,
) -> dict:
    ...
    estado_atual = estado_aleatorio()
    conflitos_atual = contar_conflitos(estado_atual)

    melhor_estado = estado_atual[:]
    melhor_conflitos = conflitos_atual
    temperatura = temp_inicial

    for iteracao in range(max_iteracoes):
        if conflitos_atual == 0:     # (1) solução encontrada
            break
        if temperatura < temp_min:   # (2) resfriou demais, para
            break

        vizinho = vizinho_aleatorio(estado_atual)      # (3) um vizinho qualquer
        conflitos_vizinho = contar_conflitos(vizinho)

        delta = conflitos_vizinho - conflitos_atual    # (4) diferença

        if delta < 0:                                  # (5) vizinho é melhor
            estado_atual = vizinho
            conflitos_atual = conflitos_vizinho
        else:
            probabilidade = math.exp(-delta / temperatura)  # (6)
            if random.random() < probabilidade:
                estado_atual = vizinho
                conflitos_atual = conflitos_vizinho

        if conflitos_atual < melhor_conflitos:         # (7) guarda o melhor
            melhor_estado = estado_atual[:]
            melhor_conflitos = conflitos_atual

        temperatura *= taxa_resfriamento               # (8) resfria
```

### Explicação passo a passo

| Passo | O que acontece |
|---|---|
| **(1)(2)** condições de parada | Para ao encontrar solução ou ao resfriar demais (abaixo de `temp_min`). |
| **(3)** `vizinho_aleatorio` | Ao contrário do Hill Climbing, escolhe **um vizinho aleatório** — não avalia todos. Custo constante e muito menor. |
| **(4)** `delta` | Positivo = vizinho tem mais conflitos (pior). Negativo = vizinho é melhor. |
| **(5)** `delta < 0` | Movimento de melhora: aceita sempre. |
| **(6)** `math.exp(-delta / temperatura)` | A chave do algoritmo: probabilidade de aceitar uma piora. Com temperatura alta, `exp` ≈ 1 → aceita quase tudo. Com temperatura baixa, `exp` ≈ 0 → recusa pioras. |
| **(7)** guarda o melhor | O estado atual pode piorar depois de aceitar uma piora, então mantém separado o melhor estado já visto. |
| **(8)** `temperatura *= taxa_resfriamento` | Com `taxa_resfriamento = 0.995`, a temperatura cai ~1% por iteração. Em 50 000 iterações, vai de 100 a `100 × 0.995^50000 ≈ 0`. |

### A fórmula da probabilidade

```
probabilidade = e^(-delta / temperatura)
```

| delta | temperatura | probabilidade |
|---|---|---|
| 1 (piora pequena) | 100 (quente) | e^(-0.01) ≈ 0.99 → quase sempre aceita |
| 1 (piora pequena) | 1 (frio) | e^(-1) ≈ 0.37 → aceita ~37% das vezes |
| 5 (piora grande) | 1 (frio) | e^(-5) ≈ 0.007 → raramente aceita |

### Parâmetros

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `temp_inicial` | 100.0 | Temperatura de partida |
| `taxa_resfriamento` | 0.995 | Fator de resfriamento por iteração (próximo de 1 = resfria devagar) |
| `temp_min` | 0.01 | Temperatura mínima para parar |
| `max_iteracoes` | 50 000 | Limite total de iterações |

---

## 3. Algoritmo Genético — `genetic.py`

### Ideia

Inspirado na evolução biológica. Em vez de trabalhar com uma solução, mantém uma **população** de soluções. As melhores se reproduzem, os filhos sofrem mutações, e as piores são descartadas. Ao longo das gerações, a população converge para soluções melhores.

### Funções auxiliares

#### `_fitness`

```python
def _fitness(individuo: list[int]) -> int:
    return 28 - contar_conflitos(individuo)
```

Converte conflitos em qualidade: `fitness = 28 - conflitos`. Quanto **maior** o fitness, melhor. `fitness == 28` significa solução perfeita (zero conflitos).

---

#### `_selecao_torneio`

```python
def _selecao_torneio(populacao: list[list[int]], k: int = 3) -> list[int]:
    participantes = random.choices(populacao, k=k)
    return max(participantes, key=_fitness)
```

Escolhe `k=3` indivíduos aleatórios da população e retorna o de maior fitness. Vantagem sobre simplesmente pegar o melhor global: os piores ainda têm chance de ser selecionados, mantendo diversidade genética.

---

#### `_cruzamento`

```python
def _cruzamento(pai1: list[int], pai2: list[int]) -> tuple[list[int], list[int]]:
    ponto_corte = random.randint(1, 7)
    filho1 = pai1[:ponto_corte] + pai2[ponto_corte:]
    filho2 = pai2[:ponto_corte] + pai1[ponto_corte:]
    return filho1, filho2
```

Escolhe um ponto de corte aleatório e combina os dois pais:

```
pai1 = [3, 6, 2, | 7, 1, 4, 0, 5]   ponto_corte = 3
pai2 = [1, 0, 4, | 3, 6, 2, 5, 7]
                 ↓
filho1 = [3, 6, 2,  3, 6, 2, 5, 7]  ← início do pai1 + fim do pai2
filho2 = [1, 0, 4,  7, 1, 4, 0, 5]  ← início do pai2 + fim do pai1
```

Cada filho herda características de ambos os pais — explora combinações que nenhum dos dois tinha.

---

#### `_mutacao`

```python
def _mutacao(individuo: list[int], taxa: float) -> list[int]:
    mutado = individuo[:]
    for i in range(8):
        if random.random() < taxa:
            valor_atual = mutado[i]
            nova_linha = random.choice([r for r in range(8) if r != valor_atual])
            mutado[i] = nova_linha
    return mutado
```

Para cada coluna, com probabilidade `taxa` (padrão 5%), troca a rainha por outra linha aleatória. Evita que a população inteira convirja para os mesmos genes (**convergência prematura**).

---

### Loop principal

```python
def algoritmo_genetico(...) -> dict:
    populacao = _inicializar_populacao(tamanho_populacao)  # (1)

    for geracao in range(max_geracoes):
        populacao.sort(key=_fitness, reverse=True)         # (2) ordena por fitness

        melhor_da_geracao = populacao[0]
        if _fitness(melhor_da_geracao) == 28:              # (3) solução perfeita
            break

        nova_populacao = [ind[:] for ind in populacao[:n_elites]]  # (4) elitismo

        while len(nova_populacao) < tamanho_populacao:
            pai1 = _selecao_torneio(populacao)             # (5) seleção
            pai2 = _selecao_torneio(populacao)

            if random.random() < taxa_cruzamento:
                filho1, filho2 = _cruzamento(pai1, pai2)   # (6) cruzamento
            else:
                filho1, filho2 = pai1[:], pai2[:]

            filho1 = _mutacao(filho1, taxa_mutacao)        # (7) mutação
            filho2 = _mutacao(filho2, taxa_mutacao)

            nova_populacao.append(filho1)
            if len(nova_populacao) < tamanho_populacao:
                nova_populacao.append(filho2)

        populacao = nova_populacao                         # (8) próxima geração
```

### Explicação passo a passo

| Passo | O que acontece |
|---|---|
| **(1)** inicializa | Cria `tamanho_populacao` tabuleiros aleatórios. |
| **(2)** ordena | Coloca os melhores no início — facilita o elitismo e o diagnóstico. |
| **(3)** critério de parada | `fitness == 28` equivale a zero conflitos: solução encontrada. |
| **(4)** elitismo | Os `n_elites` melhores passam direto para a próxima geração sem alterar. Garante que a melhor solução nunca é perdida por azar na mutação. |
| **(5)** seleção | `_selecao_torneio` escolhe pais bons mas não sempre os mesmos, preservando diversidade. |
| **(6)** cruzamento | Com probabilidade `taxa_cruzamento` (padrão 90%) os pais cruzam; caso contrário, os filhos são cópias dos pais. |
| **(7)** mutação | Introduz variações aleatórias nos filhos para explorar regiões do espaço não alcançadas pelo cruzamento. |
| **(8)** substitui | A nova geração **substitui completamente** a anterior (exceto os elites). |

### Parâmetros

| Parâmetro | Padrão | Descrição |
|---|---|---|
| `tamanho_populacao` | 100 | Quantos indivíduos por geração |
| `taxa_mutacao` | 0.05 | Probabilidade de mutar cada gene (5%) |
| `taxa_cruzamento` | 0.9 | Probabilidade de cruzar dois pais (90%) |
| `max_geracoes` | 1 000 | Limite de gerações |
| `n_elites` | 2 | Quantos melhores passam direto |

---

## Comparativo

| | Hill Climbing | Têmpera Simulada | Genético |
|---|---|---|---|
| Trabalha com | 1 solução | 1 solução | população de soluções |
| Escapa de mínimo local? | Só reiniciando | Sim (probabilidade) | Sim (diversidade genética) |
| Vizinhos avaliados por iteração | 56 (todos) | 1 (aleatório) | toda a população |
| Aleatoriedade | No reinício | Na aceitação de pioras | Seleção, cruzamento e mutação |
| Garantia de solução? | Não | Não | Não |
