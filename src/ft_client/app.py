# from fasthtml import *
import json
import os
import asyncio
import html
from rich import print
from fasthtml.common import *
from dotenv import load_dotenv

load_dotenv()

import requests
import httpx
from starlette.responses import StreamingResponse, RedirectResponse
from .custom_css import custom_css
from .custom_js import custom_js



# App with custom styling to override the pico defaults
css = Style(custom_css)
js_stream_handler = Script(custom_js)
app = FastHTML(hdrs=(picolink, css, js_stream_handler))


def Dropdown_clienttype():
    return Select(
        Option("openai-gpt-4o-mini", value="openai"),
        Option("claude-3-5-sonnet-20240620", value="claude"),
        Option("coze-gpt-4o", value="coze"),
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
        style="resize: none; width: 100%; height: 450px; background-color: #f0f0f0; color: #333; font-size: 13px;",
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
            Button(
                "Insert",
                id="insert_slot_button",
                style="margin-top: 10px; background-color: #4CAF50; color: white;",
            ),
            cls="modal-content",
        ),
        id="slot_modal",
        cls="modal",
    )


def Help_content():
    return Div(
        H1(
            "Minichat",
            Img(
                src="/public/minichatlogo.png",
                alt="Minichat Logo",
                style="height: 1em; vertical-align: middle; margin-bottom: 6px; margin-left: 0;",
            ),
        ),
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
        P(
            "5. Use the 'Slot' button to input variable content that can be inserted into your message using {{slot}} syntax."
        ),
        A("Back to Chat", href="/", cls="button"),
        cls="container",
    )


def Login_dropdown():
    return Div(
        Div(
            "Login",
            cls="dropbtn",
        ),
        Div(
            A("GitHub", href="/login/github", cls="login-option github"),
            A("Google", href="/login/google", cls="login-option google"),
            cls="dropdown-content",
        ),
        cls="dropdown",
        style="position: absolute; top: 10px; right: 10px;"
    )


@app.get("/")
def home():
    return Title("Minichat"), Main(
        Div(
            Login_dropdown(),  # Add login dropdown to the top-right corner
            H1(
                "Minichat",
                Img(
                    src="/public/minichatlogo.png",
                    alt="Minichat Logo",
                    style="height: 1em; vertical-align: middle; margin-bottom: 6px; margin-left: 0;",
                ),
            ),
            P(
                "Welcome to minichat! Talk to the AI with minimum effort.",
                id="chat",
            ),
            Hr(),
            cls="container",
            style="position: relative;"  # Add this to make absolute positioning work
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
            A(
                "?",
                href="/help",
                cls="button help-button",
                style="position: fixed; bottom: 12px; right: 12px; background-color: #4a9eff; color: white; border: none; border-radius: 50%; width: 32px; height: 32px; display: flex; align-items: center; justify-content: center; font-size: 16px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); transition: all 0.3s ease; text-decoration: none;"
            ),
            cls="container",
        ),
    )


@app.get("/help")
def help_page():
    return Title("Minichat Help"), Main(Help_content())


@app.post("/chat")
async def chat(req):
    form_data = await req.form()
    re_post = {
        "t_id": (int(form_data.get("t_id")) if form_data.get("t_id") else None),
        "user_id": int(form_data.get("dropdown_username") or 0),
        # "role": form_data.get("dropdown_role") or "",
        "client_type": (
            form_data.get("dropdown_clienttype")
            if form_data.get("dropdown_clienttype")
            else None
        ),
        "content": html.escape(form_data.get("chat_input")) or "",
        "response_format": form_data.get("response_format") or "json",
    }
    url = os.getenv("BACKEND_URL")
    print(re_post)

    def proxy_generator(url, data):
        # async with httpx.AsyncClient() as client:
        #     async with client.stream("POST", url, json=data) as response:
        #         async for line in response.aiter_lines():
        #             if line:
        #                 # 假设响应是UTF-8编码的
        #                 yield line.encode("utf-8") + b"\n"
        with requests.post(url, json=data, stream=True) as response:
            for line in response.iter_lines():
                if line:
                    # Assuming the response is UTF-8 encoded
                    yield line.decode('utf-8').encode('utf-8') + b'\n'
                    
    # It has some bug when called from frontend, so use the sync version for now
    # async def proxy_generator_async(url, data):
    #     async with httpx.AsyncClient() as client:
    #         async with client.stream("POST", url, json=data) as response:
    #             async for line in response.aiter_lines():
    #                 if line:
    #                     # 假设响应是UTF-8编码的
    #                     yield line.encode("utf-8") + b"\n"


    return StreamingResponse(proxy_generator(url, re_post), media_type="text/plain")


@app.get("/public/{fname:path}.{ext:static}")
async def get(fname: str, ext: str):
    return FileResponse(f"public/{fname}.{ext}")


# @app.get("/login/{provider}")
# async def login(provider: str):
#     # This is a placeholder. You'll need to implement actual OAuth flow.
#     if provider == "github":
#         github_provider = GithubProvider()
#         return RedirectResponse(url=github_provider.get_authorization_url())
#     elif provider == "google":
#         google_provider = GoogleProvider()
#         return RedirectResponse(url=google_provider.get_authorization_url())
#     else:
#         return {"error": "Invalid provider"}