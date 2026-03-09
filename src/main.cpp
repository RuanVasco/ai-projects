#include <iostream>
#include <vector>
#include <future>
#include "models/PuzzleBoard.h"
#include <models/Solver.h>
#include "raylib.h"
#include <string>
#include <ui/Button.h>

int main() {
    const int screenWidth = 850;
    const int screenHeight = 600;
    const int sidebarWidth = 250;
    const int cellSize = 200;

    InitWindow(screenWidth, screenHeight, "8 Puzzle Solver");
    SetTargetFPS(60);

    std::vector<int> initialState = { 1, 2, 3, 4, 0, 5, 7, 8, 6 };
    PuzzleBoard puzzle(3, initialState);
    Solver solver = Solver();

    Button btnInput(25, 50, 200, 50, "Set Initial State");
    Button btnShuffle(25, 120, 200, 50, "Shuffle");
    Button btnSolve(25, 190, 200, 50, "Solve");

    std::vector<PuzzleBoard> solutionPath;
    bool isAnimating = false;
    int currentStep = 0;
    bool isProcessing = false;
    std::future<std::vector<PuzzleBoard>> futureSolution;
    int framesCounter = 0;

    bool isModalOpen = false;
    std::string inputText = "";

    while (!WindowShouldClose()) {
        btnInput.update();
        btnShuffle.update();
        btnSolve.update();

        bool anyHovered = btnInput.get_is_hovered() || btnShuffle.get_is_hovered() || btnSolve.get_is_hovered();
        if (anyHovered && !isModalOpen) {
            SetMouseCursor(MOUSE_CURSOR_POINTING_HAND);
        }
        else {
            SetMouseCursor(MOUSE_CURSOR_DEFAULT);
        }

        if (isModalOpen) {
            int key = GetCharPressed();
            while (key > 0) {
                if ((key >= '0' && key <= '8') && inputText.length() < 9) {
                    if (inputText.find((char)key) == std::string::npos) {
                        inputText += (char)key;
                    }
                }
                key = GetCharPressed();
            }

            if (IsKeyPressed(KEY_BACKSPACE) && inputText.length() > 0) {
                inputText.pop_back();
            }

            if ((IsKeyPressed(KEY_ENTER) || IsKeyPressed(KEY_KP_ENTER)) && inputText.length() == 9) {
                std::vector<int> newState;
                for (char c : inputText) {
                    newState.push_back(c - '0');
                }
                puzzle = PuzzleBoard(3, newState);
                isModalOpen = false;
            }

            if (IsKeyPressed(KEY_ESCAPE)) {
                isModalOpen = false;
            }
        }
        else {
            if (btnInput.is_clicked() && !isAnimating && !isProcessing) {
                isModalOpen = true;
                inputText = "";
            }

            if (btnShuffle.is_clicked() && !isAnimating && !isProcessing) {
                for (int i = 0; i < 100; i++) {
                    std::vector<PuzzleBoard> neighbors = puzzle.get_neighbors();
                    int randomIndex = GetRandomValue(0, neighbors.size() - 1);
                    puzzle = neighbors[randomIndex];
                }
            }

            if (btnSolve.is_clicked() && !isAnimating && !isProcessing) {
                btnInput.set_disabled(true);
                btnShuffle.set_disabled(true);
                btnSolve.set_disabled(true);
                isProcessing = true;

                futureSolution = std::async(std::launch::async, &Solver::solve_bfs, &solver, puzzle);
            }
        }

        if (isProcessing) {
            if (futureSolution.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
                solutionPath = futureSolution.get();
                isProcessing = false;

                if (!solutionPath.empty()) {
                    isAnimating = true;
                    currentStep = 0;
                    framesCounter = 0;
                }
                else {
                    btnInput.set_disabled(false);
                    btnShuffle.set_disabled(false);
                    btnSolve.set_disabled(false);
                }
            }
        }

        if (isAnimating) {
            framesCounter++;
            if (framesCounter >= 30) {
                framesCounter = 0;
                if (currentStep < solutionPath.size() - 1) {
                    currentStep++;
                    puzzle = solutionPath[currentStep];
                }
                else {
                    isAnimating = false;
                    btnInput.set_disabled(false);
                    btnShuffle.set_disabled(false);
                    btnSolve.set_disabled(false);
                }
            }
        }

        BeginDrawing();
        ClearBackground(RAYWHITE);

        DrawRectangle(0, 0, sidebarWidth, screenHeight, LIGHTGRAY);
        btnInput.draw();
        btnShuffle.draw();
        btnSolve.draw();

        if (isProcessing) {
            DrawText("Processing...", 65, 260, 20, DARKBLUE);
        }

        const std::vector<int>& state = puzzle.get_board();

        for (int i = 0; i < 9; i++) {
            int row = i / 3;
            int col = i % 3;
            int value = state[i];

            int x = sidebarWidth + (col * cellSize);
            int y = row * cellSize;

            if (value != 0) {
                DrawRectangle(x + 5, y + 5, cellSize - 10, cellSize - 10, DARKBLUE);

                std::string text = std::to_string(value);
                int valueTextWidth = MeasureText(text.c_str(), 60);
                DrawText(text.c_str(), x + (cellSize - valueTextWidth) / 2, y + (cellSize - 60) / 2, 60, WHITE);
            }
            else {
                DrawRectangle(x + 5, y + 5, cellSize - 10, cellSize - 10, RAYWHITE);
            }
        }

        if (isModalOpen) {
            DrawRectangle(0, 0, screenWidth, screenHeight, Fade(BLACK, 0.8f));
            DrawRectangle(screenWidth / 2 - 200, screenHeight / 2 - 100, 400, 200, RAYWHITE);
            DrawText("Enter 9 unique digits (0-8):", screenWidth / 2 - 180, screenHeight / 2 - 80, 20, DARKGRAY);
            DrawText(inputText.c_str(), screenWidth / 2 - 180, screenHeight / 2 - 20, 40, DARKBLUE);
            DrawText("Press ENTER to confirm or ESC to cancel", screenWidth / 2 - 180, screenHeight / 2 + 50, 15, GRAY);
        }

        EndDrawing();
    }

    CloseWindow();
    return 0;
}