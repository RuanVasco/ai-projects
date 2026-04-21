# Algoritmos de Busca Local — 8 Rainhas

O problema das 8 rainhas consiste em posicionar 8 rainhas num tabuleiro 8x8 sem que nenhuma se ataque. Os algoritmos abaixo são técnicas de **busca local**: partem de um estado inicial e tentam melhorá-lo iterativamente, sem explorar o espaço inteiro de soluções.

## Representação do tabuleiro

O tabuleiro é uma **lista de 8 inteiros**, onde:
- O **índice** representa a coluna (0–7)
- O **valor** representa a linha onde a rainha está (0–7)

```
estado = [2, 0, 6, 4, 7, 1, 3, 5]
           c0 c1 c2 c3 c4 c5 c6 c7
```

Isso garante que nunca há duas rainhas na mesma coluna. Os conflitos verificados são apenas de **linha** e **diagonal**.

O número máximo de pares sem conflito num tabuleiro 8x8 é **28** (C(8,2) = 28 pares de rainhas).

---

## 1. Subida de Encosta (Hill Climbing)

### Ideia

Imagine que você está perdido numa montanha com neblina e quer chegar ao topo. Sem enxergar longe, você olha apenas os arredores imediatos e dá um passo para o lugar mais alto. Se todos os passos ao redor forem para baixo, você para — mesmo que não esteja no topo de verdade.

No problema das 8 rainhas, "subir" significa **reduzir conflitos**.

### Como funciona

1. Começa com um tabuleiro aleatório
2. Avalia todos os **vizinhos** (mover qualquer rainha para qualquer outra linha da mesma coluna — 8 × 7 = 56 possibilidades)
3. Move para o vizinho com **menos conflitos**
4. Repete até não haver vizinho melhor (mínimo local) ou encontrar solução
5. Se travar, **reinicia** com um novo tabuleiro aleatório

### Problema: mínimos locais

O algoritmo trava quando nenhum vizinho é melhor, mesmo sem ter encontrado a solução ótima. A saída é reiniciar várias vezes (`max_reinicios`).

```
conflitos
    |
  5 |  *
  4 |    *
  3 |      *  ← trava aqui (mínimo local)
  2 |              *
  1 |                *
  0 |                  * ← solução real
    +-------------------→ iterações
```

### Parâmetros

| Parâmetro | Descrição |
|---|---|
| `max_reinicios` | Quantas vezes recomeça do zero |
| `max_passos_por_reinicio` | Limite de passos por tentativa |

---

## 2. Têmpera Simulada (Simulated Annealing)

### Ideia

Inspirado no processo metalúrgico de resfriar metal lentamente para que os átomos se organizem na estrutura mais estável. Quando o metal está **quente**, os átomos se movem livremente (aceitam qualquer posição). Conforme **esfria**, ficam mais rígidos (só aceitam posições melhores).

No algoritmo: no começo aceita movimentos piores (escapa de mínimos locais); no fim, só aceita melhoras (como Hill Climbing).

### Como funciona

1. Começa com um tabuleiro aleatório e uma temperatura alta
2. A cada iteração, escolhe um **vizinho aleatório** (não o melhor, só um qualquer)
3. Se o vizinho for melhor → aceita sempre
4. Se o vizinho for pior → aceita com probabilidade `e^(-delta/temperatura)`
5. Resfria a temperatura multiplicando por `taxa_resfriamento` (ex: 0.995)
6. Repete até encontrar solução, temperatura mínima ou limite de iterações

### A probabilidade de aceitar pioras

```
probabilidade = e^(-delta / temperatura)
```

- `delta` = quanto o vizinho é pior (conflitos a mais)
- Temperatura alta → probabilidade alta → aceita quase qualquer coisa
- Temperatura baixa → probabilidade baixa → só aceita se for bem parecido
- Delta grande → probabilidade menor → pioras grandes são menos aceitas

### Vantagem sobre Hill Climbing

Consegue **escapar de mínimos locais** sem precisar reiniciar, pois às vezes aceita um passo ruim para explorar outras regiões.

### Parâmetros

| Parâmetro | Descrição |
|---|---|
| `temp_inicial` | Temperatura de partida (controla ousadia inicial) |
| `taxa_resfriamento` | Fator de resfriamento por iteração (próximo de 1 = lento) |
| `temp_min` | Temperatura mínima para parar |
| `max_iteracoes` | Limite total de iterações |

---

## 3. Algoritmo Genético

### Ideia

Inspirado na evolução biológica. Em vez de trabalhar com **uma solução**, mantém uma **população** de soluções. As melhores se reproduzem (cruzamento), os filhos sofrem mutações aleatórias, e as piores são descartadas. Ao longo das gerações, a população evolui para soluções melhores.

### Como funciona

```
Geração 0: população aleatória
    ↓
Avaliar fitness de cada indivíduo
    ↓
Selecionar os melhores (torneio)
    ↓
Cruzar pares → gerar filhos
    ↓
Mutar filhos aleatoriamente
    ↓
Nova geração → repetir
```

### Etapas detalhadas

**Fitness:** Mede a qualidade de um indivíduo. Aqui: `fitness = 28 - conflitos`. Quanto maior, melhor. Fitness 28 = solução perfeita (zero conflitos).

**Seleção por torneio:** Escolhe K indivíduos aleatórios da população e retorna o de maior fitness. Dá mais chances aos melhores sem eliminar totalmente os piores.

**Cruzamento (crossover):** Combina dois pais escolhendo um ponto de corte aleatório:
```
pai1 = [3, 6, 2, | 7, 1, 4, 0, 5]
pai2 = [1, 0, 4, | 3, 6, 2, 5, 7]
                 ↓ corte na posição 3
filho1 = [3, 6, 2,   3, 6, 2, 5, 7]  ← início do pai1 + fim do pai2
filho2 = [1, 0, 4,   7, 1, 4, 0, 5]  ← início do pai2 + fim do pai1
```

**Mutação:** Com pequena probabilidade, troca a linha de uma rainha por outra aleatória. Evita que a população fique homogênea (convergência prematura).

**Elitismo:** Os N melhores indivíduos da geração atual passam direto para a próxima, sem cruzamento nem mutação. Garante que a melhor solução nunca seja perdida.

### Parâmetros

| Parâmetro | Descrição |
|---|---|
| `tamanho_populacao` | Quantos indivíduos por geração |
| `taxa_mutacao` | Probabilidade de mutar cada gene |
| `taxa_cruzamento` | Probabilidade de cruzar dois pais |
| `max_geracoes` | Limite de gerações |
| `n_elites` | Quantos melhores passam direto |

---

## Comparativo

| | Hill Climbing | Têmpera Simulada | Genético |
|---|---|---|---|
| Trabalha com | 1 solução | 1 solução | população de soluções |
| Escapa de mínimo local? | Só reiniciando | Sim (probabilidade) | Sim (diversidade genética) |
| Custo por iteração | Alto (avalia 56 vizinhos) | Baixo (1 vizinho aleatório) | Alto (avalia população inteira) |
| Aleatoriedade | No reinício | Na aceitação de pioras | Na seleção, cruzamento e mutação |
| Garantia de solução? | Não | Não | Não |
