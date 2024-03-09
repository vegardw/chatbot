import json
import os

class ChatHistory:
    def __init__(self, file: str = "chat_history.json") -> None:
        self.file = file
        self.create_history_file()

    def create_history_file(self):
        if not os.path.exists(self.file):
            with open(self.file, "w") as f:
                json.dump([], f)

    def load_history(self):
        self.create_history_file()
        with open(self.file, "r") as f:
            return json.load(f)

    def save_history(self, history):
        self.create_history_file()
        with open(self.file, "w") as f:
            json.dump(history, f, indent=2)

    def add_to_history(self, user_message, assistant_response):
        history = self.load_history()
        history.append({"user": user_message, "assistant": assistant_response})
        self.save_history(history)