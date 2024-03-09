import os.path
import zipfile
import io
from glob import glob

import requests

BASE = "http://127.0.0.1:5000/"
headers_json, headers_zip = {"Content-Type": "application/json"}, {"Content-Type": "application/zip"}


def get_in_queue_and_get_matchmaking_status():
    response = requests.put(BASE + "matchmaking")
    matchmaking_status = response.json()["started_matchmaking"]
    if response.json()["player_id"]:
        player_id = response.json()["player_id"]
    else:
        player_id = None
    return matchmaking_status, player_id


def only_get_matchmaking_status(player_id):
    response = requests.get(BASE + "matchmaking", json={"player_id": player_id})
    matchmaking_status = response.json()["started_matchmaking"]
    return matchmaking_status


def get_current_game_version():
    response = requests.get(BASE + "update")
    gversion = response.json()["gversion"]
    return gversion


def get_backup():
    response = requests.get(BASE + "backup", headers=headers_json)
    if response.status_code == 200:
        with zipfile.ZipFile(io.BytesIO(response.content), 'r') as zip_ref:
            zip_ref.extractall(os.path.join("saves"))


def post_backup():  # Not finished
    extract_path = os.path.join("saves")
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, "w") as zf:
        for file in glob(os.path.join(extract_path, "*.json")):
            zf.write(file, os.path.basename(file))
    stream.seek(0)
    response = requests.post(BASE + "backup", headers=headers_zip, files={'file': ('downloaded_files.zip', stream)})
    return response


def get_country_list():
    response = requests.get(BASE + "communicationAPI")
    return response.json()


def patch_score_to_api(current_score, current_acc, player_id):
    response = requests.patch(BASE + "communicationAPI", json={"score": current_score, "acc": current_acc,
                                                               "id": player_id})
    score, acc, finished = response.json()["score"], response.json()["acc"], response.json()["game_finished"]
    return score, acc, finished


def post_finish(player_id):
    response = requests.post(BASE + "communicationAPI", json={"game_finished": True, "player_id": player_id})

    return response
