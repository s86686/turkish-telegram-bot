from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

from sqlalchemy import BigInteger
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import Float


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )


class Word(Base):
    __tablename__ = "words"

    id: Mapped[int] = mapped_column(primary_key=True)

    lemma: Mapped[str] = mapped_column(String(255))

    translation: Mapped[str] = mapped_column(String(255))

    level: Mapped[str] = mapped_column(String(10))

    topic: Mapped[str] = mapped_column(String(50))

    frequency_rank: Mapped[int] = mapped_column(Integer)


class UserWord(Base):
    __tablename__ = "user_words"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(Integer)

    word_id: Mapped[int] = mapped_column(Integer)

    repetitions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    ease_factor: Mapped[float] = mapped_column(
        Float,
        default=2.5
    )

    interval_days: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    correct_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    wrong_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
