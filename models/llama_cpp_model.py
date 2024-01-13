from .language_model import LanguageModel
from typing import List
from huggingface_hub import hf_hub_download
import os, errno
from llama_cpp import Llama

class LlamaCppModel(LanguageModel):
    def __init__(
            self,
            models: List[str],
            local_path: str,
            hf_repo: str = None,
            suggested_model: str = None,
            chat_format: str = 'llama-2',
            n_gpu_layers: int = 0,
            n_context: int = 512
        ) -> None:
        super().__init__(models=models, suggested_model=suggested_model)
        self.local_path = local_path
        self.hf_repo = hf_repo
        self.chat_format = chat_format
        self.n_gpu_layers = n_gpu_layers
        self.n_context = n_context
        self.model_objects = {}


    def generate_chat_completion_streaming(self, message, history, system_prompt, model):
        if model not in self.models:
            raise ValueError("Requested model not found")
        filename = model + ".gguf"

        if not os.path.isdir(self.local_path):
            os.mkdir(self.local_path)

        if self.hf_repo:
            hf_hub_download(repo_id=self.hf_repo, filename=filename, local_dir=self.local_path)

        filename = os.path.join(self.local_path, filename)

        if not os.path.exists(filename):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
        
        if not model in self.model_objects:
            self.model_objects[model] = Llama(
                model_path=filename,
                chat_format=self.chat_format,
                n_gpu_layers=self.n_gpu_layers,
                n_context = self.n_context,
                verbose=False
            )
        model = self.model_objects[model]

        messages = [{'role': 'system', 'content': system_prompt}]

        if len(history) > 0:
            for m in history:
                messages.append({'role': 'user', 'content': m[0]})
                messages.append({'role': 'assistant', 'content': m[1]})
        
        messages.append({'role': 'user', 'content': message})

        completion = ""

        for chunk in model.create_chat_completion(messages=messages, stream=True):
            if 'content' in chunk["choices"][0]['delta']:
                completion = completion + chunk["choices"][0]['delta']['content']
                yield completion    
