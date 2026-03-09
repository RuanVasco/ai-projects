#include <ui/Button.h>

Button::Button(float x, float y, float width, float height, const std::string& text) {
    this->bounds = { x, y, width, height };
    this->text = text;
    this->normalColor = DARKPURPLE;
    this->hoverColor = PURPLE;
    this->isHovered = false;
}

bool Button::is_clicked() {
    Vector2 mousePoint = GetMousePosition();
    this->isHovered = CheckCollisionPointRec(mousePoint, bounds);

    if (this->isHovered && IsMouseButtonReleased(MOUSE_BUTTON_LEFT)) {
        return true;
    }
    return false;
}

void Button::draw() const {
    Color currentColor = isHovered ? hoverColor : normalColor;
    DrawRectangleRec(bounds, currentColor);

    int textWidth = MeasureText(text.c_str(), 30);
    DrawText(text.c_str(), bounds.x + (bounds.width - textWidth) / 2, bounds.y + 10, 30, WHITE);
}