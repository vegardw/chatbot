# ./models/anthropic_claude_model.py
from .language_model import LanguageModel
from typing import List
from anthropic import Anthropic
from anthropic.types import ContentBlockDeltaEvent

class AnthropicClaudeModel(LanguageModel):
    def __init__(
            self,
            models: List[str],
            api_key: str,
            suggested_model: str = None,
            streaming: bool = True
        ) -> None:
        super().__init__(models=models, suggested_model=suggested_model, streaming=streaming)
        self.api_key = api_key
        self.client = Anthropic(api_key=self.api_key)

    def generate_chat_completion(self, message, history, system_prompt, model):
        yield from self.generate_chat_completion_int(message, history, system_prompt, model, False)

    def generate_chat_completion_streaming(self, message, history, system_prompt, model):
        yield from self.generate_chat_completion_int(message, history, system_prompt, model, True)

    def generate_chat_completion_int(self, message, history, system_prompt, model, streaming):
        if model not in self.models:
            raise ValueError("Requested model not found")

        messages = []

        if len(history) > 0:
            for m in history:
                messages.append({'role': 'user', 'content': m[0]})
                messages.append({'role': 'assistant', 'content': m[1]})
        
        messages.append({'role': 'user', 'content': message})

        response = self.client.messages.create(
            max_tokens=4000,
            messages=messages,
            system=system_prompt,
            model=model,
            stream=streaming
        )

        if streaming:
            completion = ""
            for data in response:
                if isinstance(data, ContentBlockDeltaEvent):
                    completion += data.delta.text
                    yield completion
        else:
            yield response.content[0].text
