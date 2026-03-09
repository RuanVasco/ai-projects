#include <queue>
#include <set>
#include <map>
#include <algorithm>
#include <iostream>
#include <models/PuzzleBoard.h>
#include <models/Solver.h>

int Solver::get_tested_states() const {
    return this->last_tested_states;
}

std::vector<PuzzleBoard> Solver::solve_bfs(PuzzleBoard initial_board) {
    std::queue<PuzzleBoard> queue;
    std::set<std::vector<int>> visited;
    std::map<std::vector<int>, PuzzleBoard> parent_map;

    queue.push(initial_board);
    visited.insert(initial_board.get_board());

    bool found = false;
    PuzzleBoard goal_board = initial_board;

    while (!queue.empty()) {
        PuzzleBoard current = queue.front();
        queue.pop();

        if (current.is_goal()) {
            goal_board = current;
            found = true;
            break;
        }

        for (const PuzzleBoard& neighbor : current.get_neighbors()) {
            if (visited.find(neighbor.get_board()) == visited.end()) {
                visited.insert(neighbor.get_board());
                parent_map.insert({ neighbor.get_board(), current });
                queue.push(neighbor);
            }
        }
    }

    this->last_tested_states = visited.size();
    std::cout << ">>> Total states tested: " << this->last_tested_states << " <<<" << std::endl;

    if (!found) {
        return {};
    }

    std::vector<PuzzleBoard> path;
    PuzzleBoard current = goal_board;
    path.push_back(current);

    while (current.get_board() != initial_board.get_board()) {
        current = parent_map.at(current.get_board());
        path.push_back(current);
    }

    std::reverse(path.begin(), path.end());
    return path;
}