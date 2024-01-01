#!/usr/bin/env python
import gradio as gr

from config import Config
from models import LlamaCppModel


conf = Config()
test_model_name = "stablelm-zephyr-3b.Q5_K_S"

stablelm = LlamaCppModel([test_model_name], local_path=conf.model_path, hf_repo="TheBloke/stablelm-zephyr-3b-GGUF", chat_format="zephyr")

def generate_chat_completion_streaming(message, history, system_prompt, model):
    yield from stablelm.generate_chat_completion_streaming(message, history, system_prompt, model)

with gr.Blocks() as chatbot:
    with gr.Row():
        system_prompt = gr.Textbox("You are a helpful assistant", label="System Prompt")
        models = gr.Dropdown([test_model_name], value=test_model_name, label="Model")
    gr.ChatInterface(generate_chat_completion_streaming, additional_inputs=[system_prompt, models])

chatbot.launch(server_name="0.0.0.0")