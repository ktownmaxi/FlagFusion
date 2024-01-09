import pickle
import queue

import Game
from client import ClientConnection

HEADER = 64


class WithServerCommunicationClient:
    """
    Class to communicate with the server in the 1v1 mode.
    """
    def __init__(self, client_objekt):
        """
        Initializes an object of ClientConnection
        :param client_objekt:
        """
        self.client_obj = client_objekt

    @Game.Flag2CountryMixin.run_once
    def recv_flag_list(self) -> list:
        """
        Method to receive a list of flags from the server.
        :return: the decoded data in a list
        """
        msg_length_header = self.client_obj.recv(HEADER)
        msg_length = int(msg_length_header.decode().strip())
        if msg_length:
            data = ClientConnection.recv_data(self.client_obj, msg_length)
            enc_data = pickle.loads(data)
            return enc_data

    def recv_player_ready(self) -> bool:
        """
        Method to receive a bool when all instances are ready to start the game.
        :return: The boolean if all instances are ready
        """
        msg_length_header = self.client_obj.recv(HEADER)
        msg_length = int(msg_length_header.decode().strip())
        if msg_length:
            data = ClientConnection.recv_data(self.client_obj, msg_length)
            enc_data = pickle.loads(data)
            return enc_data

    def send_score_to_server(self, score: int, q: queue.Queue):
        """
        Method to send the own score to the server.
        :param score: Score which should be sent to the server.
        :param q: Queue object which is passed on to recv_score_from_server method.
        :return:
        """
        score_dec = str(score).encode()
        self.client_obj.send(score_dec)
        self.recv_score_from_server(q)

    def recv_score_from_server(self, q: queue.Queue):
        """
        Method which receives a score from the server and puts it in a Queue object.
        :param q: Queue object to put the score in.
        :return:
        """
        score = self.client_obj.recv(1024).decode()
        q.put(score)
