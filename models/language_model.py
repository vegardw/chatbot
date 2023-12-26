from abc import ABC, abstractmethod

class LanguageModel(ABC):
    def __init__(self) -> None:
        pass

    @abstractmethod
    def generate_chat_completion(self):
        pass

    @abstractmethod
    def generate_chat_completion_streaming(self):
        pass