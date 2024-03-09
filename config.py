import json
from typing import Any

class Config:
    def __init__(self, file: str = "config.json") -> None:
        self.file = file
        with open(self.file) as f:
            self.config = json.loads(f.read())
        self.system_prompts = self.config.get("system_prompts", ["You are a helpful assistant."])
    
    def __getattr__(self, attr) -> Any:
        if(attr in self.config):
            return self.config[attr]
        else:
            raise AttributeError(f"'{attr}' not found in config")
    
    def __getitem__(self, key) -> Any:
        if(key in self.config):
            return self.config[key]
        else:
            raise KeyError(f"'{key}' not found in config")
        
    def save(self) -> None:
        self.config["system_prompts"] = self.system_prompts
        with open(self.file, "w") as f:
            json.dump(self.config, f, indent=2)
