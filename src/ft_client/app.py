# from fasthtml import *
import json
import asyncio
from rich import print
from fasthtml.common import *
# import requests
import httpx
from starlette.responses import StreamingResponse

# App with custom styling to override the pico defaults
css = Style(":root { --pico-font-size: 100%; --pico-font-family: Pacifico, cursive;}")
app = FastHTML(hdrs=(picolink, css))

# count = 0


def Dropdown_model():
    return Select(
        Option("gpt-3.5-turbo", value="gpt-3.5-turbo"),
        Option("gpt-4-o", value="gpt-4-o"),
        Option("claude-3-opus-20240229", value="claude-3-opus-20240229"),
        id="dropdown_model",
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
    return Textarea(id="chat_input", placeholder="Enter your message", rows=4, cols=50)


def Chat_output():
    return Textarea(id="chat_output", placeholder="Output", rows=4, cols=50)


@app.get("/")
def home():
    return Title("Minichat🦜"), Main(
        Div(
            H1("Minichat🦜"),
            P("Welcome to minichat! Talk to the AI with minimun effort.", id="chat"),
            Hr(),
            cls="container",
        ),
        Div(
            Div(
                Dropdown_model(),
                Dropdown_username(),
                Dropdown_role(),
                Dropdown_tid(),
                cls="grid grid-cols-4",
            ),
            cls="container",
        ),
        Div(
            Chat_input(),
            Chat_output(),
            Button(
                "Chat",
                hx_post="/chat",
                hx_target="#chat_output",
                hx_swap="innerHTML",
                hx_include="#dropdown_tid, #dropdown_username, #dropdown_role, #dropdown_model, #chat_input",
            ),
            cls="container",
        ),
    )


@app.post("/chat")
async def chat(req):
    form_data = await req.form()
    re_post = {
        "t_id": int(form_data.get("dropdown_tid") or 0),
        "user_id": int(form_data.get("dropdown_username") or 0),
        "role": form_data.get("dropdown_role") or "",
        "model": form_data.get("dropdown_model") or "",
        "content": form_data.get("chat_input") or "你好",
    }
    url = "http://100.99.103.12:5010/chat"
    print(re_post)



    async def proxy_generator(url, data):
        async with httpx.AsyncClient() as client:
            async with client.stream('POST', url, json=data) as response:
                async for line in response.aiter_lines():
                    if line:
                        # 假设响应是UTF-8编码的
                        yield line.encode('utf-8') + b'\n'

    return StreamingResponse(proxy_generator(url, re_post), media_type="text/plain")
