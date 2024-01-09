import pygame

import helper


class Button:
    """
    A class which is a template for creating a button
    """
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        """
        Initializes hyperparameters to create a Button at xy cords
        :param image:
        :param pos: Position of the center of the Button should be in (x, y) format
        :param text_input: Text which should be displayed in the button
        :param font: font in which the text should be written
        :param base_color: base color of the text
        :param hovering_color: color of the text when the mouse cursor is hovering on top of the text
        """
        self.image = image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """
        Method which updates the appearance of the button on screen.
        :param screen: pygame screen.
        :return:
        """
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position: tuple) -> bool:
        """
        Method which checks if the button was clicked.
        :param position: Mouse position in (x, y) style.
        :return: True if the button was clicked.
        """
        if self.rect.collidepoint(position):
            return True
        return False

    def changeColor(self, position: tuple):
        """
        Method which checks if the button is hovered and changes color depending.
        :param position: Mouse position in (x, y) style.
        :return:
        """
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


class Button_xy_cords:
    """
    A Class which is basically a duplicate of Button(), but places the upper left corner to
    given coordinates and not the center
    """
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        """
        Initializes hyperparameters to create a Button at xy cords
        :param image:
        :param pos: Position of the top left of the Button at which the Button should be in (x, y) format
        :param text_input: Text which should be displayed in the button
        :param font: font in which the text should be written
        :param base_color: base color of the text
        :param hovering_color: color of the text when the mouse cursor is hovering on top of the text
        """
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(left=self.x_pos, top=self.y_pos)
        self.text_rect = self.text.get_rect(left=self.x_pos, top=self.y_pos)

    def update(self, screen):
        """
                Method which updates the appearance of the button on screen.
                :param screen: pygame screen.
                :return:
                """
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position: tuple) -> bool:
        """
        Method which checks if the button was clicked.
        :param position: Mouse position in (x, y) style.
        :return: True if the button was clicked.
        """
        if self.rect.collidepoint(position):
            return True
        return False

    def changeColor(self, position: tuple):
        """
                Method which checks if the button is hovered and changes color depending.
                :param position: Mouse position in (x, y) style.
                :return:
                """
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


class ImageButton:
    """
    Class which replaces the text of the button with an image
    """
    def __init__(self, image, pos):
        """
        Initializes hyperparameters to create an Image Button
        :param image: image path which should be displayed as the button
        :param pos: position of the image center in (x, y) format
        """
        self.image = image
        self.x_pos, self.y_pos = pos
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """
                        Method which updates the appearance of the button on screen.
                        :param screen: pygame screen.
                        :return:
                        """
        screen.blit(self.image, self.rect)

    def checkForInput(self, position: tuple):
        """
                Method which checks if the button was clicked.
                :param position: Mouse position in (x, y) style.
                :return: True if the button was clicked.
                """
        if self.rect.collidepoint(position):
            return True
        return False


class DropDownMenu:
    """
    Class which is a template for a dynamically create dropdown menu
    """
    option_buttons = []

    def __init__(self, image, pos, text_input, dropdown_options, font, base_color, hovering_color, state=False):
        """
        Initializes hyperparameters to create a DropDown menu
        :param image:
        :param pos: Position where the center of the dropdown menu should be in (x, y) format
        :param text_input: Text which should appear in the dropdown main box
        :param dropdown_options: list of strings which should appear sequentially in the boxes
        :param font: font which should be used
        :param base_color: base color of the text
        :param hovering_color: color when the mouse cursor is over the text hit-box
        :param state: bool if the dropdown menu should be closed or open at the start
        """
        self.image = image
        self.x_pos, self.y_pos = pos
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.dropdown_options = dropdown_options
        self.state = state
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        """
                        Method which updates the appearance of the button on screen.
                        :param screen: pygame screen.
                        :return:
                        """
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position: tuple) -> bool:
        """
        Method which checks if the button was clicked.
        :param position: Mouse position in (x, y) style.
        :return: True if the button was clicked.
        """
        if self.rect.collidepoint(position):
            if self.state:
                self.state = False
            else:
                self.state = True
            return self.state
        return False

    def changeColor(self, position: tuple):
        """
                Method which checks if the button is hovered and changes color depending.
                :param position: Mouse position in (x, y) style.
                :return:
                """
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

    def draw_dropdown(self, screen, font_factor: float, mouse_pos: tuple, window_hw: tuple):
        """
        Method which draws dynamically the dropdown menu.
        :param screen: Screen object on which to draw on top
        :param font_factor: Faktor in which the font should be drawn for example: 0.08.
        :param mouse_pos: Mouse position in (x, y) style
        :param window_hw: Height in width in (h, w) style
        :return:
        """
        for i, option in enumerate(self.dropdown_options):
            option_button = Button(image=None,
                                   pos=(self.x_pos,
                                        self.y_pos + window_hw[1] / 25 + (i + 1) * helper.calculate_font_size(
                                            window_hw[0], window_hw[1],
                                            font_factor)),
                                   text_input=option,
                                   font=helper.get_font(
                                       helper.calculate_font_size(window_hw[0], window_hw[1], font_factor)),
                                   base_color="White", hovering_color="#dadddd")
            self.option_buttons.append(option_button)
            option_button.changeColor(mouse_pos)
            option_button.update(screen)

    def check_dropdown(self, mouse_pos):
        """
        Method which checks the dropdown menu for input
        :param mouse_pos: Mouse position in (x, y) style
        :return: if clicked the text of the dropdown cell which was clicked on
        """
        for i, option in enumerate(self.option_buttons):
            if option.checkForInput(mouse_pos):
                return option.text_input
            else:
                continue


class DraggableBar:
    """
    Class which is a template for a draggable bar
    """
    def __init__(self, pos: tuple, bar_par: tuple, start_volume=0.7):
        """
        Initializes hyperparameters to create a DraggableBar
        :param pos: Position in (x, y) format where the left top of the Bar should be
        :param bar_par: Parameter in (w, h) format
        :param start_volume: Volume in decimal percentage of how much da bar should be filled at the start
        """
        self.volume = start_volume
        self.bar_x, self.bar_y = pos
        self.bar_width, self.bar_height = bar_par
        self.bar = pygame.Rect(self.bar_x, self.bar_y, self.bar_width * self.volume, self.bar_height)
        self.background = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)

    def update(self, window, inactive_color: tuple, active_color: tuple):
        """
        Method which updates the appearance of the bar on the screen
        :param window: Window object on which should be drawn on
        :param inactive_color: color for the inactive part of the bar
        :param active_color: color for the active part of the bar
        :return:
        """
        self.bar = pygame.Rect(self.bar_x, self.bar_y, self.bar_width * self.volume, self.bar_height)
        self.background = pygame.Rect(self.bar_x, self.bar_y, self.bar_width, self.bar_height)
        pygame.draw.rect(window, inactive_color, self.background)
        pygame.draw.rect(window, active_color, self.bar)

    def checkForInput(self, mouse: tuple) -> bool:
        """
        Method which checks for input on any part of the bar
        :param mouse: Mouse position in (x, y) style
        :return: If clicked returns true
        """
        if self.background.collidepoint(mouse):
            return True
        return False

    def set_bar(self, mouse: tuple, screen_width: int):
        """
        Method which sets the volume (how much is filled up) of the bar
        :param mouse: Mouse position in (x, y) style
        :param screen_width: Width of the screen
        :return:
        """
        self.volume = min((mouse[0] - self.bar_x), screen_width) / self.bar_width

    def get_volume(self) -> float:
        """
        Getter for the volume (percentage of how much is filled up)
        :return: the volume in decimal percentage
        """
        return self.volume
