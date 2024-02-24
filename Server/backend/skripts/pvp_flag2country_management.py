import json
import os
import pickle
import random
from socket import socket

current_dir = os.path.dirname(os.path.abspath(__file__))
HEADER = 64


class Server_side_pvp:
    """Class to handel the communication and data processing for the pvp mode on the server side"""

    def __init__(self, server_objekt):
        """
        Initializes parameters
        :param server_objekt: Instance of a server object
        """
        self.flag_file_names = self.read_json(os.path.join(current_dir, '..', 'resources', 'flag_name.json'))
        self.number_questions = 20
        self.player_list = []
        self.server_obj = server_objekt
        self.player_ready = False

    @staticmethod
    def read_json(json_file_path: str) -> dict:
        """Method to read a json file
            :param path json_file_path: Path to find the json file.
            :returns : Returns a Dictionary with the information from the file
            :rtype : Returns a Dictionary
            :raises anyError: if something goes wrong"""

        with open(json_file_path, 'r') as json_datei:
            file = json.load(json_datei)
            return file

    @staticmethod
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
                break
            msg += chunk
        return msg

    def create_flag_list(self) -> list:
        """
        Method to create a list with 20 items of random flag file names
        :return: a list of the chosen countries
        """
        final_countries = []
        for i in range(0, 20):
            random_country = random.choice(self.flag_file_names)
            final_countries.append(random_country)
        if self.detect_duplicates(final_countries):
            self.create_flag_list()
        return final_countries

    @staticmethod
    def detect_duplicates(my_list: list) -> bool:
        """
        Method to detect duplicates in a given list.
        :param my_list: list which should be checked on duplicates.
        :return: returns a bool if a duplicate was detected
        """
        duplicates = False
        for value in my_list:
            if my_list.count(value) > 1:
                duplicates = True
            else:
                pass
        return duplicates

    def send_flag_table(self, table: list | dict):
        """
        A method to decode and send a list of flags to given clients.
        :param table: list which should be sent to the client.
        :return: None
        """
        for client in self.player_list:
            temp_list = pickle.dumps(table)
            msg_length = len(temp_list)
            msg_length_header = f"{msg_length:<{HEADER}}".encode()
            client.send(msg_length_header)
            client.send(temp_list)

    def setup(self):
        """
        Starts the setup process of the communication structure between the server and the clients
        :return: None
        """
        print("started setup")
        self.send_ready()
        flag_table = self.create_flag_list()
        if self.check_player_count():
            self.send_flag_table(flag_table)

    def check_player_count(self) -> bool:
        """
        Checks if a certain player count is met.
        :return: True if player_count is met.
        """
        if len(self.player_list) % 2 == 0 and len(self.player_list) >= 2:
            return True

    def send_ready(self):
        """
        Method to send a bool to the clients - should signal when all parties are ready.
        :return: None
        """
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

    def recv_score(self, client_obj: socket):
        """
        Simple method to receive a score form a client.
        :param client_obj: client socket from which the score should be received.
        :return:
        """
        score = client_obj.recv(1024).decode()
        try:
            self.send_score(client_obj, int(score))
        except ValueError:
            self.send_score(client_obj, int(0))

    def send_score(self, client_obj: socket, score: int):
        """
        Simple method to send the earlier received score to the other client.
        :param client_obj: client socket to which the score should not be sent.
        :param score: score which the other player has gotten.
        :return:
        """
        player_list_copy = self.player_list.copy()
        player_list_copy.remove(client_obj)
        player_list_copy[0].send(str(score).encode())
