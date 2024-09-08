from sqlalchemy import ForeignKey
from sqlalchemy import String, Integer
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy.orm import relationship

class Base(DeclarativeBase):
    pass


class ChatLine(Base):
    __tablename__ = "chat_line"
    id: Mapped[int] = mapped_column(primary_key=True)
    t_id: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String())
    
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    # user_provider_unique_id: Mapped[str] = mapped_column(ForeignKey("user.provider_unique_id"), nullable=True)
    user: Mapped["User"] = relationship(back_populates="chat_lines", foreign_keys=[user_id])
    
    

    # service_name: Mapped[str] = mapped_column(String())
    # model_name: Mapped[str] = mapped_column(String())

    def __repr__(self) -> str:
        return f"ChatLine(id={self.id!r}, role={self.role!r}, content={self.content!r})"

class ImageLine(Base):
    __tablename__ = "image_line"
    id: Mapped[int] = mapped_column(primary_key=True)
    t_id: Mapped[int] = mapped_column(Integer)
    role: Mapped[str] = mapped_column(String(30))
    content: Mapped[str] = mapped_column(String())
    filename: Mapped[str] = mapped_column(String())
    user_id: Mapped[int] = mapped_column(ForeignKey("user.id"))
    user: Mapped["User"] = relationship(back_populates="image_lines", foreign_keys=[user_id])

    # service_name: Mapped[str] = mapped_column(String())
    # model_name: Mapped[str] = mapped_column(String())

    def __repr__(self) -> str:
        return f"ImageLine(id={self.id!r}, role={self.role!r}, content={self.content!r})"

class User(Base):
    __tablename__ = "user"
    id: Mapped[int] = mapped_column(primary_key=True)

    username: Mapped[str] = mapped_column(String(30), nullable=True)
    usertype: Mapped[str] = mapped_column(String(30), nullable=True)
    chat_lines: Mapped[list["ChatLine"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    image_lines: Mapped[list["ImageLine"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    
    provider: Mapped[str] = mapped_column(String(30))
    provider_user_id: Mapped[str] = mapped_column(String(50))
    provider_unique_id: Mapped[str] = mapped_column(String(50))
    email: Mapped[str] = mapped_column(String(100))
    name: Mapped[str] = mapped_column(String(100))
    avatar_url: Mapped[str] = mapped_column(String(255), nullable=True)

    def __repr__(self) -> str:
        return f"User(id={self.id!r})"
