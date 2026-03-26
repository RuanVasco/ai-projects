# Implementação do Algoritmo de Busca em Largura e A* para o Problema do 8 Puzzle

Este repositório contém o código-fonte e a documentação referentes ao trabalho prático de implementação dos algoritmos de Busca em Largura (Breadth-First Search - BFS) e Busca Heurística (A*) aplicados à resolução do problema do 8-Puzzle para a disciplina de Inteligência Artificial, ministrada pelo professor Andrws Vieira, do Instituto Federal de Ciência, Tecnologia e Educação do Rio Grande do Sul - Campus Ibirubá.

O problema do 8-Puzzle consiste em um quebra-cabeça deslizante, composto por uma grade 3x3 contendo 8 peças numeradas (de 1 a 8) e um espaço vazio, representado pelo dígito 0. O objetivo do algoritmo é calcular a sequência ótima de movimentos para transitar de um estado inicial arbitrário até o estado final (meta), minimizando o número de transições.

## 1. Disponibilidade e Execução

Para fins de avaliação e validação, uma versão compilada do software foi disponibilizada. 

* **Arquivo Executável:** [8_puzzle_solver.exe (v1.0.1)](https://github.com/RuanVasco/8-puzzle-solver/releases/tag/1.0.1)

A execução deste arquivo em ambiente Windows dispensa a necessidade de configuração prévia de compiladores ou bibliotecas.

## 2. Instruções de Compilação (Código-Fonte)

O projeto foi desenvolvido na linguagem C++ e faz uso da biblioteca gráfica `raylib` para a renderização da interface e visualização das soluções. 

**Pré-requisitos:**
* Compilador com suporte ao padrão C++11 ou superior (GCC/MinGW, Clang ou MSVC).
* Biblioteca [raylib](https://www.raylib.com/) devidamente instalada e vinculada ao *path* do compilador.

*(Nota: Insira aqui os comandos exatos de compilação utilizados no seu ambiente, como por exemplo: `g++ -o solver main.cpp ui/*.cpp models/*.cpp -lraylib -lGL -lm -lpthread -ldl -lrt -lX11`)*

## 3. Especificação de Entrada e Saída

O software foi projetado para receber o estado inicial e fornecer os resultados de forma interativa e visual, cumprindo os requisitos de formatação exigidos.

### 3.1. Entrada de Dados
A inserção do estado inicial é realizada via interface gráfica:
1. Acione a função "Definir Estado Inicial" (Set Initial State).
2. Insira uma sequência linear de 9 dígitos únicos, compreendidos entre 0 e 8, onde 0 denota o espaço vazio.
3. Alternativamente, é suportada a inserção via área de transferência (`Ctrl+V`). Exemplo de entrada válida: `123456708`.
4. Pressione `ENTER` para confirmar a configuração do tabuleiro.

### 3.2. Saída de Dados e Visualização
Após o acionamento da função "Resolver", o sistema apresenta:
* **Animação da Solução:** Transição gráfica passo a passo do tabuleiro, desde o estado inicial até a meta.
* **Métricas de Desempenho:** Exibição do número total de movimentos requeridos (passos) e do número absoluto de estados testados (nós expandidos na árvore de busca).
* **Árvore da Solução (Visualização Gráfica):** Uma interface dedicada que mapeia visualmente a sequência completa de estados (caminho ótimo) gerada pelo algoritmo, atendendo ao critério de diferencial qualitativo.

### 3.3. Exemplos de Execução

Abaixo estão exemplos do software em funcionamento:

* **Tela Inicial e Inserção de Dados:**
  ![Inserção de Dados](./assets/main_screen.png)
  ![Inserção de Dados](./assets/set_initial_state.png)

* **Processamento e Animação da Solução:**
  ![Animação](./assets/solved.png)

* **Árvore da Solução (Visualização do Caminho):**
  ![Árvore da Solução](./assets/view_tree.png)

## 4. Metodologia de Implementação (Busca em Largura e A*)

O projeto suporta duas abordagens fundamentais em Inteligência Artificial para a resolução do problema: uma busca cega (BFS) e uma busca informada (A*).

### 4.1 Busca em Largura (BFS)
A BFS foi implementada de forma a garantir a completude e a otimalidade da solução de forma exaustiva. 
* **`std::queue<PuzzleBoard>`:** A propriedade FIFO assegura a exploração do espaço de estados estritamente nível por nível.
* **`std::set<std::vector<int>>`:** Conjunto para armazenar tabuleiros visitados, prevenindo ciclos e otimizando a memória.

### 4.2 Busca Heurística (A*)


[Image of A* search algorithm flowchart]

Para elevar a eficiência computacional e reduzir a quantidade de estados testados, foi incorporado o algoritmo **A***. Ele avalia os nós com base na função de custo $f(n) = g(n) + h(n)$, onde $g(n)$ é o custo real (número de movimentos) e $h(n)$ é a estimativa até a meta.

* **Heurística (Distância de Manhattan):** A heurística escolhida foi a Distância de Manhattan. Ela calcula a soma das distâncias horizontais e verticais que cada peça está de sua posição final correta. Como ela é uma heurística *admissível* (nunca superestima o custo real), o A* continua garantindo a descoberta do caminho mais curto.
* **Eficiência e Poda:**
Foi utilizada uma `std::priority_queue` (Fila de Prioridade em formato Min-Heap) para ordenar os estados. Dessa forma, o algoritmo prioriza ramificações que se aproximam visual e matematicamente da solução. Isso reduz drasticamente os estados abertos em memória, resolvendo cenários complexos de forma substancialmente mais rápida que a BFS.

### 4.3 Estruturas Comuns
* **`std::map<std::vector<int>, PuzzleBoard>`:** Utilizado por ambos os algoritmos para mapear a ancestralidade e reconstruir o caminho de movimentos (*backtracking*).
* **Processamento Assíncrono (`std::async`):** Os cálculos são realizados em threads secundárias para não bloquear a renderização gráfica (`raylib`).

## 5. Recursos Adicionais

* **Geração Estocástica (Shuffle):** Permite a criação de estados iniciais pseudoaleatórios válidos através da aplicação de transições randômicas a partir da meta.
* **Suporte Bilíngue:** A interface suporta alternância em tempo real entre os idiomas Português (PT) e Inglês (EN).

---
**Desenvolvido por:** Ruan Vasconcelos e Caetano Matos