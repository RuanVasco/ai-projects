#include <iostream>
#include <vector>
#include "models/PuzzleBoard.h"
#include <models/Solver.h>
#include "raylib.h"
#include <string>

int main() {
    const int screenWidth = 600;
    const int screenHeight = 600;
    const int cellSize = 200;

    InitWindow(screenWidth, screenHeight, "8 Puzzle Solver");
    SetTargetFPS(60);

    std::vector<int> initialState = { 1, 2, 3, 4, 0, 5, 7, 8, 6 };
    PuzzleBoard puzzle(3, initialState);

    while (!WindowShouldClose()) {
        BeginDrawing();
        ClearBackground(RAYWHITE);

        const std::vector<int>& state = puzzle.get_board();

        for (int i = 0; i < 9; i++) {
            int row = i / 3;
            int col = i % 3;
            int value = state[i];

            int x = col * cellSize;
            int y = row * cellSize;

            if (value != 0) {
                DrawRectangle(x + 5, y + 5, cellSize - 10, cellSize - 10, DARKBLUE);

                std::string text = std::to_string(value);
                int textWidth = MeasureText(text.c_str(), 60);
                DrawText(text.c_str(), x + (cellSize - textWidth) / 2, y + (cellSize - 60) / 2, 60, WHITE);
            }
            else {
                DrawRectangle(x + 5, y + 5, cellSize - 10, cellSize - 10, LIGHTGRAY);
            }
        }

        EndDrawing();
    }

    CloseWindow();
    return 0;
}