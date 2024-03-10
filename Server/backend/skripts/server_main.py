import json
import random
from glob import glob
from io import BytesIO
from zipfile import ZipFile

from flask import Flask, send_from_directory, request, send_file, jsonify
from flask_restful import Api, Resource, reqparse, fields, marshal_with, abort
from flask_sqlalchemy import SQLAlchemy
import os
import queue

app = Flask(__name__)
api = Api(app)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///player_data.db"
db = SQLAlchemy(app)

current_dir = os.path.dirname(os.path.abspath(__file__))


class Datastorage(db.Model):
    player_id = db.Column(db.Integer, primary_key=True)
    player_score = db.Column(db.Integer, nullable=False)
    player_acc = db.Column(db.Integer, nullable=False)
    matched_player = db.Column(db.Integer, nullable=True)
    game_finished = db.Column(db.Boolean, nullable=True)


with app.app_context():
    db.create_all()

player_queue = queue.Queue()


class Matchmaking(Resource):

    def __init__(self):
        self.matchmaking_status_args = reqparse.RequestParser()
        self.matchmaking_status_args.add_argument("player_id", type=int, help="Player ID to identify Player")

    def put(self):
        if player_queue.empty():
            player_id = self.getID()
            player_queue.put(player_id)

            new_entry = Datastorage(player_id=player_id, player_score=0, player_acc=100, game_finished=False)
            db.session.add(new_entry)
            db.session.commit()

            return {"started_matchmaking": False,
                    "player_id": player_id}, 200
        else:
            global final_flags
            final_flags = CommunicationAPI.create_flag_list()

            player_2_id = self.getID()
            player_1_id = player_queue.get()

            new_entry = Datastorage(player_id=self.getID(), player_score=0, player_acc=100,
                                    matched_player=player_1_id, game_finished=False)
            db.session.add(new_entry)

            player = Datastorage.query.filter_by(player_id=player_1_id).first()
            if player is not None:
                player.matched_player = player_2_id

            db.session.commit()

            return {"started_matchmaking": True,
                    "player_id": player_2_id}, 200

    def get(self):
        args = self.matchmaking_status_args.parse_args()

        player = Datastorage.query.filter_by(player_id=args["player_id"]).first()
        if player and not player_queue.empty():
            return {"started_matchmaking": False}, 200
        if player and player_queue.empty():
            return {"started_matchmaking": True}, 200
        else:
            return "Player not registered", 400

    def patch(self):
        args = self.matchmaking_status_args.parse_args()

        try:
            player_queue.queue.remove(args["player_id"])
            return "Successfully removed player from queue", 200

        except Exception:
            return "Could not find player with this ID in queue", 400

    def getID(self):
        match_id = db.session.query(Datastorage).count() + 1
        return match_id


final_flags = None


class CommunicationAPI(Resource):

    def __init__(self):
        self.score_patch_args = reqparse.RequestParser()
        self.score_patch_args.add_argument("score", type=int, help="Current score of the player")
        self.score_patch_args.add_argument("acc", type=float, help="Accuracy of the questions")
        self.score_patch_args.add_argument("id", type=float, help="Player ID - Required")

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

    @staticmethod
    def read_json(json_file_path: str) -> dict:
        """
        Method to read a json file
            :param path json_file_path: Path to find the json file.
            :returns : Returns a Dictionary with the information from the file
            :rtype : Returns a Dictionary
            :raises anyError: if something goes wrong
        """

        with open(json_file_path, 'r') as json_datei:
            file = json.load(json_datei)
            return file

    @staticmethod
    def create_flag_list() -> list:
        """
        Method to create a list with 20 items of random flag file names
        :return: a list of the chosen countries
        """
        flag_file_names = CommunicationAPI.read_json(os.path.join(current_dir, '..', 'resources', 'flag_name.json'))
        final_countries = []
        for i in range(0, 20):
            random_country = random.choice(flag_file_names)
            final_countries.append(random_country)
        if CommunicationAPI.detect_duplicates(final_countries):
            CommunicationAPI.create_flag_list()
        return final_countries

    def get(self):
        return {"final_flags": final_flags}

    def patch(self):
        args = self.score_patch_args.parse_args()
        player = None

        if args["id"]:
            player = Datastorage.query.filter_by(player_id=args["id"]).first()
        if player is not None:
            if args["score"]:
                player.player_score = args["score"]
            if args["acc"]:
                player.player_acc = args["acc"]

            db.session.commit()

            sec_player_id = player.matched_player

            if sec_player_id:
                sec_player = Datastorage.query.filter_by(player_id=sec_player_id).first()
                if sec_player:
                    return {"score": sec_player.player_score, "acc": sec_player.player_acc,
                            "game_finished": sec_player.game_finished}, 200

    def post(self):
        args_pars = reqparse.RequestParser()
        args_pars.add_argument("game_finished", type=bool, help="Bool which indicates state of game")
        args_pars.add_argument("player_id", type=int, help="Player ID to identify player in DB")

        args = args_pars.parse_args()
        if args["player_id"]:
            player = Datastorage.query.filter_by(player_id=args["player_id"]).first()
            if player is not None:
                player.game_finished = True
                db.session.commit()
                return "State successfully set", 200
            else:
                return "Player not found in DB", 500
        else:
            return "Content not able to indentify", 400


class UpdateAPI(Resource):
    def __init__(self):
        self.game_version = 0.2

    def get(self):
        return {"gversion": self.game_version}


class BackupFunctionAPI(Resource):
    def __init__(self):
        pass

    def get(self):
        path = fr'backups\{request.remote_addr}'
        par_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        directory_path = os.path.join(par_dir, path)

        if os.path.exists(directory_path):
            stream = BytesIO()
            with ZipFile(stream, 'w') as zf:
                for file in glob(os.path.join(directory_path, '*.json')):
                    zf.write(file, os.path.basename(file))
            stream.seek(0)
            print("sent")
            return send_file(
                stream,
                as_attachment=True,
                download_name='downloaded_files.zip'
            )

    def post(self):
        pass


@app.route('/ping')
def ping_server():
    return {"server_online": True}, 200


api.add_resource(Matchmaking, "/matchmaking")
api.add_resource(CommunicationAPI, "/communicationAPI")
api.add_resource(UpdateAPI, "/update")
api.add_resource(BackupFunctionAPI, "/backup")

if __name__ == "__main__":
    app.run(debug=True)
