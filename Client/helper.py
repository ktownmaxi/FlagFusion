import pygame


def get_font(size: int, font_location: str = "assets/font.ttf") -> pygame.font.Font:
    """
    Returns a font in the desired size
    :param font_location: location where the ttf file is stored
    :param size: integer which describes the font size
    :return: Returns a font in the desired size
    """
    return pygame.font.Font(font_location, size)


def calculate_font_size(window_width_: int, window_height_: int, font_size_factor: float) -> int:
    """
    Method to calculate the desired font size by taking in account the window area
    :param window_width_: window width as an integer
    :param window_height_: window height as an integer
    :param font_size_factor: float which describes the occupied area of the screen
    :return: Returns an integer which can be put in the get_font_method
    """
    font_size = int(min(window_width_,
                        window_height_) * font_size_factor)
    return font_size
