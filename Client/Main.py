import datetime
import os
import random
import socket
import sys

import pycountry
import pycountry_convert
import pygame.time

import MusicManager
import Recommendation
from button import *

pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_endevent(pygame.USEREVENT)

window_width, window_height = 1920, 1080

SCREEN = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Flag Quest")

BG_img = pygame.image.load("assets/Background.jpg")
BG = pygame.transform.scale(BG_img, (window_width, window_height))

# global sounds
CLICK_SOUND = pygame.mixer.Sound('assets/tones/click.mp3')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

target_fps = 120
clock = pygame.time.Clock()

server_ip = '172.27.32.1'

music_manager_obj = MusicManager.MusicManager()
next_song = music_manager_obj.get_next_song()
pygame.mixer.music.load(os.path.join('assets/music', next_song))
pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play()


# noinspection PyCompatibility
class Flag2Country:
    pos_count = 0
    correct_sound = pygame.mixer.Sound("assets/tones/correct.mp3")
    incorrect_sound = pygame.mixer.Sound("assets/tones/wrong.mp3")
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    start_time = None
    elapsed_time = 0

    def __init__(self, game_version=str(0.1), country_deck=None, streak=0,
                 filename=f"Gamesave_ID_1{formatted_datetime}.json", scroll_x=0, scroll_y=0, scroll_speed=10):
        self.state = "StartMenu"
        self.country_deck = country_deck
        self.country_name = ""
        self.countries = pycountry.countries
        self.list_of_countries = []
        self.list_of_chosen_countries = []
        self.pos_list = []
        self.picked_flag = ""
        self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 3.5, window_height / 3.5
        self.streak = streak
        self.card = None
        self.filename = filename
        self.game_version = game_version
        self.scroll_x = scroll_x
        self.scroll_y = scroll_y
        self.scroll_speed = scroll_speed

    @staticmethod
    def quit_game(client):
        client.send('Disconnect')
        pygame.quit()
        sys.exit()

    @staticmethod
    def detect_duplicates(my_list):
        duplicates = False
        for value in my_list:
            if my_list.count(value) > 1:
                duplicates = True
            else:
                pass
        return duplicates

    def increase_streak(self):
        self.streak = self.streak + 1
        return

    def reset_streak(self):
        self.streak = 0
        return

    def value_generator(self):
        self.pos_list = [(window_width / 2 - window_width / 2.125, window_height / 2),  # 1 oben links
                         (window_width / 2 + window_width / 15, window_height / 2),
                         (window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4),
                         (window_width / 2 + window_width / 15, window_height / 2 + window_height / 4)]
        detect_duplicate_list = []
        self.list_of_chosen_countries.clear()
        self.card = self.country_deck.get_next_value()
        self.picked_flag = self.card.value[1]
        self.country_name = self.card.value[0]

        for i in range(0, 3):
            cache = self.country_deck.get_random_card()
            self.list_of_chosen_countries.append(
                cache.value[0])  # Wählt 3 random Items aus dieser Liste aus und fügt sie einer anderen an
        duplicate = GAME_OBJEKT.detect_duplicates(detect_duplicate_list)

        if duplicate:
            return True

    def create_game_deck_generation(self):
        if self.country_deck is not None:
            return

        else:
            print("generated")
            items = os.listdir(
                r"flags")

            self.country_deck = Recommendation.FlashcardDeck()

            for i in items:
                flag_code = i
                flag_code_edited = i.replace(".png", "")
                flag_code_edited = flag_code_edited.upper()  # transforms the imagename to an alpha_2 code
                country_name = pycountry_convert.country_alpha2_to_country_name(
                    flag_code_edited)  # converts the alpha_2 code into the country name

                country = Recommendation.Flashcard([country_name, flag_code])
                self.country_deck.add_card(country)
            return

    def assign_pos(self):
        if not self.pos_list:
            self.pos_count = 0
            self.pos_list = [(window_width / 2 - window_width / 2.125, window_height / 2),  # 1 oben links
                             (window_width / 2 + window_width / 15, window_height / 2),
                             (window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4),
                             (window_width / 2 + window_width / 15, window_height / 2 + window_height / 4)]
            return

        pos_var_name = "pos_" + str(self.pos_count + 1)
        random_tuple = random.choice(self.pos_list)
        setattr(self, pos_var_name, random_tuple)
        self.pos_list.remove(random_tuple)
        self.pos_count += 1

        self.assign_pos()

    def wrong_answer(self):
        self.incorrect_sound.play()
        GAME_OBJEKT.reset_streak()
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = None
        self.country_deck.update_card(self.card, True, self.elapsed_time)

    def right_answer(self):
        self.correct_sound.play()
        GAME_OBJEKT.increase_streak()
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = None
        self.country_deck.update_card(self.card, False, self.elapsed_time)

    def save(self):
        CLICK_SOUND.play()
        self.country_deck.write_to_json(obj=self.country_deck, filename=self.filename)

    def flag2country_quiz(self):
        GAME_OBJEKT.create_game_deck_generation()
        if GAME_OBJEKT.value_generator():
            GAME_OBJEKT.value_generator()
        GAME_OBJEKT.assign_pos()
        self.elapsed_time = 0
        self.start_time = None
        self.start_time = pygame.time.get_ticks()
        while True:
            self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 3.5, window_height / 3.5
            DRAW_MOUSE_POS = pygame.mouse.get_pos()

            SCREEN.fill("#353a3c")

            answer_1 = Button_xy_cords(image=None, pos=GAME_OBJEKT.pos_1,
                                       text_input=self.list_of_chosen_countries[0],
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_2 = Button_xy_cords(image=None, pos=GAME_OBJEKT.pos_2,
                                       text_input=self.list_of_chosen_countries[1],
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_3 = Button_xy_cords(image=None, pos=GAME_OBJEKT.pos_3,
                                       text_input=self.list_of_chosen_countries[2],
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_4 = Button_xy_cords(image=None, pos=GAME_OBJEKT.pos_4,
                                       text_input=self.country_name,
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            flag_img = pygame.image.load(
                os.path.join('flags', self.picked_flag)
            )
            flag = pygame.transform.scale(flag_img, (self.FLAG_WIDTH, self.FLAG_HEIGHT))
            SCREEN.blit(flag, (window_width / 2 - self.FLAG_WIDTH / 2, window_height / 9))

            button_list = [answer_1, answer_2, answer_3, answer_4]

            for button in button_list:
                button.changeColor(DRAW_MOUSE_POS)
                button.update(SCREEN)

            if self.start_time is not None:
                elapsed_time_display = self.elapsed_time + (pygame.time.get_ticks() - self.start_time)
            else:
                elapsed_time_display = self.elapsed_time

            seconds = elapsed_time_display // 1000
            milliseconds = elapsed_time_display % 1000

            seconds_text = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.03)).render(
                f"Time: {seconds} seconds", True, WHITE)
            milliseconds_text = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.03)).render(
                f"and {milliseconds} ms", True, WHITE)
            SCREEN.blit(seconds_text, (window_width / 2 + self.FLAG_WIDTH - window_width / 10, window_height / 9))
            SCREEN.blit(milliseconds_text, (window_width / 2 + self.FLAG_WIDTH - window_width / 10, window_height / 6))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 - window_width / 2.125, window_height / 2):
                            CLICK_SOUND.play()  # Wenn Button 4 oben links (pos1(gedrückte taste)) ist dann -
                            GAME_OBJEKT.right_answer()
                            self.state = "Flag2CountryRightA"
                            return
                    if event.key == pygame.K_2:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 + window_width / 15, window_height / 2):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.right_answer()
                            self.state = "Flag2CountryRightA"
                            return
                    if event.key == pygame.K_3:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.right_answer()
                            self.state = "Flag2CountryRightA"
                            return
                    if event.key == pygame.K_4:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 + window_width / 15, window_height / 2 + window_height / 4):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.right_answer()
                            self.state = "Flag2CountryRightA"
                            return
                    if event.type != pygame.KEYDOWN or event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        CLICK_SOUND.play()
                        GAME_OBJEKT.wrong_answer()
                        self.state = "Flag2CountryWrongA"
                        return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if answer_1.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.wrong_answer()
                            self.state = "Flag2CountryWrongA"
                            return
                        if answer_2.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.wrong_answer()
                            self.state = "Flag2CountryWrongA"
                            return
                        if answer_3.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.wrong_answer()
                            self.state = "Flag2CountryWrongA"
                            return
                        if answer_4.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.right_answer()
                            self.state = "Flag2CountryRightA"
                            return

                elif event.type == pygame.USEREVENT:
                    pygame.mixer.music.load(os.path.join('assets/music', music_manager_obj.get_next_song()))
                    pygame.mixer.music.play()

            pygame.display.update()
            clock.tick(target_fps)

    def true_answer_screen(self):
        while True:
            TRUE_MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("#353a3c")

            heading_text = helper.get_font(
                helper.calculate_font_size(window_width, window_height, 0.09)).render("Richtige Antwort",
                                                                                      True, "Green")
            heading_rect = heading_text.get_rect(center=(window_width / 2, window_height / 9))
            SCREEN.blit(heading_text, heading_rect)

            streak_text = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.04)).render(
                f"Streak: {self.streak}", True, "White")
            streak_rect = streak_text.get_rect(center=(window_width / 2 - window_width / 3, window_height / 2))
            SCREEN.blit(streak_text, streak_rect)

            next_button = Button(image=None,
                                 pos=(window_width / 2 - window_width / 2.75, window_height / 2 + window_height / 2.75),
                                 text_input="Next",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            menu_button = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 2.75),
                                 text_input="Menu",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            save_button = Button(image=None,
                                 pos=(window_width / 2 + window_width / 2.5, window_height / 2 + window_height / 2.75),
                                 text_input="Save",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            for button in [next_button, menu_button, save_button]:
                button.changeColor(TRUE_MOUSE_POS)
                button.update(SCREEN)

            seconds = self.elapsed_time // 1000
            milliseconds = self.elapsed_time % 1000

            time_text = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.03)).render(
                f"Guessed right in:", True, WHITE)
            clock_text = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.03)).render(
                f"{seconds} seconds and {milliseconds} ms", True, WHITE)
            SCREEN.blit(time_text, (window_width / 2, window_height / 2 - window_height / 15))
            SCREEN.blit(clock_text, (window_width / 2, window_height / 2))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        CLICK_SOUND.play()
                        self.state = "PlayFlag2Country"
                        return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if next_button.checkForInput(TRUE_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "PlayFlag2Country"
                            return
                        if menu_button.checkForInput(TRUE_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "StartMenu"
                            return
                        if save_button.checkForInput(TRUE_MOUSE_POS):
                            GAME_OBJEKT.save()

            pygame.display.update()
            clock.tick(target_fps)

    def false_answer_screen(self):
        while True:
            FALSE_MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("#353a3c")
            heading_text = helper.get_font(
                helper.calculate_font_size(window_width, window_height, 0.09)).render("Falsche Antwort",
                                                                                      True, "Red")
            heading_rect = heading_text.get_rect(center=(window_width / 2, window_height / 9))
            SCREEN.blit(heading_text, heading_rect)

            correct_country_text = helper.get_font(
                helper.calculate_font_size(window_width, window_height, 0.04)).render(
                self.country_name, True, "Green")
            correct_country_rect = correct_country_text.get_rect(
                center=(window_width / 2 + window_width / 3, window_height / 2))
            SCREEN.blit(correct_country_text, correct_country_rect)

            streak_text = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.04)).render(
                f"Streak: {self.streak}", True, "White")
            streak_rect = streak_text.get_rect(center=(window_width / 2 - window_width / 3, window_height / 2))
            SCREEN.blit(streak_text, streak_rect)

            flag_img = pygame.image.load(
                os.path.join('flags', self.picked_flag)
            )
            flag = pygame.transform.scale(flag_img, (self.FLAG_WIDTH, self.FLAG_HEIGHT))
            SCREEN.blit(flag, (window_width / 2 - self.FLAG_WIDTH / 2, window_height / 2 - window_height / 6))

            next_button = Button(image=None,
                                 pos=(window_width / 2 - window_width / 2.75, window_height / 2 + window_height / 2.75),
                                 text_input="Next",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            menu_button = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 2.75),
                                 text_input="Menu",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            save_button = Button(image=None,
                                 pos=(window_width / 2 + window_width / 2.5, window_height / 2 + window_height / 2.75),
                                 text_input="Save",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            for button in [next_button, menu_button, save_button]:
                button.changeColor(FALSE_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        CLICK_SOUND.play()
                        self.state = "PlayFlag2Country"
                        return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if next_button.checkForInput(FALSE_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "PlayFlag2Country"
                            return
                        if menu_button.checkForInput(FALSE_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "StartMenu"
                            return
                        if save_button.checkForInput(FALSE_MOUSE_POS):
                            GAME_OBJEKT.save()

            pygame.display.update()
            clock.tick(target_fps)

    def start_menu(self):
        while True:
            SCREEN.blit(BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.12)).render(
                "MAIN MENU", True,
                "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            NEW_GAME_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                     text_input="New Game",
                                     font=helper.get_font(
                                         helper.calculate_font_size(window_width, window_height, 0.09)),
                                     base_color="White", hovering_color="#dadddd")
            RESUME_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                   text_input="Resume",
                                   font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.09)),
                                   base_color="White",
                                   hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3.25),
                                 text_input="QUIT",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.08)),
                                 base_color="White", hovering_color="#dadddd")
            SETTINGS_BUTTON = Button(image=None, pos=(
                window_width / 2 + window_width / 4, window_height / 2 + window_height / 3.25),
                                     text_input="SETTINGS",
                                     font=helper.get_font(
                                         helper.calculate_font_size(window_width, window_height, 0.08)),
                                     base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [NEW_GAME_BUTTON, RESUME_BUTTON, QUIT_BUTTON, SETTINGS_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if NEW_GAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "NewGameMenu"
                            return
                        if RESUME_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "ResumeGameMenu"
                            return
                        if SETTINGS_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "SettingsMenu"
                            return
                        if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            clock.tick(target_fps)

    def new_game_menu(self):

        while True:
            SCREEN.blit(BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = helper.get_font(
                helper.calculate_font_size(window_width, window_height, 0.08)).render("CREATE A NEW GAME",
                                                                                      True, "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            FLAG2COUNTRY_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                         text_input="Flag2Country",
                                         font=helper.get_font(
                                             helper.calculate_font_size(window_width, window_height, 0.07)),
                                         base_color="White",
                                         hovering_color="#dadddd")
            COUNTRY2FLAG_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                         text_input="Country2Flag",
                                         font=helper.get_font(
                                             helper.calculate_font_size(window_width, window_height, 0.07)),
                                         base_color="White",
                                         hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="QUIT",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")
            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="BACK",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [FLAG2COUNTRY_BUTTON, COUNTRY2FLAG_BUTTON, QUIT_BUTTON, BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if FLAG2COUNTRY_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "CreateGameMenu"
                            return
                        if COUNTRY2FLAG_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                        if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "StartMenu"
                            return
                        if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            clock.tick(target_fps)

    def create_game_name(self):
        input_rect = pygame.Rect(window_width / 2 - window_width / 2.25, window_height / 2, window_width / 1.125,
                                 helper.calculate_font_size(window_width, window_height, 0.07) * 1.2)
        input_text = ""
        input_color = GRAY
        active = False

        while True:
            SCREEN.blit(BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.09)).render(
                "Name the Game", True,
                "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            CONFIRM_BUTTON = Button(image=None,
                                    pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3),
                                    text_input="CONFIRM",
                                    font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                    base_color="White",
                                    hovering_color="#dadddd")
            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="BACK",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            event = pygame.event.get()
            for button in [CONFIRM_BUTTON, BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in event:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if CONFIRM_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            text_input = input_text
                            text_input = text_input + ".json"
                            self.filename = text_input
                            self.state = "PlayFlag2Country"
                            return
                        elif BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "NewGameMenu"
                            return
                        elif input_rect.collidepoint(event.pos):
                            active = not active
                        else:
                            active = False
                        input_color = WHITE if active else GRAY

                elif event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            CLICK_SOUND.play()
                            text_input = input_text
                            text_input = text_input + ".json"
                            self.filename = text_input
                            self.state = "PlayFlag2Country"
                            return
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            if len(input_text) < 15:
                                input_text += event.unicode
                            else:
                                pass

                pygame.draw.rect(SCREEN, input_color, input_rect, 0)
                pygame.draw.rect(SCREEN, BLACK, input_rect, 2)

                text_surface = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)).render(
                    input_text, True, BLACK)
                SCREEN.blit(text_surface, (input_rect.x + 10, input_rect.y + 10))

                pygame.display.update()
                clock.tick(target_fps)

    def resume_game_menu(self):
        while True:
            MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.blit(BG, (0, 0))

            MENU_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.09)).render(
                "RESUME A GAME",
                True, "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="QUIT",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="BACK",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SAVED_GAMES_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                        text_input="SAVED_GAMES_BUTTON",
                                        font=helper.get_font(
                                            helper.calculate_font_size(window_width, window_height, 0.07)),
                                        base_color="White",
                                        hovering_color="#dadddd")

            OPTIONS_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                    text_input="OPTIONS_BUTTON",
                                    font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                    base_color="White",
                                    hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [QUIT_BUTTON, BACK_BUTTON, SAVED_GAMES_BUTTON, OPTIONS_BUTTON]:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "StartMenu"
                            return
                        elif QUIT_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()
                        elif SAVED_GAMES_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "SavedGamesMenu"
                            return
                        elif OPTIONS_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()

            pygame.display.update()
            clock.tick(target_fps)

    def settings_menu(self):
        import client
        server_connection_state = False
        try:
            client_conn = client.ClientConnection(server_ip)
            server_connection_state = True
        except ConnectionRefusedError:
            print("Server refused the connection")
            server_connection_state = False
        global SCREEN, window_height, window_width, BG, target_fps
        Window_size_dropdown_state = False
        FPS_dropdown_state = False
        UPLOAD_IMG = pygame.image.load("assets/send_backup_icon.png")
        UPLOAD_TR = pygame.transform.scale(UPLOAD_IMG, (window_width / 8, window_height / 6))
        LOAD_IMG = pygame.image.load("assets/get_backup_icon.png")
        LOAD_TR = pygame.transform.scale(LOAD_IMG, (window_width / 8, window_height / 6))

        MUSIK_VOLUME_BAR = DraggableBar((window_width / 1.4, window_height / 2 + window_height / 8), (400, 30))

        start_time = pygame.time.get_ticks()

        while True:
            MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("#353a3c")

            MENU_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.09)).render(
                "SETTINGS",
                True, "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            WINDOW_SIZE_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.05)).render(
                "WINDOW SIZE:",
                True, "White")
            WINDOW_SIZE_RECT = WINDOW_SIZE_TEXT.get_rect(
                center=(window_width / 2 - window_width / 4, window_height / 2 - window_height / 4 - self.scroll_y))

            SEND_BACKUP_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.05)).render(
                "SAVE BACKUP:",
                True, "White")
            SEND_BACKUP_TEXT_RECT = SEND_BACKUP_TEXT.get_rect(
                center=(window_width / 2 - window_width / 4, window_height / 2 - window_height / 8 - self.scroll_y))

            LOAD_BACKUP_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.05)).render(
                "LOAD BACKUP:",
                True, "White")
            LOAD_BACKUP_TEXT_RECT = LOAD_BACKUP_TEXT.get_rect(
                center=(window_width / 2 - window_width / 4, window_height / 2 - self.scroll_y))

            MUSIC_VOLUME_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.05)).render(
                "MUSIC VOLUME:",
                True, "White")
            MUSIC_VOLUME_TEXT_RECT = MUSIC_VOLUME_TEXT.get_rect(
                center=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 8 - self.scroll_y))

            FPS_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.05)).render(
                "TARGET FPS:",
                True, "White")
            FPS_TEXT_RECT = FPS_TEXT.get_rect(
                center=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 4 - self.scroll_y))

            SAVE_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 2.75),
                                 text_input="SAVE",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 2.75),
                                 text_input="BACK",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            CHECK_FOR_UPDATE_BUTTON = Button(image=None,
                                             pos=(window_width / 2,
                                                  window_height / 2 + window_height / 2.75 - self.scroll_y),
                                             text_input="CHECK FOR UPDATE",
                                             font=helper.get_font(
                                                 helper.calculate_font_size(window_width, window_height, 0.05)),
                                             base_color="White", hovering_color="#dadddd")

            WINDOW_SIZE_DROPDOWN = DropDownMenu(image=None, pos=(
                window_width / 1.4, window_height / 2 - window_height / 4 - self.scroll_y), text_input="SIZES",
                                                dropdown_options=["FULL SCREEN", "1920 x 1080", "2560 x 1440",
                                                                   "4096 x 2304"],
                                                font=helper.get_font(
                                                    helper.calculate_font_size(window_width, window_height, 0.05)),
                                                base_color="White", hovering_color="#dadddd")
            FPS_DROPDOWN = DropDownMenu(image=None, pos=(
                window_width / 2 + window_width / 4, window_height / 2 + window_height / 4 - self.scroll_y),
                                        text_input="FPS",
                                        dropdown_options=["30", "60", "144"],
                                        font=helper.get_font(
                                            helper.calculate_font_size(window_width, window_height, 0.05)),
                                        base_color="White", hovering_color="#dadddd")

            SEND_BACKUP_BUTTON = ImageButton(UPLOAD_TR, (
                window_width / 1.4, window_height / 2 - window_height / 8 - self.scroll_y),
                                             UPLOAD_TR)
            LOAD_BACKUP_BUTTON = ImageButton(LOAD_TR, (window_width / 1.4, window_height / 2 - self.scroll_y),
                                             LOAD_TR)

            MUSIK_VOLUME_BAR.bar_y = window_height / 2 + window_height / 8 - self.scroll_y

            SCREEN.blit(WINDOW_SIZE_TEXT, WINDOW_SIZE_RECT)
            SCREEN.blit(SEND_BACKUP_TEXT, SEND_BACKUP_TEXT_RECT)
            SCREEN.blit(LOAD_BACKUP_TEXT, LOAD_BACKUP_TEXT_RECT)
            SCREEN.blit(MUSIC_VOLUME_TEXT, MUSIC_VOLUME_TEXT_RECT)
            SCREEN.blit(FPS_TEXT, FPS_TEXT_RECT)

            MUSIK_VOLUME_BAR.update(SCREEN, GRAY, GREEN)
            if pygame.mouse.get_pressed()[0]:
                if MUSIK_VOLUME_BAR.checkForInput(MOUSE_POS):
                    MUSIK_VOLUME_BAR.setbar(MOUSE_POS, window_width)
                    pygame.mixer.music.set_volume(MUSIK_VOLUME_BAR.get_volume())

            for button in [WINDOW_SIZE_DROPDOWN, FPS_DROPDOWN, CHECK_FOR_UPDATE_BUTTON]:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            if Window_size_dropdown_state:
                WINDOW_SIZE_DROPDOWN.draw_dropdown(SCREEN, 0.05, MOUSE_POS)

            if FPS_dropdown_state:
                FPS_DROPDOWN.draw_dropdown(SCREEN, 0.05, MOUSE_POS)

            for image_button in [SEND_BACKUP_BUTTON, LOAD_BACKUP_BUTTON]:
                image_button.update(SCREEN)

            pygame.draw.rect(SCREEN, (53, 58, 60), (0, 0, window_width, window_height / 5))
            pygame.draw.rect(SCREEN, (53, 58, 60), (0, window_height - window_height / 5,
                                                    window_width, window_height / 5))
            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [SAVE_BUTTON, BACK_BUTTON]:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            current_time = pygame.time.get_ticks()

            if current_time - start_time < 4500 and server_connection_state is False:
                WARNING_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.05)).render(
                    "SERVER REFUSED THE CONNECTION",
                    True, RED)
                WARNING_RECT = WARNING_TEXT.get_rect(center=(window_width / 2, window_height / 2))

                SCREEN.blit(WARNING_TEXT, WARNING_RECT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Mausrad nach oben
                        self.scroll_y -= self.scroll_speed * 2
                    elif event.button == 5:  # Mausrad nach unten
                        self.scroll_y += self.scroll_speed * 2
                    elif event.button == 1:
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "StartMenu"
                            client_conn.send("Disconnect")
                            return

                        elif SAVE_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                        try:
                            if SEND_BACKUP_BUTTON.checkForInput(MOUSE_POS):
                                if server_connection_state is not False:
                                    CLICK_SOUND.play()
                                    client_conn.send("BackupGames")
                                else:
                                    start_time = pygame.time.get_ticks()
                            elif LOAD_BACKUP_BUTTON.checkForInput(MOUSE_POS):
                                if server_connection_state is not False:
                                    CLICK_SOUND.play()
                                    client_conn.send("LoadBackup")
                                else:
                                    start_time = pygame.time.get_ticks()
                            elif CHECK_FOR_UPDATE_BUTTON.checkForInput(MOUSE_POS):
                                if server_connection_state is not False:
                                    CLICK_SOUND.play()
                                    version_up_to_date = client_conn.send('checkUpdate')
                                else:
                                    start_time = pygame.time.get_ticks()

                        except socket.error:
                            print("A Error with the network occurred")

                        if WINDOW_SIZE_DROPDOWN.checkForInput(MOUSE_POS):
                            if Window_size_dropdown_state:
                                Window_size_dropdown_state = False
                            else:
                                Window_size_dropdown_state = True
                        elif Window_size_dropdown_state:
                            selected_options = WINDOW_SIZE_DROPDOWN.check_dropdown(MOUSE_POS)
                            print(selected_options)
                            if selected_options:
                                if selected_options == "FULL SCREEN":
                                    SCREEN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
                                    BG = pygame.transform.scale(BG_img, (SCREEN.get_width(), SCREEN.get_height()))
                                    window_width, window_height = SCREEN.get_width(), SCREEN.get_height()
                                    CLICK_SOUND.play()
                                elif selected_options == "1920 x 1080":
                                    window_width, window_height = 1920, 1080
                                    BG = pygame.transform.scale(BG_img, (window_width, window_height))
                                    SCREEN = pygame.display.set_mode((window_width, window_height))
                                    CLICK_SOUND.play()
                                elif selected_options == "2560 x 1440":
                                    window_width, window_height = 2560, 1440
                                    BG = pygame.transform.scale(BG_img, (window_width, window_height))
                                    SCREEN = pygame.display.set_mode((window_width, window_height))
                                    CLICK_SOUND.play()
                                elif selected_options == "4096 x 2304":
                                    window_width, window_height = 4096, 2304
                                    BG = pygame.transform.scale(BG_img, (window_width, window_height))
                                    SCREEN = pygame.display.set_mode((window_width, window_height))
                                    CLICK_SOUND.play()

                        if FPS_DROPDOWN.checkForInput(MOUSE_POS):
                            if FPS_dropdown_state:
                                FPS_dropdown_state = False
                            else:
                                FPS_dropdown_state = True
                        elif FPS_dropdown_state:
                            selected_options = FPS_DROPDOWN.check_dropdown(MOUSE_POS)
                            if selected_options:
                                if selected_options == "30":
                                    CLICK_SOUND.play()
                                    target_fps = 30
                                elif selected_options == "´60":
                                    CLICK_SOUND.play()
                                    target_fps = 60
                                elif selected_options == "144":
                                    CLICK_SOUND.play()
                                    target_fps = 144

            pygame.display.update()
            clock.tick(target_fps)

    def saved_games_menu(self):
        BG_header_img = pygame.image.load("assets/Background-heading.jpg")
        BG_header = pygame.transform.scale(BG_header_img, (window_width, window_height / 4.431))

        scroll_window_width = window_width
        scroll_window_height = window_height * 10
        relativ_x = window_width / 2
        relativ_y = window_height / 2 - window_height / 6

        CARD_DECK_OBJEKT = Recommendation.FlashcardDeck()
        game_buttons = CARD_DECK_OBJEKT.get_json_names()

        button_obj_list = []
        button_pos = []

        for _ in game_buttons:
            button_pos.append((relativ_x, relativ_y))
            relativ_y += helper.calculate_font_size(window_width, window_height,
                                                    0.07) * 1.5  # Spacing zwischen den Zeilen

        while True:
            MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.blit(BG, (0, 0))

            button_obj_list.clear()
            for count, text in enumerate(game_buttons):
                x, y = button_pos[count]
                pos_var_name = "BUTTON" + str(count)  # game_buttons[count]
                setattr(self, pos_var_name, Button(image=None, pos=(relativ_x, y - self.scroll_y),
                                                   text_input=game_buttons[count],
                                                   font=helper.get_font(
                                                       helper.calculate_font_size(window_width, window_height,
                                                                                  0.07)),
                                                   base_color="White", hovering_color="#dadddd"))

                button_instance = getattr(self, pos_var_name)
                button_obj_list.append(button_instance)
                button_instance.changeColor(MOUSE_POS)
                button_instance.update(SCREEN)

            self.scroll_x = max(0, min(self.scroll_x, scroll_window_width - window_width))
            self.scroll_y = max(0, min(self.scroll_y, scroll_window_height - window_height))

            HEADING_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.12)).render(
                "SAVED GAMES", True,
                "#f1f25f")
            HEADING_RECT = HEADING_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 2.5, window_height / 2 + window_height / 8),
                                 text_input="BACK",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White",
                                 hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 2.5, window_height / 2 + window_height / 8),
                                 text_input="QUIT",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(BG_header, (0, 0))
            SCREEN.blit(HEADING_TEXT, HEADING_RECT)

            for button in [BACK_BUTTON, QUIT_BUTTON]:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Mausrad nach oben
                        self.scroll_y -= self.scroll_speed * 2
                    elif event.button == 5:  # Mausrad nach unten
                        self.scroll_y += self.scroll_speed * 2
                    if event.button == 1:
                        count = 0
                        for button in button_obj_list:
                            x, y = button_pos[count]
                            button.x_pos = x - self.scroll_x
                            button.y_pos = y - self.scroll_y
                            if button.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                filename = button.text_input + ".json"
                                loaded_deck_obj = Recommendation.FlashcardDeck()
                                loaded_deck = loaded_deck_obj.read_from_json(filename=filename)
                                self.filename = filename
                                self.country_deck = loaded_deck
                                self.state = "PlayFlag2Country"
                                return
                            count += 1
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            self.state = "ResumeGameMenu"
                            return
                        if QUIT_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            clock.tick(target_fps)


def mainloop():
    while GAME_OBJEKT.state != "Close":
        if GAME_OBJEKT.state == "StartMenu":
            GAME_OBJEKT.start_menu()
        elif GAME_OBJEKT.state == "NewGameMenu":
            GAME_OBJEKT.new_game_menu()
        elif GAME_OBJEKT.state == "CreateGameMenu":
            GAME_OBJEKT.create_game_name()
        elif GAME_OBJEKT.state == "ResumeGameMenu":
            GAME_OBJEKT.resume_game_menu()
        elif GAME_OBJEKT.state == "SavedGamesMenu":
            GAME_OBJEKT.saved_games_menu()
        elif GAME_OBJEKT.state == "SettingsMenu":
            GAME_OBJEKT.settings_menu()
        elif GAME_OBJEKT.state == "PlayFlag2Country":
            GAME_OBJEKT.flag2country_quiz()
        elif GAME_OBJEKT.state == "Flag2CountryWrongA":
            GAME_OBJEKT.false_answer_screen()
        elif GAME_OBJEKT.state == "Flag2CountryRightA":
            GAME_OBJEKT.true_answer_screen()


if __name__ == "__main__":
    GAME_OBJEKT = Flag2Country()
    mainloop()
