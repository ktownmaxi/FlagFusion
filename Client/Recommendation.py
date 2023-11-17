import random
import json
import os


class Flashcard:
    def __init__(self, value, score=50):
        self.value = value
        self.score = score  # Start-Score immer 50

    def update_score(self, wrong, timee):
        if wrong:
            self.score = min(self.score + 15, 100)
        if not wrong:
            self.score = max(self.score - 10, 0)
            if timee < 3000:
                self.score = max(self.score - 5, 0)
            else:
                self.score = min(self.score + 5, 100)


class FlashcardDeck:
    def __init__(self):
        self.cards = []

    def add_card(self, card):
        self.cards.append(card)

    def get_next_value(self):
        total_score = sum(card.score for card in self.cards)
        if total_score == 0:
            return None

        card_probabilities = [(card, card.score / total_score) for card in self.cards]
        chosen_card = random.choices(card_probabilities, weights=[prob for _, prob in card_probabilities])[0][0]

        return chosen_card

    def get_random_card(self):
        random_number = random.randint(0, len(self.cards) - 1)
        return self.cards[random_number]

    @staticmethod
    def update_card(card, wrong, time):
        card.update_score(wrong, time)

    @staticmethod
    def flashcard_encoder(obj):
        if isinstance(obj, Flashcard):
            return {
                "value": obj.value,
                "score": obj.score
            }
        if isinstance(obj, FlashcardDeck):
            return {"cards": obj.cards}
        raise TypeError(f"Object of type {obj.__class__.__name__} is not JSON serializable")

    @staticmethod
    def flashcard_decoder(json_dict):
        if "cards" in json_dict:
            deck = FlashcardDeck()
            for card_data in json_dict["cards"]:
                value = card_data["value"]
                score = card_data["score"]
                card = Flashcard(value, score)
                deck.add_card(card)
            return deck
        return json_dict

    def write_to_json(self, obj, filename):
        file_path = os.path.join("saves", filename)
        with open(file_path, "w") as json_file:
            json.dump(obj, json_file, default=self.flashcard_encoder, indent=4)

    def read_from_json(self, filename):
        file_path = os.path.join("saves", filename)
        with open(file_path, "r") as json_file:
            loaded_data = json.load(json_file, object_hook=self.flashcard_decoder)
            return loaded_data

    @staticmethod
    def get_json_names():
        directory = 'saves'
        json_files = [file for file in os.listdir(directory) if file.endswith('.json')]
        filenames_without_extension = []

        for i in json_files:
            filenames_without_extension.append(i.replace(".json", ""))
        return filenames_without_extension
