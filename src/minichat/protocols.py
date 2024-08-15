from typing import TypeVar
from typing import Protocol
from typing import Any
from typing import Iterable
from typing import Callable

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

from sqlalchemy.engine import Engine


class SupportMinichat(Protocol):
    def add_line(
        self,
        db_engine: Engine,
        user_id: int,
        t_id: int,
        role: str,
        content: str,
    ): ...

    def get_lines(
        self, db_engine: Engine, user_id: int, t_id: int, orderred: bool = True
    ) -> Any: ...

    def del_line(self, db_engine: Engine, id: int, t_id: int): ...

    def update_line(self, db_engine: Engine, target_by, target, **kwargs): ...

    def get_max_tid(self, db_engine, user_id: int) -> int: ...

    def new_tid(self, db_engine, user_id: int) -> int: ...

    def fetch_messages(
        self,
        user_id: int,
        t_id: int | None = None,
        # role: Literal["user"] | Literal["assistant"] = "user",
        # content: str = "",
    ): ...

    def make_chat(
        self,
        history_msgs: Any,
        user_id: int,
        t_id: int,
        role: str,
        content: str,
    ) -> Any: ...

    def make_chat_json(
        self,
        history_msgs: Any,
        user_id: int,
        t_id: int,
        role: str,
        content: str,
    ) -> Any: ...


MC_T = TypeVar("MC_T", bound=SupportMinichat)


class SupportMinichatDB(Protocol):
    def add_line(
        self,
        db_engine: Engine,
        user_id: int,
        t_id: int,
        role: str,
        content: str,
    ): ...

    def get_lines(
        self, db_engine: Engine, user_id: int, t_id: int, orderred: bool = True
    ) -> Any: ...

    def del_line(self, db_engine: Engine, id: int, t_id: int): ...

    def update_line(self, db_engine: Engine, target_by, target, **kwargs): ...

    def get_max_tid(self, db_engine, user_id: int) -> int: ...

    def new_tid(self, db_engine, user_id: int) -> int: ...

    def fetch_messages(
        self,
        user_id: int,
        t_id: int | None = None,
        # role: Literal["user"] | Literal["assistant"] = "user",
        # content: str = "",
    ): ...


MCDB_T = TypeVar("MCDB_T", bound=SupportMinichatDB)


class SupportChat(Protocol):
    def make_chat(
        self,
        history_msgs: Any,
        user_id: int,
        t_id: int,
        role: str,
        content: str,
    ) -> Any: ...

    def make_chat_json(
        self,
        history_msgs: Any,
        user_id: int,
        t_id: int,
        role: str,
        content: str,
    ) -> Any: ...


C_T = TypeVar("C_T", bound=SupportChat)


class ClientBaseDB:
    def __init__(self, cfig: Config, engine: Engine):
        self.cfig = cfig
        self.engine = engine

    def add_line(self, user_id: int, t_id: int, role: str, content: str):
        with Session(self.engine) as session:
            chat_line = ChatLine(
                role=role, content=content, t_id=t_id, user_id=user_id
            )
            session.add(chat_line)
            session.commit()

    def get_lines(self, user_id: int, t_id: int, orderred: bool = True):
        session = Session(self.engine)
        if orderred:
            stmt = (
                select(ChatLine)
                .where(and_(ChatLine.t_id == t_id, ChatLine.user_id == user_id))
                .order_by(ChatLine.id)
            )
        else:
            stmt = select(ChatLine).where(ChatLine.t_id == t_id)
        scalars = session.scalars(stmt)
        return scalars, session

    def del_line(self, id: int, t_id: int):
        with Session(self.engine) as session:
            stmt = delete(ChatLine).where(
                and_(ChatLine.id == id, ChatLine.t_id == t_id)
            )
            session.execute(stmt)
            session.commit()

    def update_line(self, target_by, target, **kwargs):
        if target_by not in (ChatLine.id,):
            raise TypeError("'where' must be attribute of ChatLine")
        else:
            with Session(self.engine) as session:
                stmt = (
                    update(ChatLine).where(target_by == target).values(**kwargs)
                )
                session.execute(stmt)
                session.commit()

    def get_max_tid(self, user_id: int) -> int:
        """return the max t_id of a user"""
        with Session(self.engine) as session:
            stmt = (
                select(ChatLine)
                .where(ChatLine.user_id == user_id)
                .order_by(ChatLine.t_id.desc())
            )
            scalars = session.scalars(stmt)
            first = scalars.first()
            if first is not None:
                if first.t_id is not None:
                    return first.t_id
                else:
                    raise ValueError("t_id is None")
            else:
                # 0 stand for thers is no t_id for this user
                return 0
                # raise ValueError("first line is None")

    def new_tid(self, user_id: int) -> int:
        try:
            max_id = self.get_max_tid(user_id)
            return max_id + 1
        except ValueError as e:
            raise (e)
        except Exception as e:
            raise (e)

    def fetch_messages(
        self,
        user_id: int,
        t_id: int | None = None,
    ):
        if t_id == None:
            t_id = 1
        # logger.debug(f"Current t_id: {t_id}")
        logger.opt(colors=True).debug(
            mwrapper(f"Current t_id:{mwrapper(t_id, 'red')}", "green")
        )
        # add_line(engine, t_id, role, content)

        history, session = self.get_lines(user_id, t_id)
        messages: Any = []
        for line in history:
            messages.append({"role": line.role, "content": line.content})
        session.close()

        logger.opt(colors=True).debug(mwrapper("History messages:", "green"))
        logger.opt(colors=True).debug(mwrapper(messages, "blue"))
        return messages
