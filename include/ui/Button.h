#pragma once
#include "raylib.h"
#include <string>

class Button {
private:
	Rectangle bounds;
	std::string text;
	Color normalColor;
	Color hoverColor;
	bool isHovered;
public:
	Button(float x, float y, float width, float height, const std::string& text);
	bool is_clicked();
	void draw() const;
};