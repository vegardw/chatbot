import json
import argparse
from datetime import datetime
from session import Session
from session_manager import SessionManager
from history import ChatHistory

def convert_history_to_sessions(old_history_file: str, sessions_dir: str):
    chat_history = ChatHistory(sessions_dir)

    with open(old_history_file, "r") as f:
        old_history = json.load(f)

    session_id = chat_history.create_session(name="Converted Session")
    session = chat_history.session_manager.get_session(session_id)

    for entry in old_history:
        user_message = entry["user"]
        assistant_response = entry["assistant"]
        session.add_message("user", user_message)
        session.add_message("assistant", assistant_response)

    chat_history.session_manager.update_session(session)
    print(f"Conversion complete. New session created with ID: {session_id}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert old chat history to new session format")
    parser.add_argument("old_history_file", type=str, help="Path to the old chat history JSON file")
    parser.add_argument("sessions_dir", type=str, help="Directory to store the new session files")
    args = parser.parse_args()

    convert_history_to_sessions(args.old_history_file, args.sessions_dir)