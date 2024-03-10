import os
import json
from datetime import datetime

class Session:
    def __init__(self, id: str, name: str = None, history: list = None, last_activity: datetime = None):
        self.id = id
        self.name = name or f"Session {id}"
        self.history = history or []
        self.last_activity = last_activity or datetime.now()

    def save(self, sessions_dir: str):
        session_file = os.path.join(sessions_dir, f"{self.id}.json")
        session_data = {
            "id": self.id,
            "name": self.name,
            "history": self.history,
            "last_activity": self.last_activity.isoformat()
        }
        with open(session_file, "w") as f:
            json.dump(session_data, f, indent=2)

    @classmethod
    def load(cls, session_file: str):
        with open(session_file, "r") as f:
            session_data = json.load(f)
        session = cls(
            id=session_data["id"],
            name=session_data["name"],
            history=session_data["history"],
            last_activity=datetime.fromisoformat(session_data["last_activity"])
        )
        return session

    def add_message(self, role: str, content: str):
        self.history.append({"role": role, "content": content})
        self.last_activity = datetime.now()

    def clear_history(self):
        self.history = []
        self.last_activity = datetime.now()