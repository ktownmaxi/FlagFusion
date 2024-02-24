import os
import pickle
import socket
import threading

import pvp_flag2country_management as pvp

HEADER = 64
PORT = 5050
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!DISCONNECT"
current_game_version = '0.1'

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)


def handle_client(conn: socket.socket, addr: socket.socket, pvp_server_obj: pvp.Server_side_pvp):
    """
    Handels communication between clients and the server.
    :param conn: Connection to send to and receive data from
    :param addr: Address for data purposes
    :param pvp_server_obj: Class object to manage the communication between server and clients in the 1v1 mode
    :return:
    """

    print(f"New Connection {addr} connected.")
    connected = True
    while connected:
        msg_type = conn.recv(1).decode(FORMAT)
        if msg_type == '1':  # SyncHighscore
            pass
        if msg_type == '2':  # 1v1
            pass
        if msg_type == '3':  # checkUpdate
            msg_length_header = conn.recv(HEADER)
            msg_length = int(msg_length_header.decode().strip())

            if msg_length:
                data = recv_data(conn, msg_length)
                data = pickle.loads(data)

                if data == current_game_version:
                    update_msg = pickle.dumps(True)
                    msg_length = len(update_msg)
                    msg_length_header = f"{msg_length:<{HEADER}}".encode()
                    conn.send(msg_length_header)
                    conn.send(update_msg)
                else:
                    update_msg = pickle.dumps(False)
                    msg_length = len(update_msg)
                    msg_length_header = f"{msg_length:<{HEADER}}".encode()
                    conn.send(msg_length_header)
                    conn.send(update_msg)

        if msg_type == '4':  # Backup Games
            path = f'backups/{addr[0]}'
            directory_path = os.path.join(os.path.dirname(__file__), path)

            if os.path.exists(directory_path):
                msg_length_header = conn.recv(HEADER)
                msg_length = int(msg_length_header.decode().strip())
                filename = conn.recv(msg_length).decode()
                file_path = os.path.join(directory_path, filename)

                msg_length_header = conn.recv(HEADER)
                msg_length = int(msg_length_header.decode().strip())
                data = conn.recv(msg_length).decode()

                with open(file_path, 'w') as file:
                    file.write(data)

            else:
                os.makedirs(directory_path)
                msg_length_header = conn.recv(HEADER)
                msg_length = int(msg_length_header.decode().strip())
                filename = conn.recv(msg_length).decode()
                file_path = os.path.join(directory_path, filename)

                msg_length_header = conn.recv(HEADER)
                msg_length = int(msg_length_header.decode().strip())
                data = conn.recv(msg_length).decode()

                with open(file_path, 'w') as file:
                    file.write(data)

        if msg_type == '5':  # Load Games
            path = f'backups/{addr[0]}'
            directory_path = os.path.join(os.path.dirname(__file__), path)

            if os.path.exists(directory_path):
                element_count = str(len(os.listdir(directory_path))).encode()
                conn.send(element_count)

                for file in os.listdir(directory_path):
                    filename_bytes = str(file).encode()
                    msg_length = len(filename_bytes)
                    msg_length_header = f"{msg_length:<{HEADER}}".encode()
                    conn.send(msg_length_header)
                    conn.send(filename_bytes)

                    file_path = os.path.join(directory_path, file)
                    with open(file_path, 'r') as reading_file:
                        data = reading_file.read()
                        data_bytes = data.encode()
                        msg_length = len(data_bytes)
                        msg_length_header = f"{msg_length:<{HEADER}}".encode()
                        conn.send(msg_length_header)
                        conn.send(data_bytes)

            else:
                element_count = str(0).encode()
                conn.send(element_count)

        if msg_type == '6':  # starting 1vs1 mode
            if conn not in pvp_server_obj.player_list:
                pvp_server_obj.player_list.append(conn)
            if pvp_server_obj.check_player_count():
                pvp_server_obj.setup()
            while not pvp_server_obj.player_ready:
                if pvp_server_obj.player_ready:
                    continue
            while pvp_server_obj.player_ready:
                pvp_server_obj.recv_score(conn)

        if msg_type == '7':
            if conn in pvp_server_obj.player_list:
                pvp_server_obj.player_list.remove(conn)
            connected = False
    print("Connection closed")
    conn.close()


def SyncHighscore():
    """
    Meth
    :return:
    """
    pass

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


def start():
    """Starts the server and does all steps needed to accept new clients"""

    server.listen(2)
    print(f"Server Local IP {SERVER}")
    pvp_server = pvp.Server_side_pvp(server)
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr, pvp_server))
        thread.start()
        print(f" Active Connections {threading.active_count() - 1}")


print("Starting server is starting...!")
start()
