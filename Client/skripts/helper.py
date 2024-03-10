from socket import socket
import functools
import pygame
import time


def get_font(size: int, font_location: str = "../assets/font.ttf") -> pygame.font.Font:
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


def recv_data(conn: socket, msg_length: int) -> str:
    """
            Method to make receiving data more stable.
            :param conn: connection from which we want to receive.
            :param int msg_length: length of the msg in bytes.
            :returns: the not decoded msg in binary.
            :rtype: str.
            """

    msg = b""
    while len(msg) < msg_length:
        chunk = conn.recv(msg_length - len(msg))
        if not chunk:
            # Connection closed or data lost
            break
        msg += chunk
    return msg


def run_once(func):
    """
    Decorator to only run a function once
    :param func: function which should be run once
    :return: returns the wrapper
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if not wrapper.has_run:
            wrapper.has_run = True
            return func(*args, **kwargs)

    wrapper.has_run = False
    return wrapper


def run_once_a_second(func):
    """
    Decorator for only run a function once a second
    :param func: function which should be run at max once a second
    :return: returns the wrapper
    """
    last_execution_time = 0

    def wrapper(*args, **kwargs):
        nonlocal last_execution_time

        current_time = time.time()
        time_since_last_execution = current_time - last_execution_time

        if time_since_last_execution >= 1:
            result = func(*args, **kwargs)
            last_execution_time = time.time()
            return result

    return wrapper
