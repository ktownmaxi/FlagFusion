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
        self.player_ready = False

    @staticmethod
    def read_json(json_file_path):
        with open(json_file_path, 'r') as json_datei:
            file = json.load(json_datei)
            return file

    @staticmethod
    def recv_data(conn, msg_length):
        msg = b""
        while len(msg) < msg_length:
            chunk = conn.recv(msg_length - len(msg))
            if not chunk:
                # Connection closed or data lost
                break
            msg += chunk
        return msg

    def create_flag_list(self):
        final_countries = []
        for i in range(0, 20):
            random_country = random.choice(self.flag_file_names)
            final_countries.append(random_country)
        if self.detect_duplicates(final_countries):
            self.create_flag_list()
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

    def setup(self):
        print("started setup")
        self.send_ready()
        flag_table = self.create_flag_list()
        if self.check_player_count():
            self.send_flag_table(flag_table)

    def check_player_count(self):
        if len(self.player_list) % 2 == 0 and len(self.player_list) >= 2:
            return True

    def send_ready(self):
        for client in self.player_list:
            if client.fileno() != -1:  # Checks if Socket is active
                temp_ready_bool = pickle.dumps(True)
                msg_length = len(temp_ready_bool)
                msg_length_header = f"{msg_length:<{HEADER}}".encode()
                try:
                    client.send(msg_length_header)
                    client.send(temp_ready_bool)
                    self.player_ready = True
                except OSError as e:
                    print(f"Error by trying to contact: {e}")

    def recv_score(self, client_obj):
        score = client_obj.recv(1024).decode()
        self.send_score(client_obj, score)

    def send_score(self, client_obj, score):
        player_list_copy = self.player_list.copy()
        player_list_copy.remove(client_obj)
        player_list_copy[0].send(str(score).encode())
