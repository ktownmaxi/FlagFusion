import json
import os
import random


class Flashcard:
    """
    Class for creating a Flashcard - usually used in combination with FlashcardDeck.
    """
    def __init__(self, value, score=50):
        """
        Constructor for Flashcard. Initializes a value of a card and a score.
        :param value: Value or name of the card.
        :param score: Score of the card. Default = 50.
        """
        self.value = value
        self.score = score

    def update_score(self, wrong: bool, time: int):
        """
        Method to update the score on the card.
        :param wrong: A boolean to decided if the answer was wrong or right.
        :param time: A int with a value for the time.
        :return:
        """
        if wrong:
            self.score = min(self.score + 15, 100)
        if not wrong:
            self.score = max(self.score - 10, 0)
            if time < 3000:
                self.score = max(self.score - 5, 0)
            else:
                self.score = min(self.score + 5, 100)


class FlashcardDeck:
    """
    Class to manage a collection of Flashcards.
    """
    def __init__(self):
        """
        Constructor of the FlashcardDeck class - Initializes a list named cards to store all cards.
        """
        self.cards = []

    def add_card(self, card):
        """
        Method to add a card to the cards list.
        :param card: Card wanted to add.
        :return:
        """
        self.cards.append(card)

    def get_next_value(self) -> Flashcard:
        """
        Method to get a card based on the score on the cards - Higher score = higher prob.
        :return: Returns the chosen card.
        """
        total_score = sum(card.score for card in self.cards)
        if total_score == 0:
            return None

        card_probabilities = [(card, card.score / total_score) for card in self.cards]
        chosen_card = random.choices(card_probabilities, weights=[prob for _, prob in card_probabilities])[0][0]

        return chosen_card

    def get_random_card(self) -> Flashcard:
        """
        Method to get a completely random card from the card deck.
        :return: Returns the randomly chosen card.
        """
        random_number = random.randint(0, len(self.cards) - 1)
        return self.cards[random_number]

    @staticmethod
    def update_card(card: Flashcard, wrong: bool, time: int):
        """
        Method to call the update_score method in the Flashcard class.
        :param card: Card we wish to update the score.
        :param wrong: Bool to decide if the answer was right or wrong.
        :param time: int which represents the needed time.
        :return:
        """
        card.update_score(wrong, time)

    @staticmethod
    def flashcard_encoder(obj):
        """
        Helper method to decode and encode the Flashcard Deck class into a json file.
        :param obj: Class instance we wish to encode.
        :return: The values to create the json file.
        """
        if isinstance(obj, Flashcard):
            return {
                "value": obj.value,
                "score": obj.score
            }
        if isinstance(obj, FlashcardDeck):
            return {"cards": obj.cards}
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    @staticmethod
    def flashcard_decoder(json_dict: dict):
        """
        Method to decode the class object into a json file.
        :param json_dict: The values to decode in dictionary format.
        :return:
        """
        if "cards" in json_dict:
            deck = FlashcardDeck()
            for card_data in json_dict["cards"]:
                value = card_data["value"]
                score = card_data["score"]
                card = Flashcard(value, score)
                deck.add_card(card)
            return deck
        return json_dict

    def write_to_json(self, obj, filename: str):
        """
        Method to write an instance of the FlashCard deck to json.
        :param obj: Class instance which should be written to json.
        :param filename: Name of the json file.
        :return:
        """
        file_path = os.path.join("saves", filename)
        with open(file_path, "w") as json_file:
            json.dump(obj, json_file, default=self.flashcard_encoder, indent=4)

    @staticmethod
    def read_from_json(file_path: str):
        """
        Method to read the json file back in.
        :param file_path: Path were the json file is.
        :return: returns the loaded data.
        """
        with open(file_path, "r") as json_file:
            loaded_data = json.load(json_file, object_hook=FlashcardDeck.flashcard_decoder)
            return loaded_data

    @staticmethod
    def get_json_names():
        """
        Method to create a path where to safe a json file to.
        :return: Path.
        """
        directory = 'saves'
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        filenames_without_extension = []

        for i in json_files:
            filenames_without_extension.append(i.replace(".json", ""))
        return filenames_without_extension
