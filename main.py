#!/usr/bin/env python
import gradio as gr

from config import Config
from models import LlamaCppModel, HfTransformersModel, AnthropicClaudeModel


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

def generate_chat_completion(message, history, system_prompt, model):
    for m in models:
        if model in m.models:
            if m.streaming == True:
                yield from m.generate_chat_completion_streaming (message, history, system_prompt, model)
                break
            else:
                yield from m.generate_chat_completion (message, history, system_prompt, model)


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

    gr.ChatInterface(generate_chat_completion, additional_inputs=[system_prompt, model], fill_height=True)

chatbot.launch(server_name="0.0.0.0")
