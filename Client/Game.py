import datetime
import json
import os
import queue
import random
import socket
import sys
import threading

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

CLICK_SOUND = pygame.mixer.Sound('assets/tones/click.mp3')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

target_fps = 30
clock = pygame.time.Clock()

server_ip = '192.168.178.86'

music_manager_obj = MusicManager.MusicManager()
next_song = music_manager_obj.get_next_song()
pygame.mixer.music.load(os.path.join('assets/music', next_song))
pygame.mixer.music.set_volume(0.0)
pygame.mixer.music.play()


class Flag2CountryMixin:
    """
    Class to share functions and variables between classes.
    """

    def __init__(self, game_version):
        self.country_deck = None
        self.country_name = None
        self.card = None
        self.picked_flag = None
        self.game_version = game_version
        self.random_countries = []

    @staticmethod
    def quit_game(client_conn=None, client_bol: bool = None):
        """
        Method to safely quit the game
        :param client_conn: Client class to disconnect from the server.
        :param client_bol: boolean to check if the client is connected to the server.
        :return:
        """
        if client_bol:
            try:
                client_conn.sendDisconnect()
            except socket.error:
                pass
        pygame.quit()
        sys.exit()

    @staticmethod
    def detect_duplicates(my_list: list) -> bool:
        """
        Method to detect duplicates in a list.
        :param my_list: list which should be checked for duplicates.
        :return: Boolean if duplicate was detected
        """
        duplicates = False
        for value in my_list:
            if my_list.count(value) > 1:
                duplicates = True
            else:
                pass
        return duplicates

    @staticmethod
    def assign_pos(obj, pos_list, pos_count=0):
        """
        Method to assign random positions to a pos_ variable
        :param obj: class instance on which the pos_ variable should be written
        :param pos_list: list with possible positions to which can be assigned to pos_
        :param pos_count: ---
        :return:
        """
        if not pos_list:
            return

        pos_var_name = "pos_" + str(pos_count + 1)
        random_tuple = random.choice(pos_list)
        setattr(obj, pos_var_name, random_tuple)
        pos_list.remove(random_tuple)
        pos_count += 1

        Flag2CountryMixin.assign_pos(obj, pos_list, pos_count)

    @staticmethod
    def find_country_from_pic_name(file_name: str, data_path: str) -> str:
        """
        Method to find a country from its picture name in a json file
        :param file_name: name of the file which name should be searched
        :param data_path: path of the json file
        :return: returns the country name
        """
        with open(data_path, 'r') as file:
            data = json.load(file)

        for card in data["cards"]:
            if file_name in card["value"]:
                return card["value"][0]

    def value_generator(self):
        """
        Method to generate the values for playing the flag guessing game
        :return:
        """
        detect_duplicate_list = []
        list_of_chosen_countries = []
        self.card = self.country_deck.get_next_value()
        self.picked_flag = self.card.value[1]
        self.country_name = self.card.value[0]
        detect_duplicate_list.append(self.country_name)

        for i in range(0, 3):
            cache = self.country_deck.get_random_card()
            list_of_chosen_countries.append(
                cache.value[0])  # 3 random items and adds them to the final countries list
            detect_duplicate_list.append(
                cache.value[0]
            )
        duplicate = Flag2CountryMixin.detect_duplicates(detect_duplicate_list)

        if duplicate:
            self.value_generator()
        else:
            return list_of_chosen_countries

    def create_game_deck_generation(self):
        """
        Method to create a game deck to save scores
        :return:
        """
        if self.country_deck is not None:
            return

        else:
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

    def try_connect_to_server(self) -> tuple:
        """
        Method to try connection to the server.
        :return: returns an instance of Client Connection or non, and a bool which describes if the process was a success.
        """
        import client
        try:
            client_conn = client.ClientConnection(server_ip, self.game_version)
            server_connection_state = True
            return client_conn, server_connection_state
        except ConnectionRefusedError:
            print("Server refused the connection")
            server_connection_state = False
            return None, server_connection_state


