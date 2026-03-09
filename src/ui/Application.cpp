#include "ui/Application.h"
#include <iostream>

Application::Application()
    : screenWidth(850), screenHeight(600), sidebarWidth(250), cellSize(200),
    puzzle(3, { 1, 2, 3, 4, 0, 5, 7, 8, 6 }), solver(),
    btnInput(25, 50, 200, 50, "Set Initial State"),
    btnShuffle(25, 120, 200, 50, "Shuffle"),
    btnSolve(25, 190, 200, 50, "Solve"),
    isAnimating(false), isProcessing(false), isSolved(false), isModalOpen(false),
    currentStep(0), framesCounter(0), testedStates(0) {

    InitWindow(screenWidth, screenHeight, "8 Puzzle Solver");
    SetTargetFPS(60);
    SetExitKey(KEY_NULL);
}

Application::~Application() {
    CloseWindow();
}

void Application::run() {
    while (!WindowShouldClose()) {
        handleEvents();
        updateLogic();
        render();
    }
}

void Application::handleEvents() {
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
        handleModalInput();
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
            isSolved = false;
        }

        if (btnSolve.is_clicked() && !isAnimating && !isProcessing) {
            btnInput.set_disabled(true);
            btnShuffle.set_disabled(true);
            btnSolve.set_disabled(true);
            isProcessing = true;
            isSolved = false;
            futureSolution = std::async(std::launch::async, &Solver::solve_bfs, &solver, puzzle);
        }
    }
}

void Application::pasteFromClipboard() {
    const char* clipboardText = GetClipboardText();
    if (clipboardText != nullptr) {
        std::string pasted(clipboardText);
        for (char c : pasted) {
            if (c >= '0' && c <= '8' && inputText.length() < 9) {
                if (inputText.find(c) == std::string::npos) {
                    inputText += c;
                }
            }
        }
    }
}

void Application::handleModalInput() {
    if ((IsKeyDown(KEY_LEFT_CONTROL) || IsKeyDown(KEY_RIGHT_CONTROL)) && IsKeyPressed(KEY_V)) {
        pasteFromClipboard();
    }

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
        isSolved = false;
    }

    if (IsKeyPressed(KEY_ESCAPE)) {
        isModalOpen = false;
    }
}

void Application::updateLogic() {
    if (isProcessing) {
        if (futureSolution.wait_for(std::chrono::seconds(0)) == std::future_status::ready) {
            solutionPath = futureSolution.get();
            isProcessing = false;
            testedStates = solver.get_tested_states();
            isSolved = true;

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
}

void Application::renderSidebar() {
    DrawRectangle(0, 0, sidebarWidth, screenHeight, LIGHTGRAY);
    btnInput.draw();
    btnShuffle.draw();
    btnSolve.draw();

    if (isSolved) {
        std::string statesText = "Tested States: " + std::to_string(testedStates);
        DrawText(statesText.c_str(), 25, 260, 20, DARKGRAY);

        if (solutionPath.empty()) {
            DrawText("UNSOLVABLE", 25, 290, 20, RED);
        }
    }

    if (isProcessing) {
        DrawText("Processing...", 25, 260, 20, DARKBLUE);
    }
}

void Application::renderBoard() {
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
}

void Application::renderModal() {
    DrawRectangle(0, 0, screenWidth, screenHeight, Fade(BLACK, 0.8f));
    DrawRectangle(screenWidth / 2 - 200, screenHeight / 2 - 100, 400, 200, RAYWHITE);
    DrawText("Enter 9 unique digits (0-8):", screenWidth / 2 - 180, screenHeight / 2 - 80, 20, DARKGRAY);
    DrawText(inputText.c_str(), screenWidth / 2 - 180, screenHeight / 2 - 20, 40, DARKBLUE);
    DrawText("Press ENTER to confirm or ESC to cancel", screenWidth / 2 - 180, screenHeight / 2 + 50, 15, GRAY);
}

void Application::render() {
    BeginDrawing();
    ClearBackground(RAYWHITE);

    renderSidebar();
    renderBoard();

    if (isModalOpen) {
        renderModal();
    }

    EndDrawing();
}