#ifndef SERIAL_GRAPHICS_H
#define SERIAL_GRAPHICS_H

#include <stdio.h>
#include <stdlib.h> 
#include "pico/stdlib.h"

// Define colors 
#define BLACK 0
#define WHITE 1
#define RED 2
#define GREEN 3
#define BLUE 4
#define YELLOW 5
#define CYAN 6
#define MAGENTA 7
#define DARK_BLUE 20
#define LIGHT_BLUE 40
#define DARK_GREEN 50
#define LIGHT_PINK 250

// Globals for text
static int cursor_x = 0;
static int cursor_y = 0;
static int text_color = WHITE;

static inline void initVGA() {
    stdio_init_all();
    sleep_ms(2000); 
}

// --- Drawing Functions ---

// *** FIX 1: Allow Black Pixels (The Eraser) ***
static inline void drawPixel(int x, int y, char color) {
    // We removed "if (color != BLACK)" so it can now erase!
    printf("P,%d,%d,%d\n", x, y, color);
}

static inline void fillRect(int x, int y, int w, int h, char color) {
    printf("R,%d,%d,%d,%d,%d\n", x, y, w, h, color);
}

static inline void drawRect(int x, int y, int w, int h, char color) {
    printf("R,%d,%d,%d,%d,%d\n", x, y, w, h, color);
}

static inline void fillCircle(int x, int y, int r, char color) {
    // Removed optimization to ensure erasing works for circles too
    printf("C,%d,%d,%d,%d\n", x, y, r, color);
}

static inline void drawCircle(int x, int y, int r, char color) {
    printf("C,%d,%d,%d,%d\n", x, y, r, color);
}

static inline void drawLine(int x1, int y1, int x2, int y2, char color) {
    printf("L,%d,%d,%d,%d,%d\n", x1, y1, x2, y2, color);
}

static inline void drawHLine(int x, int y, int w, char color) {
    printf("L,%d,%d,%d,%d,%d\n", x, y, x+w, y, color);
}

static inline void drawVLine(int x, int y, int h, char color) {
    printf("L,%d,%d,%d,%d,%d\n", x, y, x, y+h, color);
}

// FIX 2: Ensure background reading allows overwriting
static inline int readNeutronBackground(int x, int y) {
    return BLACK; 
}

// --- Text ---
static inline void setCursor(int x, int y) { cursor_x = x; cursor_y = y; }
static inline void setTextColor(char c) { text_color = c; }
static inline void setTextSize(int s) { }
static inline void setTextWrap(int w) { }
static inline void writeString(char* str) {
    printf("T,%d,%d,%d,%s\n", cursor_x, cursor_y, text_color, str);
    cursor_x += (8 * 5); 
}

#endif