class Flag2Country(Flag2CountryMixin):
    correct_sound = pygame.mixer.Sound("assets/tones/correct.mp3")
    incorrect_sound = pygame.mixer.Sound("assets/tones/wrong.mp3")
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    start_time = None
    elapsed_time = 0

    def __init__(self, country_deck=None, streak=0, filename=f"Game_save_ID_1{formatted_datetime}.json",
                 scroll_speed=10):
        super().__init__(0.1)
        self.country_deck = country_deck
        self.countries = pycountry.countries
        self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 3.5, window_height / 3.5
        self.streak = streak
        self.filename = filename
        self.scroll_speed = scroll_speed

    def increase_streak(self):
        self.streak = self.streak + 1
        return

    def reset_streak(self):
        self.streak = 0
        return

    def wrong_answer(self):
        self.incorrect_sound.play()
        self.reset_streak()
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = None
        self.country_deck.update_card(self.card, True, self.elapsed_time)

    def right_answer(self):
        self.correct_sound.play()
        self.increase_streak()
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = None
        self.country_deck.update_card(self.card, False, self.elapsed_time)

    def save(self):
        CLICK_SOUND.play()
        self.country_deck.write_to_json(obj=self.country_deck, filename=self.filename)

    def flag2country_quiz(self):
        answer_pos_list = [(window_width / 2 - window_width / 2.125, window_height / 2),  # 1 top left
                           (window_width / 2 + window_width / 15, window_height / 2),
                           (window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4),
                           (window_width / 2 + window_width / 15, window_height / 2 + window_height / 4)]

        self.create_game_deck_generation()
        self.random_countries = self.value_generator()
        self.assign_pos(obj=self, pos_list=answer_pos_list)
        self.elapsed_time = 0
        self.start_time = None
        self.start_time = pygame.time.get_ticks()
        while True:
            self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 3.5, window_height / 3.5
            DRAW_MOUSE_POS = pygame.mouse.get_pos()

            SCREEN.fill("#353a3c")

            answer_1 = Button_xy_cords(image=None, pos=self.pos_1,
                                       text_input=self.random_countries[0],
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_2 = Button_xy_cords(image=None, pos=self.pos_2,
                                       text_input=self.random_countries[1],
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_3 = Button_xy_cords(image=None, pos=self.pos_3,
                                       text_input=self.random_countries[2],
                                       font=helper.get_font(
                                           helper.calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_4 = Button_xy_cords(image=None, pos=self.pos_4,
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
                    Flag2CountryMixin.quit_game(None, None)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 - window_width / 2.125, window_height / 2):
                            CLICK_SOUND.play()  # Wenn Button 4 oben links (pos1(gedrückte taste)) ist dann -
                            self.right_answer()
                            menu_obj.state = "Flag2CountryRightA"
                            return
                    if event.key == pygame.K_2:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 + window_width / 15, window_height / 2):
                            CLICK_SOUND.play()
                            self.right_answer()
                            menu_obj.state = "Flag2CountryRightA"
                            return
                    if event.key == pygame.K_3:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4):
                            CLICK_SOUND.play()
                            self.right_answer()
                            menu_obj.state = "Flag2CountryRightA"
                            return
                    if event.key == pygame.K_4:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 + window_width / 15, window_height / 2 + window_height / 4):
                            CLICK_SOUND.play()
                            self.right_answer()
                            menu_obj.state = "Flag2CountryRightA"
                            return
                    if event.type != pygame.KEYDOWN or event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        CLICK_SOUND.play()
                        self.wrong_answer()
                        menu_obj.state = "Flag2CountryWrongA"
                        return

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if answer_1.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.wrong_answer()
                            menu_obj.state = "Flag2CountryWrongA"
                            return
                        if answer_2.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.wrong_answer()
                            menu_obj.state = "Flag2CountryWrongA"
                            return
                        if answer_3.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.wrong_answer()
                            menu_obj.state = "Flag2CountryWrongA"
                            return
                        if answer_4.checkForInput(DRAW_MOUSE_POS):
                            CLICK_SOUND.play()
                            self.right_answer()
                            menu_obj.state = "Flag2CountryRightA"
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
                    Flag2CountryMixin.quit_game(None, None)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        CLICK_SOUND.play()
                        menu_obj.state = "PlayFlag2Country"
                        return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if next_button.checkForInput(TRUE_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "PlayFlag2Country"
                            return
                        if menu_button.checkForInput(TRUE_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "StartMenu"
                            return
                        if save_button.checkForInput(TRUE_MOUSE_POS):
                            self.save()

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
                    Flag2CountryMixin.quit_game(None, None)

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        CLICK_SOUND.play()
                        menu_obj.state = "PlayFlag2Country"
                        return

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if next_button.checkForInput(FALSE_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "PlayFlag2Country"
                            return
                        if menu_button.checkForInput(FALSE_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "StartMenu"
                            return
                        if save_button.checkForInput(FALSE_MOUSE_POS):
                            self.save()

            pygame.display.update()
            clock.tick(target_fps)


class PvP_Flag2country(Flag2CountryMixin):
    def __init__(self):
        super().__init__(0.1)
        self.set_time = 100
        self.player_list = []
        self.list_of_chosen_countries = []
        self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 3.5, window_height / 3.5
        self.flag_list = []
        self.question_counter = 0
        self.old_question_counter_value = self.question_counter
        self.score, self.score_other_player = 0, 0
        self.right_question_counter, self.other_player_right_question_counter = 0, 0
        self.won = None

    def increase_score_and_question_counter(self, increase_value=1):
        self.score += increase_value
        self.right_question_counter += 1

    def decrease_score(self, decrease_value=1):
        self.score -= decrease_value

    def increase_question_counter(self):
        self.question_counter += 1

    def check_if_question_counter_increased(self):
        if self.question_counter == 0:
            self.question_counter += 1
            self.old_question_counter_value = self.question_counter
            return True

        elif self.question_counter == self.old_question_counter_value + 1:
            self.old_question_counter_value = self.question_counter
            return True
        else:
            self.old_question_counter_value = self.question_counter
            return False

    def create_questions(self, current_question_count):

        detect_duplicate_list = []
        file_path = os.path.join("assets", "sample_deck.json")
        self.country_deck = Recommendation.FlashcardDeck.read_from_json(file_path)

        self.picked_flag = self.flag_list[current_question_count]
        self.country_name = self.find_country_from_pic_name(file_name=self.picked_flag, data_path=file_path)
        detect_duplicate_list.append(self.country_name)

        self.random_countries.clear()
        for i in range(0, 3):
            cache = self.country_deck.get_random_card()
            self.random_countries.append(
                cache.value[0])
            detect_duplicate_list.append(
                cache.value[0]
            )
        duplicate = Flag2CountryMixin.detect_duplicates(detect_duplicate_list)

        if duplicate:
            self.create_questions(current_question_count)
        else:
            return self.random_countries

    def calculate_right_percentage(self, right_answer_count):
        return int(right_answer_count / max(1, self.question_counter - 1) * 100)

    def draw_screen(self):
        search_for_player = True
        run_once_bool = True
        client_conn, server_connection_state = self.try_connect_to_server()
        if server_connection_state:
            to_server_comm_obj = client_conn.pvpMode(client_conn.client)
            check_player_thread = threading.Thread(target=to_server_comm_obj.recv_player_ready)
            check_player_thread.start()

        start_ticks = pygame.time.get_ticks()

        while True:
            if server_connection_state:
                if not check_player_thread.is_alive():
                    search_for_player = False
                    if run_once_bool:
                        self.flag_list = to_server_comm_obj.recv_flag_list()
                        run_once_bool = False
                    if self.check_if_question_counter_increased():
                        answer_pos_list = [(window_width / 2 - window_width / 2.125, window_height / 2),
                                           (window_width / 2, window_height / 2),
                                           (window_width / 2 - window_width / 2.125,
                                            window_height / 2 + window_height / 4),
                                           (window_width / 2, window_height / 2 + window_height / 4)]

                        self.create_questions(self.question_counter)
                        self.assign_pos(obj=self, pos_list=answer_pos_list)

                        RIGHT_ANSWER_P = helper.get_font(
                            helper.calculate_font_size(window_width, window_height, 0.03)).render(
                            f"{self.calculate_right_percentage(max(0, self.right_question_counter))} % | {self.calculate_right_percentage(
                                max(0, self.other_player_right_question_counter))} %",
                            True, WHITE)
                        RIGHT_ANSWER_P_RECT = RIGHT_ANSWER_P.get_rect(
                            center=(window_width / 2 + window_width / 3,
                                    window_height / 2 - window_height / 4))

                    if "send_and_recv_score" in locals() and send_and_recv_score.is_alive():
                        pass
                    if "send_and_recv_score" in locals() and not send_and_recv_score.is_alive():
                        try:
                            self.score_other_player = int(q.get(timeout=0))
                        except queue.Empty:
                            pass
                        finally:
                            q = queue.Queue()
                            send_and_recv_score = threading.Thread(
                                target=to_server_comm_obj.send_score_to_server,
                                args=(self.score, q))
                            send_and_recv_score.start()
                    else:
                        q = queue.Queue()
                        send_and_recv_score = threading.Thread(target=to_server_comm_obj.send_score_to_server,
                                                               args=(self.score, q))
                        send_and_recv_score.start()
                        try:
                            self.score_other_player = int(q.get(timeout=0))
                        except queue.Empty:
                            pass

            self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 4, window_height / 4
            MOUSE_POS = pygame.mouse.get_pos()

            if server_connection_state is True and search_for_player is False:
                SCREEN.fill("#353a3c")

                answer_1 = Button_xy_cords(image=None, pos=self.pos_1,
                                           text_input=self.random_countries[0],
                                           font=helper.get_font(
                                               helper.calculate_font_size(window_width, window_height, 0.025)),
                                           base_color="White",
                                           hovering_color="Light Blue")

                answer_2 = Button_xy_cords(image=None, pos=self.pos_2,
                                           text_input=self.random_countries[1],
                                           font=helper.get_font(
                                               helper.calculate_font_size(window_width, window_height, 0.025)),
                                           base_color="White",
                                           hovering_color="Light Blue")

                answer_3 = Button_xy_cords(image=None, pos=self.pos_3,
                                           text_input=self.random_countries[2],
                                           font=helper.get_font(
                                               helper.calculate_font_size(window_width, window_height, 0.025)),
                                           base_color="White",
                                           hovering_color="Light Blue")

                answer_4 = Button_xy_cords(image=None, pos=self.pos_4,
                                           text_input=self.country_name,
                                           font=helper.get_font(
                                               helper.calculate_font_size(window_width, window_height, 0.025)),
                                           base_color="White",
                                           hovering_color="Light Blue")

                PLAYERS_SCORE = helper.get_font(
                    helper.calculate_font_size(window_width, window_height, 0.03)).render(
                    f"{self.score} | {self.score_other_player}",
                    True, WHITE)
                PLAYERS_SCORE_RECT = PLAYERS_SCORE.get_rect(center=(window_width / 2 + window_width / 3,
                                                                    window_height / 2))

                flag_img = pygame.image.load(
                    os.path.join('flags', self.picked_flag)
                )
                flag = pygame.transform.scale(flag_img, (self.FLAG_WIDTH, self.FLAG_HEIGHT))
                SCREEN.blit(flag, (window_width / 2 - self.FLAG_WIDTH / 2 - window_width / 10, window_height / 9))

                elapsed_time = (pygame.time.get_ticks() - start_ticks) // 1000

                if elapsed_time <= self.set_time:
                    time_display = self.set_time - elapsed_time
                else:
                    time_display = 0

                TIMER_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.03)).render(
                    f"Time: {time_display} sec",
                    True, WHITE)
                TIMER_RECT = TIMER_TEXT.get_rect(center=(window_width / 2 + window_width / 3,
                                                         window_height / 2 + window_height / 4))

                if time_display == 0:
                    if self.score > self.score_other_player:
                        self.won = True
                        client_conn.sendDisconnect()
                        menu_obj.state = "EndScreen"
                        return
                    else:
                        self.won = False
                        client_conn.sendDisconnect()
                        menu_obj.state = "EndScreen"
                        return

                SCREEN.blit(TIMER_TEXT, TIMER_RECT)
                SCREEN.blit(PLAYERS_SCORE, PLAYERS_SCORE_RECT)
                if "RIGHT_ANSWER_P" in locals():
                    SCREEN.blit(RIGHT_ANSWER_P, RIGHT_ANSWER_P_RECT)

                SURRENDER_BUTTON = Button(image=None,
                                          pos=(
                                              window_width / 2 + window_width / 3,
                                              window_height / 2 + window_height / 2.75),
                                          text_input="SURRENDER",
                                          font=helper.get_font(
                                              helper.calculate_font_size(window_width, window_height, 0.03)),
                                          base_color="White", hovering_color="#dadddd")

                button_list = [answer_1, answer_2, answer_3, answer_4, SURRENDER_BUTTON]

                for button in button_list:
                    button.changeColor(MOUSE_POS)
                    button.update(SCREEN)

            elif server_connection_state is True and search_for_player is True:
                SCREEN.fill("#353a3c")

                INFORMATION_TEXT = helper.get_font(
                    helper.calculate_font_size(window_width, window_height, 0.06)).render(
                    "WAITING FOR OTHER PLAYERS",
                    True, RED)
                INFORMATION_RECT = INFORMATION_TEXT.get_rect(center=(window_width / 2, window_height / 2))

                SCREEN.blit(INFORMATION_TEXT, INFORMATION_RECT)

                LEAVE_QUEUE_BUTTON = Button(image=None,
                                            pos=(
                                                window_width / 2,
                                                window_height / 2 + window_height / 3.5),
                                            text_input="LEAVE QUEUE",
                                            font=helper.get_font(
                                                helper.calculate_font_size(window_width, window_height, 0.05)),
                                            base_color="White", hovering_color="#dadddd")

                for button in [LEAVE_QUEUE_BUTTON]:
                    button.changeColor(MOUSE_POS)
                    button.update(SCREEN)

            else:
                SCREEN.fill("#353a3c")

                WARNING_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.06)).render(
                    "SERVER REFUSED THE CONNECTION",
                    True, RED)
                WARNING_RECT = WARNING_TEXT.get_rect(center=(window_width / 2, window_height / 2))

                SCREEN.blit(WARNING_TEXT, WARNING_RECT)

                BACK_BUTTON = Button(image=None,
                                     pos=(
                                         window_width / 2,
                                         window_height / 2 + window_height / 3.5),
                                     text_input="BACK TO START",
                                     font=helper.get_font(
                                         helper.calculate_font_size(window_width, window_height, 0.05)),
                                     base_color="White", hovering_color="#dadddd")

                for button in [BACK_BUTTON]:
                    button.changeColor(MOUSE_POS)
                    button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Flag2CountryMixin.quit_game(client_conn, True)

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 - window_width / 2.125, window_height / 2):
                            CLICK_SOUND.play()
                            self.increase_score_and_question_counter()
                            self.increase_question_counter()
                    if event.key == pygame.K_2:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 + window_width / 15, window_height / 2):
                            CLICK_SOUND.play()
                            self.increase_score_and_question_counter()
                            self.increase_question_counter()
                    if event.key == pygame.K_3:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4):
                            CLICK_SOUND.play()
                            self.increase_score_and_question_counter()
                            self.increase_question_counter()
                    if event.key == pygame.K_4:
                        if (button_list[3].x_pos, button_list[3].y_pos) == (
                                window_width / 2 + window_width / 15, window_height / 2 + window_height / 4):
                            CLICK_SOUND.play()
                            self.increase_score_and_question_counter()
                            self.increase_question_counter()
                    if event.type != pygame.KEYDOWN or event.key in [pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4]:
                        CLICK_SOUND.play()
                        self.decrease_score()
                        self.increase_question_counter()

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if server_connection_state is True and search_for_player is False:
                            if SURRENDER_BUTTON.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                menu_obj.state = "StartMenu"
                                if server_connection_state:
                                    client_conn.sendDisconnect()
                                return

                            if answer_1.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                self.decrease_score()
                                self.increase_question_counter()
                            if answer_2.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                self.decrease_score()
                                self.increase_question_counter()
                            if answer_3.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                self.decrease_score()
                                self.increase_question_counter()
                            if answer_4.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                self.increase_score_and_question_counter()
                                self.increase_question_counter()

                        if server_connection_state is True and search_for_player is True:
                            if LEAVE_QUEUE_BUTTON.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                menu_obj.state = "CompetitiveModeMenu"
                                if server_connection_state:
                                    client_conn.sendDisconnect()
                                    return
                        if server_connection_state is False:
                            if BACK_BUTTON.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                menu_obj.state = "StartMenu"
                                return
                if event.type == pygame.USEREVENT:
                    pygame.mixer.music.load(os.path.join('assets/music', music_manager_obj.get_next_song()))
                    pygame.mixer.music.play()

            pygame.display.update()
            clock.tick(target_fps)

    def end_screen(self):

        while True:
            MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.blit(BG, (0, 0))

            if self.won:
                TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.12)).render(
                    "YOU WON",
                    True, "#f1f25f")
                MENU_RECT = TEXT.get_rect(center=(window_width / 2, window_height / 3))

            else:
                TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.12)).render(
                    "YOU LOST",
                    True, "#f1f25f")
                MENU_RECT = TEXT.get_rect(center=(window_width / 2, window_height / 3))

            RETURN_BUTTON = Button(image=None,
                                   pos=(window_width / 2, window_height / 2 + window_height / 3),
                                   text_input="RETURN TO MENU",
                                   font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.08)),
                                   base_color="White", hovering_color="#dadddd")

            SCREEN.blit(TEXT, MENU_RECT)

            for button in [RETURN_BUTTON]:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Flag2CountryMixin.quit_game(None, None)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if RETURN_BUTTON.checkForInput(MOUSE_POS):
                            menu_obj.state = "StartMenu"
                            return

            pygame.display.update()
            clock.tick(target_fps)

    class Player:
        def __init__(self, current_score=0):
            self.current_score = current_score
            self.profile_picture = "____"
            self.player_name = "testname"

        def increase_score(self, increase_value):
            self.current_score += increase_value


