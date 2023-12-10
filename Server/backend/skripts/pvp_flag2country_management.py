import json
import os
import pickle
import random

current_dir = os.path.dirname(os.path.abspath(__file__))
HEADER = 64


class Server_side_pvp:

    def __init__(self, server_objekt):
        self.flag_file_names = self.read_json(os.path.join(current_dir, '..', 'resources', 'flag_name.json'))
        self.number_questions = 20
        self.player_list = []
        self.server_obj = server_objekt

    @staticmethod
    def read_json(json_file_path):
        with open(json_file_path, 'r') as json_datei:
            file = json.load(json_datei)
            return file

    def create_flag_table(self):
        final_countries = []
        for i in range(0, 20):
            random_country = random.choice(self.flag_file_names)
            final_countries.append(random_country)
        if self.detect_duplicates(final_countries):
            self.create_flag_table()
        return final_countries

    @staticmethod
    def detect_duplicates(my_list):
        duplicates = False
        for value in my_list:
            if my_list.count(value) > 1:
                duplicates = True
            else:
                pass
        return duplicates

    def send_flag_table(self, table):
        for client in self.player_list:
            temp_list = pickle.dumps(table)
            msg_length = len(temp_list)
            msg_length_header = f"{msg_length:<{HEADER}}".encode()
            client.send(msg_length_header)
            client.send(temp_list)
        print("send")

    def setup(self):
        print("started setup")
        flag_table = self.create_flag_table()
        if self.check_player_count():
            self.send_flag_table(flag_table)

    def check_player_count(self):
        if len(self.player_list) == 2:
            return True

    def send_ready(self):
        for client in self.player_list:
            temp_ready_bool = pickle.dumps(True)
            msg_length = len(temp_ready_bool)
            msg_length_header = f"{msg_length:<{HEADER}}".encode()
            client.send(msg_length_header)
            client.send(temp_ready_bool)
        print("send ready")
