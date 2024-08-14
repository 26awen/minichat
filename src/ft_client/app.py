# from fasthtml import *
import json
import asyncio
from rich import print
from fasthtml.common import *

# import requests
import httpx
from starlette.responses import StreamingResponse

# App with custom styling to override the pico defaults
css = Style(
    ":root { --pico-font-size: 100%; --pico-font-family: Pacifico, cursive;}"
)
js_stream_handler = Script(
    """
    document.addEventListener('DOMContentLoaded', function() {
        const chatButton = document.getElementById('chat_button');
        const chatOutput = document.getElementById('chat_output');
        const chatInput = document.getElementById('chat_input');

        function handleChatSubmit(event) {
            event.preventDefault();
            
            const formData = new FormData();
            formData.append('dropdown_username', document.getElementById('dropdown_username').value);
            formData.append('dropdown_role', document.getElementById('dropdown_role').value);
            formData.append('dropdown_clienttype', document.getElementById('dropdown_clienttype').value);
            formData.append('chat_input', chatInput.value);

            // Add a separator before the new response
            const separator = '\\n' + '-'.repeat(30) + '\\n';
            chatOutput.value += separator + 'You: ' + chatInput.value + '\\n\\nAI: ';
            chatOutput.scrollTop = chatOutput.scrollHeight;

            fetch('/chat', {
                method: 'POST',
                body: formData
            })
            .then(response => {
                const reader = response.body.getReader();
                const decoder = new TextDecoder();

                function readStream() {
                    reader.read().then(({ done, value }) => {
                        if (done) {
                            chatOutput.value += '\\n'; // Add a newline at the end of the response
                            chatOutput.scrollTop = chatOutput.scrollHeight;
                            return;
                        }
                        const chunk = decoder.decode(value);
                        chatOutput.value += chunk;
                        chatOutput.scrollTop = chatOutput.scrollHeight;
                        readStream();
                    });
                }

                readStream();
            })
            .catch(error => {
                console.error('Error:', error);
                chatOutput.value += 'Error occurred while fetching response.\\n';
                chatOutput.scrollTop = chatOutput.scrollHeight;
            });

            // Clear the input after sending
            chatInput.value = '';
        }

        chatButton.addEventListener('click', handleChatSubmit);

        // Move this to the end of the DOMContentLoaded event listener
        if (chatInput) {
            chatInput.addEventListener('keydown', function(event) {
                console.log("Keydown event triggered");
                if ((event.ctrlKey || event.metaKey) && event.key === 'Enter') {
                    console.log("Shortcut triggered");
                    event.preventDefault();
                    handleChatSubmit(event);
                }
            });
        } else {
            console.error("Chat input element not found");
        }
    });
    """
)
app = FastHTML(hdrs=(picolink, css, js_stream_handler))

# count = 0


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
        id="chat_input", placeholder="Enter your message", rows=12, cols=50
    )


def Chat_output():
    return Textarea(
        id="chat_output", placeholder="Output", rows=12, cols=50, readonly=True
    )


@app.get("/")
def home():
    return Title("Minichat🦜"), Main(
        Div(
            H1("Minichat🦜"),
            P(
                "Welcome to minichat! Talk to the AI with minimun effort.",
                id="chat",
            ),
            Hr(),
            cls="container",
        ),
        Div(
            Div(
                Dropdown_clienttype(),
                Dropdown_username(),
                Dropdown_role(),
                # Dropdown_tid(),
                cls="grid grid-cols-3",
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
                # hx_post="/chat",
                # hx_target="#chat_output",
                # hx_swap="innerHTML",
                # hx_include="#dropdown_tid, #dropdown_username, #dropdown_role, #dropdown_model, #chat_input",
            ),
            cls="container",
        ),
    )


@app.post("/chat")
async def chat(req):
    form_data = await req.form()
    re_post = {
        "t_id": (
            int(form_data.get("dropdown_tid"))
            if form_data.get("dropdown_tid")
            else None
        ),
        "user_id": int(form_data.get("dropdown_username") or 0),
        "role": form_data.get("dropdown_role") or "",
        "client_type": (
            form_data.get("dropdown_clienttype")
            if form_data.get("dropdown_clienttype")
            else None
        ),
        "content": form_data.get("chat_input") or "你好",
    }
    url = "http://100.99.103.12:5010/chat"
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
