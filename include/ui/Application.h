#pragma once
#include <models/PuzzleBoard.h>
#include <models/Solver.h>
#include "Button.h"
#include <future>

class Application {
private:
	int screenWidth;
	int screenHeight;
	int sidebarWidth;
	int cellSize;

	PuzzleBoard puzzle;
	Solver solver;

	Button btnInput;
	Button btnShuffle;
	Button btnSolve;

	std::vector<PuzzleBoard> solutionPath;
	std::future<std::vector<PuzzleBoard>> futureSolution;

	bool isAnimating;
	bool isProcessing;
	bool isSolved;
	bool isModalOpen;

	int currentStep;
	int framesCounter;
	int testedStates;

	std::string inputText;

	void handleEvents();
	void handleModalInput();
	void pasteFromClipboard();
	void updateLogic();
	void render();
	void renderSidebar();
	void renderBoard();
	void renderModal();

public:
	Application();
	~Application();
	void run();
};