import os
import pickle
import socket

HEADER = 64
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"


class ClientConnection:
    def __init__(self, server_ip, game_version, port=5050):
        self.SERVER = server_ip
        self.PORT = port
        self.ADDR = (self.SERVER, self.PORT)
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.game_version = game_version

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

    def reopen_connection(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(self.ADDR)
        self.ADDR = (self.SERVER, self.PORT)

    def send(self, msg_type):
        global send_msg_type
        if msg_type == 'SyncHighscore':
            send_msg_type = str(1).encode()
            self.client.send(send_msg_type)

        if msg_type == '1v1':
            send_msg_type = str(2).encode()
            self.client.send(send_msg_type)

        if msg_type == 'checkUpdate':
            send_msg_type = str(3).encode()
            self.client.send(send_msg_type)

            game_version_pickle = pickle.dumps(game_version)  # Transforms Game version to pickle objekt
            msg_length = len(game_version_pickle)
            msg_length_header = f"{msg_length:<{HEADER}}".encode()  # Makes msg_length into a header

            self.client.send(msg_length_header)
            self.client.send(game_version_pickle)

            msg_length_header = self.client.recv(HEADER)
            msg_length = int(msg_length_header.decode().strip())
            if msg_length:
                msg = ClientConnection.recv_data(self.client, msg_length)
                data = pickle.loads(msg)
                if data:
                    print("Everything up to date")
                    return True
                else:
                    print("your Application needs a update")
                    return False

        if msg_type == 'BackupGames':
            for file in os.listdir('saves'):
                send_msg_type = str(4).encode()
                self.client.send(send_msg_type)

                filename_bytes = str(file).encode()
                msg_length = len(filename_bytes)
                msg_length_header = f"{msg_length:<{HEADER}}".encode()
                self.client.send(msg_length_header)
                self.client.send(filename_bytes)  # Sends the filenames to the server

                file_path = os.path.join('saves', file)
                with open(file_path, 'r') as reading_file:
                    data = reading_file.read()
                    data_bytes = data.encode()
                    msg_length = len(data_bytes)
                    msg_length_header = f"{msg_length:<{HEADER}}".encode()
                    self.client.send(msg_length_header)
                    self.client.send(data_bytes)  # sends the json file in bytes to the Server

        if msg_type == 'LoadBackup':
            send_msg_type = str(5).encode()
            self.client.send(send_msg_type)
            element_count = self.client.recv(8).decode()

            saves_dir_path = os.path.join('saves')

            if int(element_count) > 0:
                for i in range(0, int(element_count)):
                    msg_length_header = self.client.recv(HEADER)
                    msg_length = int(msg_length_header.decode().strip())
                    filename = self.client.recv(msg_length).decode()
                    file_path = os.path.join(saves_dir_path, filename)

                    msg_length_header = self.client.recv(HEADER)
                    msg_length = int(msg_length_header.decode().strip())
                    data = self.client.recv(msg_length).decode()

                    with open(file_path, 'w') as file:
                        file.write(data)
            else:
                print("You haven't any Backup data")

        if msg_type == "":  # For 1vs1 Mode
            send_msg_type = str(6).encode()
            self.client.send(send_msg_type)

        if msg_type == 'Disconnect':
            send_msg_type = str(7).encode()
            self.client.send(send_msg_type)
