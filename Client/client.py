import socket
import pickle
import os

HEADER = 64
PORT = 5050
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
SERVER = '192.168.178.45'
ADDR = (SERVER, PORT)
game_version = '0.1'

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect(ADDR)


def send(msg_type):
    global send_msg_type
    if msg_type == 'SyncHighscore':
        send_msg_type = str(1).encode()
        client.send(send_msg_type)

    if msg_type == '1v1':
        send_msg_type = str(2).encode()
        client.send(send_msg_type)

    if msg_type == 'checkUpdate':
        send_msg_type = str(3).encode()
        client.send(send_msg_type)

        game_version_pickle = pickle.dumps(game_version)  # Transforms Game version to pickle objekt
        msg_length = len(game_version_pickle)
        msg_length_header = f"{msg_length:<{HEADER}}".encode()  # Makes msg_length into a header

        client.send(msg_length_header)
        client.send(game_version_pickle)

        msg_length_header = client.recv(HEADER)
        msg_length = int(msg_length_header.decode().strip())
        if msg_length:
            msg_length = int(msg_length)
            msg = b""
            while len(msg) < msg_length:
                chunk = client.recv(msg_length - len(msg))
                if not chunk:
                    # Verbindung geschlossen oder Daten verloren
                    break
                msg += chunk
            data = pickle.loads(msg)
            if data:
                print("Everything up to date")
            else:
                print("your Application needs a update")

    if msg_type == 'BackupGames':
        for file in os.listdir('saves'):
            send_msg_type = str(4).encode()
            client.send(send_msg_type)

            filename_bytes = str(file).encode()
            msg_length = len(filename_bytes)
            msg_length_header = f"{msg_length:<{HEADER}}".encode()
            client.send(msg_length_header)
            client.send(filename_bytes)  # Sends the filenames to the server

            file_path = os.path.join('saves', file)
            with open(file_path, 'r') as reading_file:
                data = reading_file.read()
                data_bytes = data.encode()
                msg_length = len(data_bytes)
                msg_length_header = f"{msg_length:<{HEADER}}".encode()
                client.send(msg_length_header)
                client.send(data_bytes)  # sends the json file in bytes to the Server

    if msg_type == 'LoadBackup':
        send_msg_type = str(5).encode()
        client.send(send_msg_type)
        element_count = client.recv(8).decode()

        saves_dir_path = os.path.join('saves')

        if int(element_count) > 0:
            for i in range(0, int(element_count)):
                msg_length_header = client.recv(HEADER)
                msg_length = int(msg_length_header.decode().strip())
                filename = client.recv(msg_length).decode()
                file_path = os.path.join(saves_dir_path, filename)

                msg_length_header = client.recv(HEADER)
                msg_length = int(msg_length_header.decode().strip())
                data = client.recv(msg_length).decode()

                with open(file_path, 'w') as file:
                    file.write(data)
        else:
            print("You haven't any Backup data")

    if msg_type == 'Disconnect':
        send_msg_type = str(6).encode()
        client.send(send_msg_type)
