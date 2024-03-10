import os.path
import zipfile
import io
from glob import glob
import helper

import requests

BASE = "http://127.0.0.1:5000/"
headers_json, headers_zip = {"Content-Type": "application/json"}, {"Content-Type": "application/zip"}


def get_in_queue_and_get_matchmaking_status() -> tuple:
    """
    This function sends a PUT request to the matchmaking endpoint and retrieves the matchmaking status and player ID.
    It does not take any parameters and returns a tuple containing the matchmaking status and player ID.
    :returns: tuple of matchmaking status and player ID
    """

    response = requests.put(BASE + "matchmaking")
    matchmaking_status = response.json()["started_matchmaking"]
    if response.json()["player_id"]:
        player_id = response.json()["player_id"]
    else:
        player_id = None
    return matchmaking_status, player_id


@helper.run_once_a_second
def only_get_matchmaking_status(player_id) -> bool:
    """
    A function that gets the matchmaking status for a player.

    Args:
        player_id (str): The ID of the player.

    Returns:
        bool: The matchmaking status for the player.
    """
    response = requests.get(BASE + "matchmaking", json={"player_id": player_id})
    matchmaking_status = response.json()["started_matchmaking"]
    return matchmaking_status


def get_current_game_version() -> int:
    """
    Get the current game version.

    :return: gversion as a string
    """
    response = requests.get(BASE + "update")
    gversion = response.json()["gversion"]
    return gversion


def get_backup():
    """
    Function to retrieve a backup from the server and save it to the specified directory.
    """
    response = requests.get(BASE + "backup", headers=headers_json)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
            zip_ref.extractall(os.path.join("../saves"))


def post_backup():
    pass

def get_country_list() -> dict:
    """
    Retrieves a list of countries from the communicationAPI endpoint and returns the response in JSON format.
    :returns: dict
    """
    response = requests.get(BASE + "communicationAPI")
    return response.json()


def patch_score_to_api(current_score, current_acc, player_id):
    """
    Update the score and accuracy of a player via an API patch request.

    Args:
        current_score (int): The current score of the player.
        current_acc (float): The current accuracy of the player.
        player_id (str): The unique identifier of the player.

    Returns:
        tuple: A tuple containing the updated score (int), accuracy (float), and a flag indicating if the game is finished.
    """
    response = requests.patch(BASE + "communicationAPI", json={"score": current_score, "acc": current_acc,
                                                               "id": player_id})
    score, acc, finished = response.json()["score"], response.json()["acc"], response.json()["game_finished"]
    return score, acc, finished


def post_finish(player_id) -> requests.Response:
    """
    Function to finish the game
    :param player_id: ID of the player
    :return: response
    """
    response = requests.post(BASE + "communicationAPI", json={"game_finished": True, "player_id": player_id})

    return response


def leave_queue(player_id) -> requests.Response:
    """
    Function to leave the matchmaking queue
    :param player_id: ID of the player
    :return: resonse
    """
    response = requests.patch(BASE + "matchmaking", json={"player_id": player_id})
    return response


@helper.run_once
def ping_server():
    """
    Function to check if the server is online
    """
    response = requests.get(BASE + "ping")
    server_state = response.json()["server_online"]
    return server_state


print(post_backup().text)
