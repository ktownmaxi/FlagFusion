import pycountry
import pycountry_convert
import pygame, sys
from pygame_textinput import TextInputVisualizer, TextInputManager
from button import Button, Button_xy_cords
import random
import os
import Recommendation
import datetime
import MusicManager

pygame.init()
pygame.mixer.init()
pygame.mixer.music.set_endevent(pygame.USEREVENT)

#window_width, window_height = 1080, 720
window_width, window_height = 2560, 1440

SCREEN = pygame.display.set_mode((window_width, window_height))
pygame.display.set_caption("Flags")

BG_img = pygame.image.load("assets/Background.jpg")
BG = pygame.transform.scale(BG_img, (window_width, window_height))

# global sounds
CLICK_SOUND = pygame.mixer.Sound('assets/tones/click.mp3')

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

target_fps = 30
clock = pygame.time.Clock()

music_manager_obj = MusicManager.MusicManager()
next_song = music_manager_obj.get_next_song()
pygame.mixer.music.load(os.path.join('assets/music', next_song))
pygame.mixer.music.set_volume(0.35)
pygame.mixer.music.play()


def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)


def calculate_font_size(window_width_, window_height_, font_size_factor):
    font_size = int(min(window_width_,
                        window_height_) * font_size_factor)  # font_size_factor = occupied screen area in dec. prozent
    return font_size


