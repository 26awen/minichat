# from fasthtml import *
import json
import os
import asyncio
import html
from rich import print
from fasthtml.common import *
from dotenv import load_dotenv
load_dotenv()

# import requests
import httpx
from starlette.responses import StreamingResponse
from .custom_css import custom_css
from .custom_js import custom_js

# App with custom styling to override the pico defaults
css = Style(custom_css)
js_stream_handler = Script(custom_js)
app = FastHTML(hdrs=(picolink, css, js_stream_handler))


def Dropdown_clienttype():
    return Select(
        Option("claude", value="claude"),
        Option("openai", value="openai"),
        Option("coze", value="coze"),
        id="dropdown_clienttype",
    )


def Dropdown_username():
    return Select(
        Option("Uear1", value="1"),
        id="dropdown_username",
    )


def Dropdown_tid():
    return Select(
        Option("new_chat", value=""),
        id="dropdown_tid",
    )


def Dropdown_role():
    return Select(
        Option("user", value="user"),
        Option("assistant", value="assistant"),
        id="dropdown_role",
    )


def Chat_input():
    return Textarea(
        id="chat_input",
        placeholder="Enter your message",
        rows=12,
        cols=50,
        style="resize: none; width: 100%; height: 450px;",
    )


def Chat_output():
    return Textarea(
        id="chat_output",
        placeholder="Output",
        rows=12,
        cols=50,
        readonly=True,
        style="resize: none; width: 100%; height: 450px;",
    )


def Variable_textarea():
    return Div(
        Div(
            Span("×", cls="close", id="close_modal"),
            H3("Slot Input"),
            Textarea(
                id="slot_textarea",
                placeholder="Enter slot content",
                rows=5,
                cols=50,
                style="resize: none; width: 100%;",
            ),
            cls="modal-content",
        ),
        id="slot_modal",
        cls="modal",
    )


def Help_content():
    return Div(
        H1("Minichat🦜 Help"),
        H2("Keyboard Shortcuts"),
        Ul(
            Li("Ctrl + Enter (or Cmd + Enter on Mac): Send message"),
            Li("Alt + Enter: Continue chat"),
        ),
        H2("How to Use"),
        P("1. Select the client type and username from the dropdowns."),
        P("2. Type your message in the input box."),
        P("3. Use the 'Chat' button or Ctrl+Enter to send your message."),
        P("4. To continue the conversation, use the 'Continue' button or Alt+Enter."),
        P("5. Use the 'Slot' button to input variable content that can be inserted into your message using {{slot}} syntax."),
        A("Back to Chat", href="/", cls="button"),
        cls="container",
    )


@app.get("/")
def home():
    return Title("Minichat🦜"), Main(
        Div(
            H1("Minichat🦜"),
            P(
                "Welcome to minichat! Talk to the AI with minimum effort.",
                id="chat",
            ),
            Hr(),
            cls="container",
        ),
        Div(
            Div(
                Dropdown_clienttype(),
                Dropdown_username(),
                cls="grid grid-cols-2 gap-2",
            ),
            cls="container",
        ),
        Div(
            Div(
                Chat_input(),
                Chat_output(),
                cls="grid grid-cols-2",
            ),
            cls="container",
        ),
        Div(
            Button(
                "Chat",
                id="chat_button",
            ),
            Button(
                "Continue",
                id="continue_button",
                style="background-color: #FFA500; color: white;",
                disabled=True,  # Initially disabled
            ),
            Button(
                "Slot",
                id="slot_button",
                style="background-color: #4CAF50; color: white;",
            ),
            Variable_textarea(),
            cls="container",
        ),
        Div(
            A("Help", href="/help", cls="button", style="position: fixed; bottom: 20px; right: 20px; background-color: #f0f0f0; color: #333; border: 1px solid #ccc; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s ease;"),
            cls="container",
        ),
    )


@app.get("/help")
def help_page():
    return Title("Minichat🦜 Help"), Main(Help_content())


@app.post("/chat")
async def chat(req):
    form_data = await req.form()
    re_post = {
        "t_id": (
            int(form_data.get("t_id"))
            if form_data.get("t_id")
            else None
        ),
        "user_id": int(form_data.get("dropdown_username") or 0),
        # "role": form_data.get("dropdown_role") or "",
        "client_type": (
            form_data.get("dropdown_clienttype")
            if form_data.get("dropdown_clienttype")
            else None
        ),
        "content": html.escape(form_data.get("chat_input")) or "你好",
        "response_format": form_data.get("response_format") or "json",
    }
    url = os.getenv("BACKEND_URL")
    print(re_post)

    async def proxy_generator(url, data):
        async with httpx.AsyncClient() as client:
            async with client.stream("POST", url, json=data) as response:
                async for line in response.aiter_lines():
                    if line:
                        # 假设响应是UTF-8编码的
                        yield line.encode("utf-8") + b"\n"

    return StreamingResponse(
        proxy_generator(url, re_post), media_type="text/plain"
    )