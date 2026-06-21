from datetime import datetime

from sqlalchemy import (
    Column,    
    Integer,
    String,
    Float,
    BigInteger,
    DateTime,
    ForeignKey,
    Text,
    Date,
    func
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
    
    quiz_direction: Mapped[str] = mapped_column(
        String(20),
        default="TR_RU"
    )

    selected_topic: Mapped[str] = mapped_column(
        String(50),
        default="all"
    )
    
    learning_language: Mapped[str] = mapped_column(
        String(10),
        default="tr"
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

    learned_at: Mapped[datetime | None] = mapped_column(
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

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    lemma: Mapped[str] = mapped_column(
        String(100)
    )

    translation: Mapped[str] = mapped_column(
        String(100)
    )

    level: Mapped[str] = mapped_column(
        String(10),
        default="A1"
    )

    topic: Mapped[str] = mapped_column(
        String(50),
        default="general"
    )

    example_tr: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    example_ru: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )
    
    priority: Mapped[int] = mapped_column(
        Integer,
        default=100
    )

class AICache(Base):

    __tablename__ = "ai_cache"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    phrase: Mapped[str] = mapped_column(
        Text,
        unique=True
    )

    response: Mapped[str] = mapped_column(
        Text
    )

    model_name: Mapped[str] = mapped_column(
        String(100)
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

class DailyStory(Base):
    __tablename__ = "daily_stories"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(BigInteger)
    story_date: Mapped[Date] = mapped_column(Date, default=func.current_date())
    story_text: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

class EnglishWord(Base):

    __tablename__ = "english_words"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True
    )

    lemma: Mapped[str] = mapped_column(
        String(100)
    )

    translation: Mapped[str] = mapped_column(
        String(200)
    )

    level: Mapped[str] = mapped_column(
        String(10),
        default="C2"
    )

    topic: Mapped[str] = mapped_column(
        String(50),
        default="general"
    )

    example_en: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    example_ru: Mapped[str | None] = mapped_column(
        String,
        nullable=True
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        default=100
    )

class UserEnglishWord(Base):

    __tablename__ = "user_english_words"

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

    learned_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    repetitions: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    interval_days: Mapped[int] = mapped_column(
        Integer,
        default=1
    )

    next_review: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

    correct_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )

    wrong_count: Mapped[int] = mapped_column(
        Integer,
        default=0
    )
