import json
from typing import Any

class Config:
    def __init__(self, file: str = "config.json") -> None:
        with open(file) as f:
            self.config = json.loads(f.read())
    
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
    