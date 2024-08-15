from typing import Any
import json

from sqlalchemy.engine import Engine, base
from sqlalchemy.orm import Session
from sqlalchemy import select
from sqlalchemy import delete
from sqlalchemy import update
from sqlalchemy import and_

from .db_moldes import ChatLine

from .logbot import logger
from .misc import mwrapper

from .config_schema import Config

import anthropic

from .protocols import ClientBaseDB


class ClientClaude(ClientBaseDB):
    def __init__(self, cfig: Config, engine: Engine):
        self.cfig = cfig
        self.engine = engine

    def make_chat(
        self, history_msgs: Any, user_id: int, t_id: int, role: str, content: str
    ):
        logger.opt(colors=True).debug(
            mwrapper(f"Chat with config:{self.cfig}", "green")
        )

        client = anthropic.Anthropic(
            api_key=self.cfig.cfig_claude.claude_key,
            base_url=self.cfig.cfig_claude.claude_baseurl
            if self.cfig.cfig_claude.claude_baseurl != ""
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

        assistant_msg = ""
        try:
            # print("sdjfojsodjfojewkjdklwjfkljksjdfkl")
            # print(self.cfig.cfig_claude.model)
            with client.messages.stream(
                max_tokens=4096,
                messages=history_msgs,
                model=self.cfig.cfig_claude.model,
            ) as stream:
                for text in stream.text_stream:
                    assistant_msg += text
                    yield text
                    # print(text, end="", flush=True)
        except Exception as e:
            logger.error("Error when chatting!")
            logger.error(e)
        else:
            self.add_line(user_id, t_id, role, content)
            self.add_line(user_id, t_id, "assistant", assistant_msg)


    def make_chat_json(self, history_msgs: Any, user_id: int, t_id: int, role: str, content: str):
        logger.opt(colors=True).debug(
            mwrapper(f"Chat with config:{self.cfig}", "green")
        )
        client = anthropic.Anthropic(
            api_key=self.cfig.cfig_claude.claude_key,
            base_url=self.cfig.cfig_claude.claude_baseurl
            if self.cfig.cfig_claude.claude_baseurl != ""
            else None,
        )

        history_msgs.append({"role": role, "content": content})

        logger.opt(colors=True).debug(
            mwrapper("History messages include the new request message:", "green")
        )
        logger.opt(colors=True).debug(history_msgs)

        assistant_msg = ""
        try:
            with client.messages.stream(
                max_tokens=4096,
                messages=history_msgs,
                model=self.cfig.cfig_claude.model,
            ) as stream:
                for text in stream.text_stream:
                    assistant_msg += text
                    yield json.dumps({
                        "chunk": text,
                        "user_id": user_id,
                        "t_id": t_id
                    })
        except Exception as e:
            logger.error("Error when chatting!")
            logger.error(e)
            yield json.dumps({
                "error": str(e),
                "user_id": user_id,
                "t_id": t_id
            })
        else:
            self.add_line(user_id, t_id, role, content)
            self.add_line(user_id, t_id, "assistant", assistant_msg)
            yield json.dumps({
                "final": True,
                "user_id": user_id,
                "t_id": t_id
            })
