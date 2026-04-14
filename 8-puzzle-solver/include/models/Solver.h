#pragma once
#include <vector>
#include "PuzzleBoard.h"

class Solver {
private:
    int last_tested_states;
    int calculate_manhattan_distance(const PuzzleBoard& board) const;
public:
    std::vector<PuzzleBoard> solve_bfs(PuzzleBoard initial_board, PuzzleBoard goal_board);
        std::vector<PuzzleBoard> solve_astar(PuzzleBoard initial_board, PuzzleBoard goal_board);
    
    int get_tested_states() const;
};