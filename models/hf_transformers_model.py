from .language_model import LanguageModel
from transformers import AutoModelForCausalLM, AutoTokenizer, TextIteratorStreamer
from typing import List, Generator
from threading import Thread

class HfTransformersModel(LanguageModel):
    def __init__(
            self, 
            models: List[str], 
            suggested_model: str = None, 
            hf_repo: str = None,
            streaming: bool = True,
            ) -> None:
        super().__init__(models=models, suggested_model=suggested_model, streaming=streaming)
        self.hf_repo = hf_repo
        self.tokenizer = AutoTokenizer.from_pretrained(self.hf_repo)
        self.model_objects = {}

    def _prepare_chat_inputs(self, message, history, system_prompt, model):
        if model not in self.models:
            raise ValueError("Requested model not found")

        if model not in self.model_objects:
            self.model_objects[model] = AutoModelForCausalLM.from_pretrained(self.hf_repo).to("cuda:0")
        model = self.model_objects[model]

        messages = []

        if len(history) > 0:
            for m in history:
                messages.append({'role': 'user', 'content': m[0]})
                messages.append({'role': 'assistant', 'content': m[1]})

        messages.append({'role': 'user', 'content': message})

        inputs = self.tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(model.device)

        return model, inputs

    def generate_chat_completion(self, message, history, system_prompt, model):
        model, inputs = self._prepare_chat_inputs(message, history, system_prompt, model)

        input_ids_cutoff = inputs.size(dim=1)

        generated_ids = model.generate(
            input_ids=inputs,
            max_new_tokens=512,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        completion = self.tokenizer.decode(
            generated_ids[0][input_ids_cutoff:],
            skip_special_tokens=True,
        )

        yield completion

    def generate_chat_completion_streaming(self, message, history, system_prompt, model) -> Generator[str, None, None]:
        model, inputs = self._prepare_chat_inputs(message, history, system_prompt, model)

        streamer = TextIteratorStreamer(self.tokenizer, skip_prompt=True)

        generation_kwargs = dict(
            input_ids=inputs,
            streamer=streamer,
            max_new_tokens=512,
            temperature=0.2,
            top_p=0.95,
            do_sample=True,
            eos_token_id=self.tokenizer.eos_token_id,
            pad_token_id=self.tokenizer.pad_token_id,
        )

        thread = Thread(target=model.generate, kwargs=generation_kwargs)
        thread.start()

        generated = ""
        for new_text in streamer:
            new_text = new_text.replace("<|endoftext|>", "")
            generated += new_text
            yield generated