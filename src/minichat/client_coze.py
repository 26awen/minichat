from typing import Any
import json

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import update
from sqlalchemy import and_

# from openai import OpenAI
import requests

from .db_moldes import ChatLine

from .logbot import logger
from .misc import mwrapper

from .config_schema import Config
from .config_schema import AiRoles


from .protocols import ClientBaseDB

class ClientCoze(ClientBaseDB):
    def __init__(self, cfig: Config, engine: Engine):
        self.cfig = cfig
        self.engine = engine

    def make_chat(
        self, history_msgs: Any, user_id: int, t_id: int, role: str, content: str
    ):
        logger.opt(colors=True).debug(
            mwrapper(f"Chat with config:{self.cfig}", "green")
        )

        end_point = "https://api.coze.com/open_api/v2/chat"

        headers = {
            "Authorization" : f"Bearer {self.cfig.cfig_coze.bearer_token}",
            "Content-Type" : "application/json",
            "Connection" : "keep-alive",
            "Accept" : "*/*"
        }

        body = {
            "bot_id": self.cfig.cfig_coze.bot_id,
            "user": "user",
            "query": content,
            "stream": True,
            "chat_history": history_msgs
        }
        # print(headers)
        # print(body)


        # history_msgs.append({"role": role, "content": content})

        logger.opt(colors=True).debug(
            mwrapper(f"Model name:{self.cfig.client_type}", "green")
        )
        logger.opt(colors=True).debug(
            mwrapper("History messages include the new request message:", "green")
        )
        # logger.opt(colors=True).debug(history_msgs)

        assistant_msg = ""

        logger.opt(colors=True).info(f"Chatting with {self, self.cfig.client_type}:")
        try:
            resp = requests.post(end_point, headers=headers, json=body, stream=True)
            # print(resp.status_code)
            if resp.status_code == 200:
                for line in resp.iter_lines():
                    # print(line)
                    if line:
                        data = json.loads(line.decode("utf8")[5:])
                        if data.get("is_finish") is not None and (not data["is_finish"]):
                            assistant_msg += data["message"]["content"]
                            yield data["message"]["content"]
                            # print(data["message"]["content"], end="")
            else:
                print(resp.status_code)
        except Exception as e:
            logger.error("Error when chatting!")
            logger.error(e)
        else:
            self.add_line(user_id, t_id, role, content)
            self.add_line(user_id, t_id, "assistant", assistant_msg)