class Menu(Flag2CountryMixin):
    def __init__(self, game_version, scroll_speed=10):
        super().__init__(game_version)
        self.state = "StartMenu"
        self.scroll_speed = scroll_speed
        self.scroll_y = 0
        self.game_version = game_version

    def start_menu(self):
        while True:
            SCREEN.blit(BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.12)).render(
                "START MENU", True,
                "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            TRAINING_BUTTON = Button(image=None, pos=(window_width / 2 - window_width / 4, window_height / 2.5),
                                     text_input="New Game",
                                     font=helper.get_font(
                                         helper.calculate_font_size(window_width, window_height, 0.07)),
                                     base_color="White", hovering_color="#dadddd")
            COMPETITIVE_MODE_BUTTON = Button(image=None, pos=(window_width / 2 + window_width / 4, window_height / 2.5),
                                             text_input="1v1 Modes",
                                             font=helper.get_font(
                                                 helper.calculate_font_size(window_width, window_height, 0.07)),
                                             base_color="White", hovering_color="#dadddd")
            RESUME_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                   text_input="Resume a Game",
                                   font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
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

            for button in [TRAINING_BUTTON, RESUME_BUTTON, QUIT_BUTTON, SETTINGS_BUTTON, COMPETITIVE_MODE_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Flag2CountryMixin.quit_game(None, None)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if TRAINING_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "NewGameMenu"
                            return
                        if RESUME_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "ResumeGameMenu"
                            return
                        if COMPETITIVE_MODE_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "CompetitiveModeMenu"
                            return
                        if SETTINGS_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "SettingsMenu"
                            return
                        if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            Flag2CountryMixin.quit_game(None, None)

            pygame.display.update()
            clock.tick(target_fps)

    def competitive_mode_menu(self):
        while True:
            SCREEN.blit(BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = helper.get_font(helper.calculate_font_size(window_width, window_height, 0.09)).render(
                "COMPETITIVE MENU", True,
                "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            PVAI_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                 text_input="Player vs. AI",
                                 font=helper.get_font(
                                     helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")
            PVP_MODE_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2),
                                     text_input="PVP (1v1)",
                                     font=helper.get_font(
                                         helper.calculate_font_size(window_width, window_height, 0.07)),
                                     base_color="White", hovering_color="#dadddd")
            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3.25),
                                 text_input="BACK",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White",
                                 hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3.25),
                                 text_input="QUIT",
                                 font=helper.get_font(helper.calculate_font_size(window_width, window_height, 0.08)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [PVAI_BUTTON, BACK_BUTTON, QUIT_BUTTON, PVP_MODE_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    Flag2CountryMixin.quit_game(None, None)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if PVAI_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                        elif BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "StartMenu"
                            return
                        elif PVP_MODE_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            temp_game_obj = PvP_Flag2country()
                            menu_obj.state = "PVP"
                            return temp_game_obj
                        elif QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            Flag2CountryMixin.quit_game(None, None)

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
                    Flag2CountryMixin.quit_game(None, None)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if FLAG2COUNTRY_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "CreateGameMenu"
                            return
                        if COUNTRY2FLAG_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                        if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "StartMenu"
                            return
                        if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            Flag2CountryMixin.quit_game(None, None)

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
                    Flag2CountryMixin.quit_game(None, None)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if CONFIRM_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            text_input = input_text
                            text_input = text_input + ".json"
                            fresh_game_obj = Flag2Country(filename=text_input)
                            menu_obj.state = "PlayFlag2Country"
                            return fresh_game_obj
                        elif BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "NewGameMenu"
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
                            fresh_game_obj = Flag2Country(filename=text_input)
                            menu_obj.state = "PlayFlag2Country"
                            return fresh_game_obj
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
                    Flag2CountryMixin.quit_game(None, None)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "StartMenu"
                            return
                        elif QUIT_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            Flag2CountryMixin.quit_game(None, None)
                        elif SAVED_GAMES_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "SavedGamesMenu"
                            return
                        elif OPTIONS_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()

            pygame.display.update()
            clock.tick(target_fps)

    def settings_menu(self):
        client_conn, server_connection_state = self.try_connect_to_server()
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
                window_width / 1.4, window_height / 2 - window_height / 8 - self.scroll_y))
            LOAD_BACKUP_BUTTON = ImageButton(LOAD_TR, (window_width / 1.4, window_height / 2 - self.scroll_y))

            MUSIK_VOLUME_BAR.bar_y = window_height / 2 + window_height / 8 - self.scroll_y

            SCREEN.blit(WINDOW_SIZE_TEXT, WINDOW_SIZE_RECT)
            SCREEN.blit(SEND_BACKUP_TEXT, SEND_BACKUP_TEXT_RECT)
            SCREEN.blit(LOAD_BACKUP_TEXT, LOAD_BACKUP_TEXT_RECT)
            SCREEN.blit(MUSIC_VOLUME_TEXT, MUSIC_VOLUME_TEXT_RECT)
            SCREEN.blit(FPS_TEXT, FPS_TEXT_RECT)

            MUSIK_VOLUME_BAR.update(SCREEN, GRAY, GREEN)
            if pygame.mouse.get_pressed()[0]:
                if MUSIK_VOLUME_BAR.checkForInput(MOUSE_POS):
                    MUSIK_VOLUME_BAR.set_bar(MOUSE_POS, window_width)
                    pygame.mixer.music.set_volume(MUSIK_VOLUME_BAR.get_volume())

            for button in [WINDOW_SIZE_DROPDOWN, FPS_DROPDOWN, CHECK_FOR_UPDATE_BUTTON]:
                button.changeColor(MOUSE_POS)
                button.update(SCREEN)

            if Window_size_dropdown_state:
                WINDOW_SIZE_DROPDOWN.draw_dropdown(SCREEN, 0.05, MOUSE_POS, (window_width, window_height))

            if FPS_dropdown_state:
                FPS_DROPDOWN.draw_dropdown(SCREEN, 0.05, MOUSE_POS, (window_width, window_height))

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
                    Flag2CountryMixin.quit_game(client_conn, server_connection_state)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Mausrad nach oben
                        self.scroll_y -= self.scroll_speed * 2
                    elif event.button == 5:  # Mausrad nach unten
                        self.scroll_y += self.scroll_speed * 2
                    elif event.button == 1:
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "StartMenu"
                            if server_connection_state:
                                client_conn.sendDisconnect()
                            return

                        elif SAVE_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                        try:
                            if SEND_BACKUP_BUTTON.checkForInput(MOUSE_POS):
                                if server_connection_state is not False:
                                    CLICK_SOUND.play()
                                    client_conn.backupGames()
                                else:
                                    start_time = pygame.time.get_ticks()
                            elif LOAD_BACKUP_BUTTON.checkForInput(MOUSE_POS):
                                if server_connection_state is not False:
                                    CLICK_SOUND.play()
                                    client_conn.loadBackup()
                                else:
                                    start_time = pygame.time.get_ticks()
                            elif CHECK_FOR_UPDATE_BUTTON.checkForInput(MOUSE_POS):
                                if server_connection_state is not False:
                                    CLICK_SOUND.play()
                                    version_up_to_date = client_conn.checkUpdate()
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
                                                    0.07) * 1.5  # Spacing between the lines

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
                    Flag2CountryMixin.quit_game(None, None)
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 4:  # Mouse up
                        self.scroll_y -= self.scroll_speed * 2
                    elif event.button == 5:  # Mouse down
                        self.scroll_y += self.scroll_speed * 2
                    if event.button == 1:
                        count = 0
                        for button in button_obj_list:
                            x, y = button_pos[count]
                            button.y_pos = y - self.scroll_y
                            if button.checkForInput(MOUSE_POS):
                                CLICK_SOUND.play()
                                filename = button.text_input + ".json"
                                file_path = os.path.join("saves", filename)
                                loaded_deck = Recommendation.FlashcardDeck.read_from_json(file_path=file_path)
                                fresh_game_obj = Flag2Country(filename=filename, country_deck=loaded_deck)
                                menu_obj.state = "PlayFlag2Country"
                                return fresh_game_obj
                            count += 1
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            menu_obj.state = "ResumeGameMenu"
                            return
                        if QUIT_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            Flag2CountryMixin.quit_game(None, None)

            pygame.display.update()
            clock.tick(target_fps)


