#!/usr/bin/env python
import gradio as gr

from config import Config
from models import LlamaCppModel, HfTransformersModel


conf = Config()
models = []
model_names = []

for m in conf.models:
    if m["type"] == "LlamaCpp":
        arguments = m["args"]
        if not "local_path" in arguments:
            arguments["local_path"] = conf.model_path

        models.append(LlamaCppModel(**arguments))
        model_names.extend(arguments["models"])
    elif m["type"] == "HfTransformers":
        arguments = m["args"]
        #if not "local_path" in arguments:
        #    arguments["local_path"] = conf.model_path

        models.append(HfTransformersModel(**arguments))
        model_names.extend(arguments["models"])

model_names = set(model_names)

def generate_chat_completion(message, history, system_prompt, model):
    for m in models:
        if model in m.models:
            if m.streaming == True:
                yield from m.generate_chat_completion_streaming (message, history, system_prompt, model)
                break
            else:
                yield from m.generate_chat_completion (message, history, system_prompt, model)

with gr.Blocks() as chatbot:
    with gr.Row():
        system_prompt = gr.Textbox("You are a helpful assistant", label="System Prompt")
        model = gr.Dropdown(model_names, value=conf.default_model, label="Model")
    gr.ChatInterface(generate_chat_completion, additional_inputs=[system_prompt, model])

chatbot.launch(server_name="0.0.0.0")