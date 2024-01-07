import pickle

import Game
from client import ClientConnection

HEADER = 64


class WithServerCommunicationClient:
    def __init__(self, client_objekt):
        self.client_obj = client_objekt

    @Game.Flag2CountryMixin.run_once
    def recv_flag_list(self):
        msg_length_header = self.client_obj.recv(HEADER)
        msg_length = int(msg_length_header.decode().strip())
        if msg_length:
            data = ClientConnection.recv_data(self.client_obj, msg_length)
            enc_data = pickle.loads(data)
            return enc_data

    def recv_player_ready(self):
        msg_length_header = self.client_obj.recv(HEADER)
        msg_length = int(msg_length_header.decode().strip())
        if msg_length:
            data = ClientConnection.recv_data(self.client_obj, msg_length)
            enc_data = pickle.loads(data)
            return enc_data

    def send_score_to_server(self, score, q):
        score_dec = str(score).encode()
        self.client_obj.send(score_dec)
        self.recv_score_from_server(q)

    def recv_score_from_server(self, q):
        score = self.client_obj.recv(1024).decode()
        q.put(score)
