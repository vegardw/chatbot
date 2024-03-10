import os
import uuid
from typing import List
from session import Session

class SessionManager:
    def __init__(self, sessions_dir: str):
        self.sessions_dir = sessions_dir
        os.makedirs(self.sessions_dir, exist_ok=True)
        self.sessions = self.load_sessions()

    def load_sessions(self) -> List[Session]:
        sessions = []
        for session_file in os.listdir(self.sessions_dir):
            if session_file.endswith(".json"):
                session_path = os.path.join(self.sessions_dir, session_file)
                session = Session.load(session_path)
                sessions.append(session)
        return sessions

    def save_session(self, session: Session):
        session.save(self.sessions_dir)

    def get_session(self, session_id: str) -> Session:
        for session in self.sessions:
            if str(session.id) == session_id:
                return session
        return None

    def create_session(self, name: str = None) -> Session:
        session_id = str(uuid.uuid4())
        session = Session(id=session_id, name=name)
        self.sessions.append(session)
        self.save_session(session)
        return session

    def update_session(self, session: Session):
        self.save_session(session)

    def delete_session(self, session_id: str):
        session = self.get_session(session_id)
        if session:
            self.sessions.remove(session)
            session_file = os.path.join(self.sessions_dir, f"{session_id}.json")
            os.remove(session_file)

    def get_all_sessions(self) -> List[Session]:
        return self.sessions