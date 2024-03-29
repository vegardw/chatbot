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

        models.append(HfTransformersModel(**arguments))
        model_names.extend(arguments["models"])
    elif m["type"] == "AnthropicClaude":
        arguments = m["args"]
        arguments["api_key"] = conf["anthropic_api_key"]

        models.append(AnthropicClaudeModel(**arguments))
        model_names.extend(arguments["models"])

model_names = sorted(set(model_names))

def load_session(session_id):
    chat_messages = []
    history = chat_history.load_history(session_id)

    if history:
        previous_role = None
        for entry in history:
            role = entry['role']
            content = entry['content']

            if role == 'user':
                if previous_role == 'user':
                    chat_messages[-1].append(None)
                chat_messages.append([content])
            elif role == 'assistant':
                if previous_role == 'assistant':
                    chat_messages.append([None])
                chat_messages[-1].append(content)

            previous_role = role

            # Handle the case where the last message is from the user
        if previous_role == 'user':
            chat_messages[-1].append(None)
    else:
        session_id = chat_history.session_manager.create_session("New session").id
        
    return session_id, chat_messages

def generate_chat_completion(message, history, system_prompt, model, session_id):
    system_prompt = system_prompt.replace("{{date}}", datetime.now().strftime("%B %-d, %Y"))
    history.append
    for m in models:
        if model in m.models:
            if m.streaming:
                response = ""
                for r in m.generate_chat_completion_streaming(message, history, system_prompt, model):
                    response = r
                    yield response
                chat_history.add_to_history(session_id, message, response)  # Save chat history
            else:
                response = next(m.generate_chat_completion(message, history, system_prompt, model))
                chat_history.add_to_history(session_id, message, response)  # Save chat history
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

def toggle_sidebar(state):
    state = not state
    return gr.update(visible = state), state

def clear_textbox(message):
    return "", message

def create_session_if_none(session_id):
    if session_id == None or chat_history.session_manager.get_session(session_id) == None:
        session_id = chat_history.session_manager.create_session("New session").id
    return session_id

def submit_message(message, history, system_prompt, model, session_id):
    out = history + [[message, ""]]
    msg.value = ""
    for res in generate_chat_completion(message, history, system_prompt, model, session_id):
        out[-1][1] = res
        yield out

def load_session_list():
    html = "<ul>\n"
    sessions = chat_history.session_manager.sessions
    for s in sessions:
        html += f"<li class=\"chatsession\" data-session-id=\"{s.id}\">{s.name}</li>\n"
    html += "</ul>"
    return html

load_session_list_js = """
() => {
    setTimeout(() => {
        sessionElements = document.querySelectorAll(".chatsession");

        sessionElements.forEach((s) => {
            new_s = s.cloneNode(true);
            s.parentNode.replaceChild(new_s, s);
            s = new_s;
            s.addEventListener("click", (e) => {
                selected_id = e.target.dataset.sessionId;
                id_to_load = document.getElementById("session_id").querySelector("textarea");
                id_to_load.value = selected_id
                evt = new Event("input");
                Object.defineProperty(evt, "target", {value: id_to_load});
                id_to_load.dispatchEvent(evt);
                s_btn = document.getElementById("s_btn");
                s_btn.click();
            });
        });
    }, 500);
}
"""

with gr.Blocks(fill_height=True) as chatbot:
    session_id = gr.Textbox(value=None, visible=False, elem_id="session_id")
    s_btn = gr.Button(visible=False, elem_id="s_btn")
    with gr.Row():
        with gr.Column(visible=False, scale=1, min_width=150) as sidebar_left:
            session_list = gr.HTML(elem_id="session_list")
        with gr.Column(scale=9) as main:
            with gr.Row():
                with gr.Column(scale=6):
                    nav_bar = gr.Markdown("NavBar")
                sidebar_state = gr.State(False)

                btn_toggle_sidebar = gr.Button("Toggle Sidebar", size="sm", scale=1)
                btn_toggle_sidebar.click(toggle_sidebar, [sidebar_state], [sidebar_left, sidebar_state])
            with gr.Row():
                with gr.Column(scale=5):
                    with gr.Row():
                        model = gr.Dropdown(model_names, value=conf.default_model, show_label=False)
                        system_prompt = gr.Dropdown(conf.system_prompts, value=conf.system_prompts[0], allow_custom_value=True, show_label=False)
                add_prompt_button = gr.Button("Add System Prompt", size="sm", scale=1)
        
            system_prompt.input(update_system_prompt, inputs=system_prompt, outputs=system_prompt)
            add_prompt_button.click(add_system_prompt, outputs=system_prompt)

            with gr.Group():
                bot = gr.Chatbot(elem_id="conversation")
                msg = gr.Textbox(show_label=False,)
            msg_buf = gr.State()

            msg.submit(
                clear_textbox, 
                inputs=msg, 
                outputs=[msg, msg_buf],
                queue=False
            ).then(
                create_session_if_none,
                inputs=session_id,
                outputs=session_id
            ).then(
                submit_message, 
                inputs=[msg_buf,bot,system_prompt,model, session_id], 
                outputs=bot
            )

            

    s_btn.click(load_session, inputs=session_id, outputs=[session_id, bot])
    chatbot.load(load_session_list, outputs=session_list).then(fn=lambda: None, js=load_session_list_js)

chatbot.queue()
chatbot.launch(server_name="0.0.0.0")