class Flag2Country():
    pos_count = 0
    correct_sound = pygame.mixer.Sound("assets/tones/correct.mp3")
    incorrect_sound = pygame.mixer.Sound("assets/tones/wrong.mp3")
    current_datetime = datetime.datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d_%H-%M-%S")
    start_time = None
    elapsed_time = 0

    def __init__(self, gameversion=str(0.1), country_deck=None, streak=0,
                 filename=f"Gamesave_ID_1{formatted_datetime}.json"):
        self.country_deck = country_deck
        self.country_name = ""
        self.countries = pycountry.countries
        self.list_of_countries = []
        self.list_of_choosen_countries = []  # Liste der random ausgewählten Länder
        self.pos_list = [(window_width / 2 - window_width / 2.125, window_height / 2),  # 1 oben links
                         (window_width / 2 + window_width / 15, window_height / 2),
                         (window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4),
                         (
                             window_width / 2 + window_width / 15,
                             window_height / 2 + window_height / 4)]  # 4 unten rechts
        self.picked_flag = ""
        self.FLAG_WIDTH, self.FLAG_HEIGHT = window_width / 3.5, window_height / 3.5
        self.streak = streak
        self.card = None
        self.filename = filename
        self.game_version = gameversion

    def detect_duplicates(self, my_list):
        duplicates = False
        for value in my_list:
            if my_list.count(value) > 1:
                duplicates = True
            else:
                pass
        return duplicates

    def read_saved_data(self):
        pass

    def increase_streak(self):
        self.streak = self.streak + 1

    def reset_streak(self):
        self.streak = 0

    def value_generator(self, obj):
        detect_duplicate_list = []
        self.list_of_choosen_countries.clear()
        self.card = self.country_deck.get_next_value()
        self.picked_flag = self.card.value[1]
        self.country_name = self.card.value[0]

        for i in range(0, 3):
            cache = self.country_deck.get_random_card()
            self.list_of_choosen_countries.append(
                cache.value[0])  # Wählt 3 random Items aus dieser Liste aus und fügt sie einer anderen an
        dupicate = obj.detect_duplicates(detect_duplicate_list)

        if dupicate:
            obj.draw(obj=obj)
            print("Double Detected")

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

    def assign_pos(self):
        if not self.pos_list:
            Flag2Country.pos_count = 0
            self.pos_list = [(window_width / 2 - window_width / 2.125, window_height / 2),  # 1 oben links
                             (window_width / 2 + window_width / 15, window_height / 2),
                             (window_width / 2 - window_width / 2.125, window_height / 2 + window_height / 4),
                             (window_width / 2 + window_width / 15, window_height / 2 + window_height / 4)]
            return

        pos_var_name = "pos_" + str(Flag2Country.pos_count + 1)
        random_tuple = random.choice(self.pos_list)
        setattr(self, pos_var_name, random_tuple)
        self.pos_list.remove(random_tuple)
        Flag2Country.pos_count += 1

        self.assign_pos()  # Rekursiver Aufruf

    def wrong_answer(self, obj):
        self.incorrect_sound.play()
        obj.reset_streak()
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = None
        self.country_deck.update_card(self.card, True, self.elapsed_time)
        obj.false_answer_screen(obj=obj)

    def right_answer(self, obj):
        self.correct_sound.play()
        obj.increase_streak()
        self.elapsed_time += pygame.time.get_ticks() - self.start_time
        self.start_time = None
        self.country_deck.update_card(self.card, False, self.elapsed_time)
        obj.true_answer_screen(obj=obj)

    def save(self):
        CLICK_SOUND.play()
        self.country_deck.write_to_json(obj=self.country_deck, filename=self.filename)
        print("saved")

    def draw(self, obj):

        obj.create_game_deck_generation()
        obj.value_generator(obj)
        obj.assign_pos()
        self.start_time = None
        self.elapsed_time = 0
        self.start_time = pygame.time.get_ticks()
        while True:
            DRAW_MOUSE_POS = pygame.mouse.get_pos()

            SCREEN.fill("#353a3c")  # Erschafft Illusion von einem neuen Fenster / #353a3c

            answer_1 = Button_xy_cords(image=None, pos=obj.pos_1,
                                       text_input=self.list_of_choosen_countries[0],
                                       font=get_font(calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_2 = Button_xy_cords(image=None, pos=obj.pos_2,
                                       text_input=self.list_of_choosen_countries[1],
                                       font=get_font(calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_3 = Button_xy_cords(image=None, pos=obj.pos_3,
                                       text_input=self.list_of_choosen_countries[2],
                                       font=get_font(calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            answer_4 = Button_xy_cords(image=None, pos=obj.pos_4,
                                       text_input=self.country_name,
                                       font=get_font(calculate_font_size(window_width, window_height, 0.05)),
                                       base_color="White",
                                       hovering_color="Light Blue")

            flag_img = pygame.image.load(
                os.path.join('flags', self.picked_flag)
            )
            flag = pygame.transform.scale(flag_img, (self.FLAG_WIDTH, self.FLAG_HEIGHT))
            SCREEN.blit(flag, (window_width / 2 - self.FLAG_WIDTH / 2, window_height / 9))

            for button in [answer_1, answer_2, answer_3, answer_4]:
                button.changeColor(DRAW_MOUSE_POS)
                button.update(SCREEN)

            if self.start_time is not None:
                elapsed_time_display = self.elapsed_time + (pygame.time.get_ticks() - self.start_time)
            else:
                elapsed_time_display = self.elapsed_time

            seconds = elapsed_time_display // 1000
            milliseconds = elapsed_time_display % 1000

            seconds_text = get_font(calculate_font_size(window_width, window_height, 0.03)).render(
                f"Time: {seconds} seconds", True, WHITE)
            milliseconds_text = get_font(calculate_font_size(window_width, window_height, 0.03)).render(
                f"and {milliseconds} ms", True, WHITE)
            SCREEN.blit(seconds_text, (window_width / 2 + self.FLAG_WIDTH - window_width / 10, window_height / 9))
            SCREEN.blit(milliseconds_text, (window_width / 2 + self.FLAG_WIDTH - window_width / 10, window_height / 6))

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        if obj.pos_4 == (50, 325):
                            obj.right_answer(obj)
                    if event.key == pygame.K_2:
                        if obj.pos_4 == (700, 325):
                            obj.right_answer(obj)
                    if event.key == pygame.K_3:
                        if obj.pos_4 == (50, 550):
                            obj.right_answer(obj)
                    if event.key == pygame.K_4:
                        if obj.pos_4 == (700, 550):
                            obj.right_answer(obj)
                    else:
                        obj.wrong_answer(obj)


                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if answer_1.checkForInput(DRAW_MOUSE_POS):
                            obj.wrong_answer(obj)
                        elif answer_2.checkForInput(DRAW_MOUSE_POS):
                            obj.wrong_answer(obj)
                        elif answer_3.checkForInput(DRAW_MOUSE_POS):
                            obj.wrong_answer(obj)
                        elif answer_4.checkForInput(DRAW_MOUSE_POS):
                            obj.right_answer(obj)

                elif event.type == pygame.USEREVENT:
                    pygame.mixer.music.load(os.path.join('assets/music', music_manager_obj.get_next_song()))
                    pygame.mixer.music.play()

            pygame.display.update()
            clock.tick(target_fps)

    def true_answer_screen(self, obj):  # Obj wird übergeben deshalb länder nicht mehr random
        while True:
            TRUE_MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("#353a3c")

            heading_text = get_font(calculate_font_size(window_width, window_height, 0.09)).render("Richtige Antwort",
                                                                                                   True, "Green")
            heading_rect = heading_text.get_rect(center=(window_width / 2, window_height / 9))
            SCREEN.blit(heading_text, heading_rect)

            streak_text = get_font(calculate_font_size(window_width, window_height, 0.04)).render(
                f"Streak: {self.streak}", True, "White")
            streak_rect = streak_text.get_rect(center=(window_width / 2 - window_width / 3, window_height / 2))
            SCREEN.blit(streak_text, streak_rect)

            next_button = Button(image=None,
                                 pos=(window_width / 2 - window_width / 2.75, window_height / 2 + window_height / 2.75),
                                 text_input="Next",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            menu_button = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 2.75),
                                 text_input="Menu",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            save_button = Button(image=None,
                                 pos=(window_width / 2 + window_width / 2.5, window_height / 2 + window_height / 2.75),
                                 text_input="Save",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            for button in [next_button, menu_button, save_button]:
                button.changeColor(TRUE_MOUSE_POS)
                button.update(SCREEN)

            seconds = self.elapsed_time // 1000
            milliseconds = self.elapsed_time % 1000

            time_text = get_font(calculate_font_size(window_width, window_height, 0.03)).render(
                f"Guessed right in:", True, WHITE)
            clock_text = get_font(calculate_font_size(window_width, window_height, 0.03)).render(
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
                        obj.draw(obj=obj)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if next_button.checkForInput(TRUE_MOUSE_POS):
                            CLICK_SOUND.play()
                            obj.draw(obj=obj)
                        if menu_button.checkForInput(TRUE_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.main_menu()
                        if save_button.checkForInput(TRUE_MOUSE_POS):
                            obj.save()

            pygame.display.update()
            clock.tick(target_fps)

    def false_answer_screen(self, obj):
        while True:
            FALSE_MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.fill("#353a3c")
            heading_text = get_font(calculate_font_size(window_width, window_height, 0.09)).render("Falsche Antwort",
                                                                                                   True, "Red")
            heading_rect = heading_text.get_rect(center=(window_width / 2, window_height / 9))
            SCREEN.blit(heading_text, heading_rect)

            correct_country_text = get_font(calculate_font_size(window_width, window_height, 0.04)).render(
                self.country_name, True, "Green")
            correct_country_rect = correct_country_text.get_rect(
                center=(window_width / 2 + window_width / 3, window_height / 2))
            SCREEN.blit(correct_country_text, correct_country_rect)

            streak_text = get_font(calculate_font_size(window_width, window_height, 0.04)).render(
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
                                 font=get_font(calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            menu_button = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 2.75),
                                 text_input="Menu",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.06)),
                                 base_color="WHITE",
                                 hovering_color="Light Blue")

            save_button = Button(image=None,
                                 pos=(window_width / 2 + window_width / 2.5, window_height / 2 + window_height / 2.75),
                                 text_input="Save",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.06)),
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
                        obj.draw(obj=obj)

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if next_button.checkForInput(FALSE_MOUSE_POS):
                            CLICK_SOUND.play()
                            obj.draw(obj=obj)
                        if menu_button.checkForInput(FALSE_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.main_menu()
                        if save_button.checkForInput(FALSE_MOUSE_POS):
                            obj.save()

            pygame.display.update()
            clock.tick(target_fps)


class Menu_windows:

    def __init__(self, scroll_x=0, scroll_y=0, scroll_speed=10):
        self.scroll_x = scroll_x
        self.scroll_y = scroll_y
        self.scroll_speed = scroll_speed

    def main_menu(self):
        while True:
            SCREEN.blit(BG, (0, 0))

            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = get_font(calculate_font_size(window_width, window_height, 0.12)).render("MAIN MENU", True,
                                                                                                "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            NEWGAME_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                    text_input="New Game",
                                    font=get_font(calculate_font_size(window_width, window_height, 0.09)),
                                    base_color="White", hovering_color="#dadddd")
            RESUME_BUTTOM = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                   text_input="Resume",
                                   font=get_font(calculate_font_size(window_width, window_height, 0.09)),
                                   base_color="White",
                                   hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 3.75),
                                 text_input="QUIT",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.09)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [NEWGAME_BUTTON, RESUME_BUTTOM, QUIT_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if NEWGAME_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.new_game_menu()
                        if RESUME_BUTTOM.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.resume_game_menu()

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

            MENU_TEXT = get_font(calculate_font_size(window_width, window_height, 0.08)).render("CREATE A NEW GAME",
                                                                                                True, "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            PLAY_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                 text_input="Flag2Country",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White",
                                 hovering_color="#dadddd")
            COUNTRY2FLAG_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                         text_input="Country2Flag",
                                         font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                         base_color="White",
                                         hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="QUIT",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")
            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="BACK",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, COUNTRY2FLAG_BUTTON, QUIT_BUTTON, BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.create_gamename()
                        if COUNTRY2FLAG_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()

                        if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.main_menu()
                        if QUIT_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            clock.tick(target_fps)

    def create_gamename(self):
        manager = TextInputManager(validator=lambda input: len(input) <= 15)
        font = pygame.font.SysFont("Consolas", calculate_font_size(window_width, window_height, 0.07))
        textinput_custom = TextInputVisualizer(manager=manager, font_object=font)
        textinput_custom.cursor_width = 2
        textinput_custom.cursor_blink_interval = 400  # ms
        textinput_custom.antialias = False
        textinput_custom.font_color = (0, 0, 0)

        text_input = None

        while True:
            SCREEN.blit(BG, (0, 0))
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            MENU_TEXT = get_font(calculate_font_size(window_width, window_height, 0.09)).render("Name the Game", True,
                                                                                                "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            CONFIRM_BUTTON = Button(image=None,
                                    pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3),
                                    text_input="CONFIRM",
                                    font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                    base_color="White",
                                    hovering_color="#dadddd")
            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="BACK",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SCREEN.blit(MENU_TEXT, MENU_RECT)

            event = pygame.event.get()
            textinput_custom.update(event)
            SCREEN.blit(textinput_custom.surface, (window_width / 2 - window_width / 7, window_height / 2))

            for button in [CONFIRM_BUTTON, BACK_BUTTON]:
                button.changeColor(MENU_MOUSE_POS)
                button.update(SCREEN)

            for event in event:
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_ENTER:
                        CLICK_SOUND.play()
                        text_input = textinput_custom.value
                    if event.key == pygame.K_RETURN:
                        CLICK_SOUND.play()
                        text_input = textinput_custom.value

                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if CONFIRM_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            text_input = textinput_custom.value
                            text_input = text_input + ".json"
                            game_obj = Flag2Country(filename=text_input)
                            game_obj.draw(game_obj)
                        if BACK_BUTTON.checkForInput(MENU_MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.main_menu()

            pygame.display.update()
            clock.tick(target_fps)

    def resume_game_menu(self):
        while True:
            MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.blit(BG, (0, 0))

            MENU_TEXT = get_font(calculate_font_size(window_width, window_height, 0.09)).render("RESUME A GAME",
                                                                                                True, "#f1f25f")
            MENU_RECT = MENU_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="QUIT",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 4, window_height / 2 + window_height / 3),
                                 text_input="BACK",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White", hovering_color="#dadddd")

            SAVED_GAMES_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2.5),
                                        text_input="SAVED_GAMES_BUTTON",
                                        font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                        base_color="White",
                                        hovering_color="#dadddd")

            OPTIONS_BUTTON = Button(image=None, pos=(window_width / 2, window_height / 2 + window_height / 14),
                                    text_input="OPTIONS_BUTTON",
                                    font=get_font(calculate_font_size(window_width, window_height, 0.07)),
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
                            GAME_OBJEKT.main_menu()
                        elif QUIT_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()
                        elif SAVED_GAMES_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.saved_games_menu()
                        elif OPTIONS_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.resume_game_options_menu()

            pygame.display.update()
            clock.tick(target_fps)

    def saved_games_menu(self):
        BG_header_img = pygame.image.load("assets/Background-heading.jpg")
        BG_header = pygame.transform.scale(BG_header_img, (window_width, window_height / 4.431))

        scroll_window_width = window_width
        scroll_window_height = window_height * 10
        count = 0
        relativ_x = window_width / 2
        relativ_y = window_height / 2 - window_height / 6

        CARD_DECK_OBJEKT = Recommendation.FlashcardDeck()
        game_buttons = CARD_DECK_OBJEKT.get_json_names()

        content_surface = pygame.Surface((scroll_window_width, scroll_window_height), pygame.SRCALPHA)

        button_obj_list = []
        button_pos = []

        for button in game_buttons:
            button_pos.append((relativ_x, relativ_y))
            relativ_y += calculate_font_size(window_width, window_height, 0.07) * 1.5  # Spacing zwischen den Zeilen

        while True:
            MOUSE_POS = pygame.mouse.get_pos()
            SCREEN.blit(BG, (0, 0))

            button_obj_list.clear()
            for count, text in enumerate(game_buttons):
                x, y = button_pos[count]
                if count >= len(game_buttons):  # reset count wenn größer als anzahl buttons
                    count = 0
                    continue
                else:
                    pos_var_name = "BUTTON" + str(count)  # game_buttons[count]
                    setattr(self, pos_var_name, Button(image=None, pos=(relativ_x, y - self.scroll_y),
                                                       text_input=game_buttons[count],
                                                       font=get_font(
                                                           calculate_font_size(window_width, window_height, 0.07)),
                                                       base_color="White", hovering_color="#dadddd"))

                    button_instance = getattr(self, pos_var_name)
                    button_obj_list.append(button_instance)
                    button_instance.changeColor(MOUSE_POS)
                    button_instance.update(SCREEN)
                count += 1

            visible_area = pygame.Rect(self.scroll_x, self.scroll_y, window_width, window_height)
            SCREEN.blit(content_surface, (50, 150), area=visible_area)

            self.scroll_x = max(0, min(self.scroll_x, scroll_window_width - window_width))
            self.scroll_y = max(0, min(self.scroll_y, scroll_window_height - window_height))

            HEADING_TEXT = get_font(calculate_font_size(window_width, window_height, 0.12)).render("SAVED GAMES", True,
                                                                                                   "#f1f25f")
            HEADING_RECT = HEADING_TEXT.get_rect(center=(window_width / 2, window_height / 7))

            BACK_BUTTON = Button(image=None,
                                 pos=(window_width / 2 - window_width / 2.5, window_height / 2 + window_height / 8),
                                 text_input="BACK",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
                                 base_color="White",
                                 hovering_color="#dadddd")
            QUIT_BUTTON = Button(image=None,
                                 pos=(window_width / 2 + window_width / 2.5, window_height / 2 + window_height / 8),
                                 text_input="QUIT",
                                 font=get_font(calculate_font_size(window_width, window_height, 0.07)),
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
                                resume_game_obj = Flag2Country(filename=filename, country_deck=loaded_deck)
                                resume_game_obj.draw(resume_game_obj)
                            count += 1
                        if BACK_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            GAME_OBJEKT.resume_game_menu()

                        if QUIT_BUTTON.checkForInput(MOUSE_POS):
                            CLICK_SOUND.play()
                            pygame.quit()
                            sys.exit()

            pygame.display.update()
            clock.tick(target_fps)

    def resume_game_options_menu(self):
        pass


GAME_OBJEKT = Menu_windows()
GAME_OBJEKT.main_menu()
