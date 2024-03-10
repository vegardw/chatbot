from session_manager import SessionManager

class ChatHistory:
    def __init__(self, sessions_dir: str = "history"):
        self.session_manager = SessionManager(sessions_dir)

    def load_history(self, session_id: str):
        session = self.session_manager.get_session(session_id)
        if session:
            return session.history
        return None

    def save_history(self, session_id: str, history: list):
        session = self.session_manager.get_session(session_id)
        if session:
            session.history = history
            self.session_manager.update_session(session)

    def add_to_history(self, session_id: str, user_message: str, assistant_response: str):
        session = self.session_manager.get_session(session_id)
        if session:
            session.add_message("user", user_message)
            session.add_message("assistant", assistant_response)
            self.session_manager.update_session(session)

    def create_session(self, name: str = None) -> str:
        session = self.session_manager.create_session(name)
        return session.id

    def delete_session(self, session_id: str):
        self.session_manager.delete_session(session_id)

    def get_all_sessions(self):
        return self.session_manager.get_all_sessions()