#include <queue>
#include <set>
#include <map>
#include <algorithm>
#include <iostream>
#include <cmath>
#include <models/PuzzleBoard.h>
#include <models/Solver.h>

int Solver::get_tested_states() const {
    return this->last_tested_states;
}

std::vector<PuzzleBoard> Solver::solve_bfs(PuzzleBoard initial_board, PuzzleBoard goal_board) {
    std::queue<PuzzleBoard> queue; // fila para explorar os estados nível por nível
    std::set<std::vector<int>> visited; // conjunto para registrar estados visitados e evitar loops infinitos
    std::map<std::vector<int>, PuzzleBoard> parent_map; // mapa de ancestralidade para reconstruir a sequência de movimentos no final

    queue.push(initial_board); // inicializa as estruturas com o estado de origem
    visited.insert(initial_board.get_board());

    bool found = false;

    while (!queue.empty()) {
        PuzzleBoard current = queue.front();
        queue.pop();

        if (current.get_board() == goal_board.get_board()) {
            found = true;
            break;
        }

        for (const PuzzleBoard& neighbor : current.get_neighbors()) { // processa o vizinho apenas se ele for um estado inédito
            if (visited.find(neighbor.get_board()) == visited.end()) {
                visited.insert(neighbor.get_board());
                parent_map.insert({ neighbor.get_board(), current }); // cadastra o estado atual como pai do novo vizinho descoberto
                queue.push(neighbor);
            }
        }
    }

    this->last_tested_states = visited.size(); // salva o total de nós analisados para exibição nas estatísticas

    if (!found) {
        return {};
    }

    std::vector<PuzzleBoard> path;
    PuzzleBoard current = goal_board;
    path.push_back(current);

    while (current.get_board() != initial_board.get_board()) { // faz o caminho reverso da meta até o início consultando os pais
        current = parent_map.at(current.get_board());
        path.push_back(current);
    }

    std::reverse(path.begin(), path.end()); // inverte a ordem para que o caminho fique do início para a meta
    return path;
}

// Estrutura auxiliar para a Fila de Prioridade do A*
struct AStarNode {
    PuzzleBoard board;
    int g; // Custo do caminho até agora (distância percorrida)
    int h; // Custo estimado até a meta (heurística)

    // Sobrecarga do operador para ordenar a Fila de Prioridade (Min-Heap: menor f() no topo)
    bool operator>(const AStarNode& other) const {
        return (g + h) > (other.g + other.h);
    }
};

// Implementação da Heurística: Distância de Manhattan
int Solver::calculate_manhattan_distance(const PuzzleBoard& pb) const {
    const std::vector<int>& state = pb.get_board();
    int distance = 0;
    
    for (int i = 0; i < 9; i++) {
        int val = state[i];
        if (val != 0) { // O espaço vazio não entra no cálculo
            int current_row = i / 3;
            int current_col = i % 3;
            
            // O estado meta assumido é {1, 2, 3, 4, 5, 6, 7, 8, 0}
            int target_row = (val - 1) / 3;
            int target_col = (val - 1) % 3;
            
            distance += std::abs(current_row - target_row) + std::abs(current_col - target_col);
        }
    }
    return distance;
}

std::vector<PuzzleBoard> Solver::solve_astar(PuzzleBoard initial_board, PuzzleBoard goal_board) {
    std::priority_queue<AStarNode, std::vector<AStarNode>, std::greater<AStarNode>> pq;
    std::set<std::vector<int>> visited;
    std::map<std::vector<int>, PuzzleBoard> parent_map;
    std::map<std::vector<int>, int> g_score;

    int initial_h = calculate_manhattan_distance(initial_board);
    pq.push({initial_board, 0, initial_h});
    g_score[initial_board.get_board()] = 0;

    bool found = false;

    while (!pq.empty()) {
        AStarNode current_node = pq.top();
        pq.pop();
        PuzzleBoard current = current_node.board;

        if (visited.find(current.get_board()) != visited.end()) {
            continue;
        }

        if (current.get_board() == goal_board.get_board()) {
            found = true;
            break;
        }

        visited.insert(current.get_board());

        for (const PuzzleBoard& neighbor : current.get_neighbors()) {
            if (visited.find(neighbor.get_board()) != visited.end()) {
                continue;
            }

            int tentative_g = g_score[current.get_board()] + 1;
            
            if (g_score.find(neighbor.get_board()) == g_score.end() || tentative_g < g_score[neighbor.get_board()]) {
                g_score[neighbor.get_board()] = tentative_g;
                int h = calculate_manhattan_distance(neighbor);
                pq.push({neighbor, tentative_g, h});
                
                parent_map.insert_or_assign(neighbor.get_board(), current);
            }
        }
    }

    this->last_tested_states = visited.size();

    if (!found) {
        return {};
    }

    std::vector<PuzzleBoard> path;
    PuzzleBoard curr = goal_board;
    path.push_back(curr);

    while (curr.get_board() != initial_board.get_board()) {
        curr = parent_map.at(curr.get_board());
        path.push_back(curr);
    }

    std::reverse(path.begin(), path.end());
    return path;
}