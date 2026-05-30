from datetime import datetime

from sqlalchemy import (
    Integer,
    String,
    Float,
    BigInteger,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import (
    DeclarativeBase,
    mapped_column,
    Mapped
)


class Base(DeclarativeBase):
    pass


class User(Base):

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True
    )

    username: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    daily_new_words: Mapped[int] = mapped_column(
        Integer,
        default=15
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )


class UserWord(Base):

    __tablename__ = "user_words"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
    )

    word_id: Mapped[int] = mapped_column(
        Integer
    )

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

    next_review: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )


class ReviewHistory(Base):

    __tablename__ = "review_history"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    user_id: Mapped[int] = mapped_column(
        Integer
    )

    word_id: Mapped[int] = mapped_column(
        Integer
    )

    quality: Mapped[int] = mapped_column(
        Integer
    )

    reviewed_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

class Word(Base):

    __tablename__ = "words"

    id = Column(
        Integer,
        primary_key=True
    )

    lemma = Column(
        String(100),
        nullable=False
    )

    translation = Column(
        String(100),
        nullable=False
    )

    level = Column(
        String(10),
        default="A1"
    )

    topic = Column(
        String(50),
        default="general"
    )

    example_tr = Column(Text)

    example_ru = Column(Text)