def mainloop():
    while menu_obj.state != "Close":
        if menu_obj.state == "StartMenu":
            menu_obj.start_menu()
        elif menu_obj.state == "NewGameMenu":
            menu_obj.new_game_menu()
        elif menu_obj.state == "ResumeGameMenu":
            menu_obj.resume_game_menu()
        elif menu_obj.state == "CompetitiveModeMenu":
            PVP_GAME_OBJ = menu_obj.competitive_mode_menu()

        elif menu_obj.state == "SettingsMenu":
            menu_obj.settings_menu()

        elif menu_obj.state == "CreateGameMenu":
            GAME_OBJ = menu_obj.create_game_name()
        elif menu_obj.state == "SavedGamesMenu":
            GAME_OBJ = menu_obj.saved_games_menu()

        elif menu_obj.state == "PlayFlag2Country":
            GAME_OBJ.flag2country_quiz()
        elif menu_obj.state == "Flag2CountryWrongA":
            GAME_OBJ.false_answer_screen()
        elif menu_obj.state == "Flag2CountryRightA":
            GAME_OBJ.true_answer_screen()

        elif menu_obj.state == "PVP":
            PVP_GAME_OBJ.draw_screen()
        elif menu_obj.state == "EndScreen":
            PVP_GAME_OBJ.end_screen()


if __name__ == "__main__":
    menu_obj = Menu("0.1")
    mainloop()
