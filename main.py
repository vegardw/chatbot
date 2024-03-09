#!/usr/bin/env python
import gradio as gr
from datetime import datetime

from config import Config
from models import LlamaCppModel, HfTransformersModel, AnthropicClaudeModel
from history import ChatHistory

chat_history = ChatHistory()
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
    elif m["type"] == "AnthropicClaude":
        arguments = m["args"]
        arguments["api_key"] = conf["anthropic_api_key"]

        models.append(AnthropicClaudeModel(**arguments))
        model_names.extend(arguments["models"])

model_names = sorted(set(model_names))

def load_initial_history():
    history = chat_history.load_history()
    chat_messages = []
    for entry in history:
        chat_messages.append((entry["user"], entry["assistant"]))
    return chat_messages

def generate_chat_completion(message, history, system_prompt, model):
    system_prompt = system_prompt.replace("{{date}}", datetime.now().strftime("%B %-d, %Y"))
    for m in models:
        if model in m.models:
            if m.streaming:
                response = ""
                for r in m.generate_chat_completion_streaming(message, history, system_prompt, model):
                    response = r
                    yield response
                chat_history.add_to_history(message, response)  # Save chat history
            else:
                response = next(m.generate_chat_completion(message, history, system_prompt, model))
                chat_history.add_to_history(message, response)  # Save chat history
                yield response
            break


def update_system_prompt(prompt):
    if prompt not in conf.system_prompts:
        conf.system_prompts[conf.system_prompts.index(system_prompt.value)] = prompt
        conf.save()
    system_prompt.value = prompt
    return gr.Dropdown(choices=conf.system_prompts, value=prompt)

def add_system_prompt():
    new_prompt = "New Prompt."
    conf.system_prompts.append(new_prompt)
    conf.save()
    system_prompt.value = new_prompt
    return gr.Dropdown(choices=conf.system_prompts, value=new_prompt)

with gr.Blocks(fill_height=True) as chatbot:
    with gr.Row():
        model = gr.Dropdown(model_names, value=conf.default_model, label="Model")
        system_prompt = gr.Dropdown(conf.system_prompts, value=conf.system_prompts[0], allow_custom_value=True, label="System Prompt")
        add_prompt_button = gr.Button("Add System Prompt")
        
    system_prompt.input(update_system_prompt, inputs=system_prompt, outputs=system_prompt)
    add_prompt_button.click(add_system_prompt, outputs=system_prompt)

    bot = gr.Chatbot(render=False)
               
    gr.ChatInterface(
        generate_chat_completion,
        chatbot=bot,
        additional_inputs=[system_prompt, model],
        fill_height=True
    )

    chatbot.load(load_initial_history, outputs=bot)

chatbot.launch(server_name="0.0.0.0")
