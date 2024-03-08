from abc import ABC, abstractmethod
from typing import List

class LanguageModel(ABC):
    def __init__(self, models: List[str], suggested_model: str = None, streaming: bool = True) -> None:
        if len(models) > 0:
            self.models = models
        else:
            raise ValueError("Models list must contain at least one model")
        if not suggested_model:
            self.suggested_model = models[0]
        elif suggested_model in models:
            self.suggested_model = suggested_model
        else:
            raise ValueError("If supplied, suggested model must be in the models list")
        self.streaming = streaming
        

    @abstractmethod
    def generate_chat_completion(self, message, history, system_prompt, model):
        pass

    @abstractmethod
    def generate_chat_completion_streaming(self, message, history, system_prompt, model):
        pass