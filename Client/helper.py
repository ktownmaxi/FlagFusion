import pygame

def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


def calculate_font_size(window_width_, window_height_, font_size_factor):
    font_size = int(min(window_width_,
                        window_height_) * font_size_factor)  # font_size_factor = occupied screen area in dec. prozent
    return font_size
