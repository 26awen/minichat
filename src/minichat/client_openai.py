from typing import Any

from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session


from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import update
from sqlalchemy import and_

from openai import OpenAI

from .db_moldes import ChatLine

from .logbot import logger
from .misc import mwrapper

from .config_schema import Config

from .protocols import ClientBaseDB

class ClientOpenai(ClientBaseDB):
    def __init__(self, cfig: Config, engine: Engine):
        self.cfig = cfig
        self.engine = engine

    def make_chat(
        self, history_msgs: Any, user_id: int, t_id: int, role: str, content: str
    ):
        logger.opt(colors=True).debug(
            mwrapper(f"Chat with config:{self.cfig}", "green")
        )
        client = OpenAI(
            api_key=self.cfig.cfig_openai.openai_key,
            base_url=self.cfig.cfig_openai.openai_baseurl
            if self.cfig.cfig_openai.openai_baseurl != ""
            else None,
        )

        history_msgs.append({"role": role, "content": content})

        # logger.opt(colors=True).debug(
        #     mwrapper(f"Model name:{self.cfig.cfig_openai.model}", "green")
        # )
        logger.opt(colors=True).debug(
            mwrapper("History messages include the new request message:", "green")
        )
        logger.opt(colors=True).debug(history_msgs)

        try:
            stream = client.chat.completions.create(
                model=self.cfig.cfig_openai.model,
                messages=history_msgs,
                stream=True,
            )
        except Exception as e:
            logger.error(e)
            raise ValueError("Bad Stream")
        else:
            logger.debug("Good Stream")

        assistant_msg = ""

        # logger.opt(colors=True).info(f"Chatting with {self, self.cfig.model}:")
        try:
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    assistant_msg += chunk.choices[0].delta.content
                    yield chunk.choices[0].delta.content
        except Exception as e:
            logger.error("Error when chatting!")
            logger.error(e)
        else:
            self.add_line(user_id, t_id, role, content)
            self.add_line(user_id, t_id, "assistant", assistant_msg)
