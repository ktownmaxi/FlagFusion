import pygame
import helper


class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
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
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if self.rect.collidepoint(position):
            return True
        return False

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


class Button_xy_cords():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
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
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if self.rect.collidepoint(position):
            return True
        return False

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)


class ImageButton():
    def __init__(self, image, pos, base_image):
        self.image = image
        self.x_pos, self.y_pos = pos
        self.base_image = base_image
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))

    def update(self, screen):
        screen.blit(self.image, self.rect)

    def checkForInput(self, position):
        if self.rect.collidepoint(position):
            return True
        return False


class DropDownMenu():
    option_buttons = []

    def __init__(self, image, pos, text_input, dropdown_options, font, base_color, hovering_color, state=False):
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
        if self.image is not None:
            screen.blit(self.image, self.rect)
        screen.blit(self.text, self.text_rect)

    def checkForInput(self, position):
        if self.rect.collidepoint(position):
            if self.state:
                self.state = False
            else:
                self.state = True
            return self.state
        return False

    def changeColor(self, position):
        if self.rect.collidepoint(position):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)

    def draw_dropdown(self, screen, window_width, window_height, font_factor, mouse_pos):

        for i, option in enumerate(self.dropdown_options):
            option_button = Button(image=None,
                                   pos=(self.x_pos,
                                        self.y_pos + window_height / 25 + (i + 1) * helper.calculate_font_size(
                                            window_width, window_height,
                                            font_factor)),
                                   text_input=option,
                                   font=helper.get_font(
                                       helper.calculate_font_size(window_width, window_height, font_factor)),
                                   base_color="White", hovering_color="#dadddd")
            self.option_buttons.append(option_button)
            option_button.changeColor(mouse_pos)
            option_button.update(screen)

    def check_dropdown(self, mouse_pos):
        for i, option in enumerate(self.option_buttons):
            if option.checkForInput(mouse_pos):
                return option.text_input
            else:
                continue
