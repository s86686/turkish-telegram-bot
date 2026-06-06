## Project Overview

### Purpose of the Project

The **Turkish Telegram Bot** is an interactive language learning application designed to help users learn Turkish through a Telegram bot interface. It combines spaced-repetition learning (inspired by Anki methodology), contextual dialogs, grammar lessons, and vocabulary quizzes to provide a comprehensive Turkish language learning experience.

### Main Functionality

The bot provides users with:

1. **Daily Vocabulary Learning** - Personalized new word introduction based on user preferences and daily limits
2. **Spaced Repetition Reviews** - Anki-like review system with adaptive intervals based on user performance
3. **Interactive Quizzes** - Multiple-choice vocabulary tests with bidirectional translation (Turkish ↔ Russian)
4. **Contextual Dialogs** - Real-world conversation scenarios across 12 topics (restaurant, hotel, transport, etc.)
5. **Grammar Lessons** - Bite-sized grammar explanations with practical examples
6. **Learning Statistics** - Progress tracking with accuracy metrics and learning milestones
7. **User Settings** - Customizable learning preferences (quiz direction, topic selection, daily word limit)
8. **Text-to-Speech** - Audio pronunciation of Turkish words and examples

### Key Features

| Feature | Description |
|---------|-------------|
| **Spaced Repetition** | Implements Anki-inspired algorithm with adaptive review intervals based on answer quality |
| **Bidirectional Quizzes** | Learn Turkish→Russian or Russian→Turkish |
| **Topic-Based Learning** | 18 different vocabulary topics (transport, hotel, pharmacy, etc.) |
| **Real-World Dialogs** | 12 scenario-based dialog collections with A1-level conversations |
| **Grammar Reference** | 11 mini-grammar lessons covering essential Turkish structures |
| **Progress Analytics** | Tracks learned words, accuracy rates, review counts, and learning velocity |
| **Text-to-Speech** | Edge TTS integration for Turkish pronunciation (male voice) |
| **Responsive UI** | Intuitive keyboard interface with emoji-based navigation |

### High-Level Architecture Summary

The bot employs a **modular, service-oriented architecture**:

- **Message Handler Layer** - Aiogram routers manage user interactions and callback queries
- **Service Layer** - Business logic for words, reviews, statistics, settings, and dialogs
- **Database Layer** - PostgreSQL with SQLAlchemy ORM for persistent user and learning data
- **Webhook Architecture** - Telegram updates delivered via HTTP POST to a Render-hosted web service
- **Data Services** - JSON-based external data (dialogs, grammar) loaded at startup

---

## System Architecture

### Architecture Diagram Description

```
┌─────────────────────────────────────────────────────────────────┐
│                      TELEGRAM BOT CLIENT                        │
│                    (User Device / Telegram App)                 │
└────────────────────────────┬────────────────────────────────────┘
                             │
                    Update via HTTPS (Webhook)
                             │
            ┌────────────────▼────────────────┐
            │   RENDER.COM DEPLOYMENT         │
            │  (Python Web Application)       │
            ├────────────────────────────────┤
            │  HTTP Webhook Server (aiohttp) │
            └────────────────┬────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
   ┌─────────┐      ┌──────────────┐      ┌─────────────┐
   │ Routers │      │Service Layer │      │Static Data  │
   │(Handlers)      │              │      │             │
   └────┬────┘      └──────┬───────┘      ├─────────────┤
        │                  │              │grammar.json │
        │                  │              │dialogs/*.   │
        │        ┌─────────┴────────┐     │json         │
        │        │                  │     └─────────────┘
        │        ▼                  ▼
        │   ┌────────────────────────────┐
        │   │   Database Layer           │
        │   │   (SQLAlchemy ORM)         │
        │   └────────────┬───────────────┘
        │                │
        │                ▼
        │   ┌────────────────────────────┐
        │   │  PostgreSQL Database       │
        │   │  (Render-hosted)           │
        │   └────────────────────────────┘
        │
        └────────────────┬─────────────────┐
                         │                 │
                         ▼                 ▼
                    ┌─────────┐      ┌──────────┐
                    │ TTS Srv │      │Telegram  │
                    │(Edge)   │      │Bot API   │
                    └─────────┘      └──────────┘
```

### Major Components and Their Responsibilities

| Component | Location | Responsibility |
|-----------|----------|-----------------|
| **Bot Core** | `bot.py` | Webhook setup, dispatcher initialization, update routing |
| **Handlers/Routers** | `handlers/` | Message/callback processing for lessons, stats, settings, grammar, dialogs |
| **Service Layer** | `services/` | Business logic for word selection, review scheduling, user management, stats |
| **Database Models** | `db/models.py` | ORM models: User, UserWord, Word, ReviewHistory |
| **Database Connection** | `db/database.py` | SQLAlchemy engine and session factory |
| **Keyboards** | `keyboards/` | Reply and inline keyboard UI components |
| **Static Data** | `dialogs/`, `grammar/` | JSON-based learning content (dialogs, grammar lessons) |
| **Configuration** | `config.py` | Environment variable management |

### Component Interactions

```
User Message / Callback
    │
    ▼
Dispatcher (Aiogram)
    │
    ├─→ Router Selection (CommandStart, MessageFilter, CallbackFilter)
    │
    ├─→ Handler Execution
    │   ├─ start.py → get_or_create_user()
    │   ├─ lesson.py → get_new_word() / get_review_word()
    │   ├─ settings.py → set_direction() / set_user_topic()
    │   ├─ stats.py → get_stats()
    │   ├─ grammar.py → load_grammar()
    │   └─ dialogs.py → load_dialogs()
    │
    ├─→ Service Layer Processing
    │   ├─ word_service → Query DB, build quizzes
    │   ├─ review_service → Update review intervals
    │   ├─ stats_service → Calculate user metrics
    │   └─ tts_service → Generate audio (edge_tts)
    │
    ├─→ Database Operations
    │   └─ SessionLocal() → Execute queries
    │
    └─→ Response to User
        └─ Bot.send_message() / edit_message_text()
```

### Data Flow

**Learning Session Flow:**

1. User initiates "📚 Новые слова" (New Words)
2. `get_new_word()` queries the database for:
   - Words not yet learned by user
   - Filtered by user's selected topic (if not "all")
   - Sorted by priority (lowest first)
   - Limited by user's daily word count
3. `build_quiz()` constructs multiple-choice options:
   - Correct answer selected
   - 3 random wrong answers from other words
   - Options shuffled
4. User selects answer → `process_quiz()` validates
5. User rates confidence → `save_review()` updates SM2-inspired intervals:
   - Quality 0 (Forgot): interval = 1 day
   - Quality 1 (Hard): interval = 2 days
   - Quality 2 (Good): interval scales (3 → 7 → 12.6 days)
   - Quality 3 (Easy): interval scales faster (5 → 14 → 35 days)
6. Stats aggregated and displayed

### External Integrations and Dependencies

| Integration | Purpose | Library |
|-------------|---------|---------|
| **Telegram Bot API** | User communication | aiogram 3.20.0 |
| **PostgreSQL** | Persistent data storage | psycopg2-binary 2.9.10 |
| **Text-to-Speech** | Turkish audio pronunciation | edge-tts (Microsoft Edge TTS) |
| **Task Scheduling** | (Dependency available) | apscheduler 3.11.0 |
| **Environment Config** | Config management | python-dotenv 1.1.1 |
| **ORM** | Database abstraction | SQLAlchemy 2.0.43 |
| **Render Platform** | Cloud deployment | render.yaml configuration |

---

## Repository Structure

### Directory Tree Overview

```
turkish-telegram-bot/
├── bot.py                          # Main entry point, webhook server
├── config.py                       # Environment variable configuration
├── requirements.txt                # Python dependencies
├── runtime.txt                     # Python version for Render
├── .python-version                 # Python version for local dev (3.12.10)
├── .gitignore                      # Git ignore rules
├── render.yaml                     # Render deployment configuration
│
├── db/                             # Database layer
│   ├── database.py                 # SQLAlchemy engine, SessionLocal factory
│   ├── models.py                   # ORM models (User, UserWord, Word, ReviewHistory)
│   └── seed.py                     # Database initialization
│
├── handlers/                       # Message and callback handlers
│   ├── start.py                    # /start command handler
│   ├── lesson.py                   # New words, reviews, quizzes, TTS
│   ├── stats.py                    # Statistics display
│   ├── settings.py                 # Quiz direction, topic selection
│   ├── grammar.py                  # Grammar lesson navigation
│   └── dialogs.py                  # (Handler reference - content in services)
│
├── services/                       # Business logic and data services
│   ├── users.py                    # User CRUD operations
│   ├── word_service.py             # New word fetching, review word fetching
│   ├── quiz_service.py             # Quiz generation (options, correct answer)
│   ├── review_service.py           # Spaced repetition interval calculation
│   ├── stats_service.py            # User statistics aggregation
│   ├── settings_service.py         # User preference management
│   ├── topic_service.py            # Topic enumeration and selection
│   ├── dialog_service.py           # Dialog loading from JSON
│   ├── grammar_service.py          # Grammar content loading
│   ├── tts_service.py              # Edge TTS integration
│   └── anki.py                     # Quality rating text mapping
│
├── keyboards/                      # UI Keyboard components
│   ├── menu.py                     # Main menu (ReplyKeyboard)
│   ├── review.py                   # Quiz and rating keyboards (InlineKeyboard)
│   └── settings.py                 # Settings navigation keyboard
│
├── dialogs/                        # JSON-based dialog scenarios (12 files)
│   ├── restaurant.json             # Restaurant conversation topics
│   ├── hotel.json                  # Hotel check-in/reservation scenarios
│   ├── transport.json              # Public transport inquiries
│   ├── pharmacy.json               # Pharmacy interactions
│   ├── bazaar.json                 # Market shopping
│   ├── beach.json                  # Beach/leisure activities
│   ├── cafe.json                   # Café ordering
│   ├── emergency.json              # Emergency situations
│   ├── excursions.json             # Tour and excursion inquiries
│   ├── shop.json                   # General shopping
│   ├── social.json                 # Social interactions
│   └── (2 more unlisted)
│
└── grammar/                        # JSON-based grammar reference
    └── grammar.json                # 11 mini-lessons on Turkish grammar
```

### Description of Each Major Folder

#### `db/` - Database Layer
Handles all persistent data storage and ORM configuration.
- **database.py**: Creates SQLAlchemy engine with connection pooling (`pool_pre_ping=True`)
- **models.py**: Defines five core entities (User, UserWord, Word, ReviewHistory)
- **seed.py**: Initializes database schema on application startup

#### `handlers/` - Message and Callback Handlers
Aiogram routers that process user interactions.
- **start.py** (45 lines): Initializes new users, displays welcome message
- **lesson.py** (390 lines): Core learning loop (new words, reviews, quizzes, answer validation, TTS)
- **stats.py** (72 lines): Displays user metrics
- **settings.py** (211 lines): Quiz direction toggle, topic selection
- **grammar.py** (191 lines): Grammar lesson menu and navigation
- **dialogs.py**: Referenced in bot.py but implementation details in services

#### `services/` - Business Logic
Pure functions implementing core features without Telegram dependencies.
- **word_service.py** (238 lines): Selects new/review words with priority and topic filtering
- **review_service.py** (123 lines): Implements SM2-inspired spaced repetition algorithm
- **stats_service.py** (94 lines): Aggregates learning statistics from database
- **quiz_service.py** (74 lines): Generates multiple-choice questions
- **users.py** (62 lines): User CRUD operations
- **settings_service.py** (62 lines): Manages quiz direction preference
- **topic_service.py** (124 lines): Topic enumeration with emoji-labeled names
- **dialog_service.py** (71 lines): JSON dialog file loading
- **grammar_service.py** (24 lines): Grammar content loading
- **tts_service.py** (30 lines): Edge TTS audio generation
- **anki.py** (16 lines): Quality rating text mapping

#### `keyboards/` - UI Components
Telegram keyboard markup builders.
- **menu.py** (36 lines): Main ReplyKeyboard with 6 buttons (New Words, Reviews, Stats, Settings, Dialogs, Grammar)
- **review.py** (73 lines): InlineKeyboards for quiz options, quality ratings, and navigation
- **settings.py** (31 lines): Settings menu buttons (direction toggle, topic selection)

#### `dialogs/` - Contextual Learning Content
12 JSON files containing A1-level Turkish conversation scenarios (approximately 3,500–6,300 bytes each).
Each file contains 5–15 dialog exchanges with Turkish/Russian text pairs.

#### `grammar/` - Grammar Reference
Single `grammar.json` file with 11 mini-lessons (4,379 bytes) covering:
- Questions, negation, pronouns, direction/location, tenses, numbers, requests, directions

### Description of Important Files

```python
name=bot.py url=https://github.com/s86686/turkish-telegram-bot/blob/main/bot.py
```
**Entry point**: Initializes Bot and Dispatcher, configures webhook with Render external URL, includes all routers, manages aiohttp web server lifecycle.

```python
name=config.py url=https://github.com/s86686/turkish-telegram-bot/blob/main/config.py
```
**Configuration management**: Loads `BOT_TOKEN`, `DATABASE_URL`, `WEBHOOK_SECRET`, `RENDER_EXTERNAL_URL` from environment variables.

```python
name=db/models.py url=https://github.com/s86686/turkish-telegram-bot/blob/main/db/models.py
```
**Core data model**: Defines User (profile + settings), UserWord (learning progress with SM2 metrics), Word (vocabulary + metadata), ReviewHistory (audit trail).

```python
name=services/word_service.py url=https://github.com/s86686/turkish-telegram-bot/blob/main/services/word_service.py
```
**Word selection logic**: `get_new_word()` filters unlearned words by priority/topic/daily limit; `get_review_word()` retrieves words due for review based on `next_review` timestamp.

```python
name=services/review_service.py url=https://github.com/s86686/turkish-telegram-bot/blob/main/services/review_service.py
```
**Spaced repetition**: `save_review()` implements SM2-like algorithm with four quality grades (0–3) → different interval multipliers.

---

## Technology Stack

### Programming Languages

- **Python 3.12.10** - Core language (specified in `.python-version` and `runtime.txt`)

### Frameworks

| Framework | Version | Purpose |
|-----------|---------|---------|
| **aiogram** | 3.20.0 | Telegram Bot API framework with FSM support |
| **aiohttp** | (implicit via aiogram) | Async HTTP server for webhook |
| **SQLAlchemy** | 2.0.43 | ORM for database abstraction |

### Libraries

| Library | Version | Purpose |
|---------|---------|---------|
| **psycopg2-binary** | 2.9.10 | PostgreSQL database adapter |
| **edge-tts** | (latest) | Microsoft Edge text-to-speech synthesis |
| **python-dotenv** | 1.1.1 | Environment variable loading |
| **apscheduler** | 3.11.0 | Task scheduling (dependency available, not currently used) |

### Databases

- **PostgreSQL** - Primary persistent data store (Render-hosted)
  - Tables: `users`, `user_words`, `words`, `review_history`
  - Connection pooling enabled

### Infrastructure Technologies

- **Render.com** - Cloud platform for bot deployment
- **Telegram Bot API** - Official Telegram bot API (webhook mode)
- **Microsoft Edge TTS** - Azure-backed text-to-speech service

### Build Tools

- **pip** - Python package manager
- **requirements.txt** - Dependency specification

### CI/CD Tools

- **render.yaml** - Infrastructure-as-Code configuration
  - Service type: `worker`
  - Build command: `pip install -r requirements.txt`
  - Start command: `python bot.py`
  - Environment variables: `BOT_TOKEN`, `DATABASE_URL`

---

## Installation and Setup

### Prerequisites

- Python 3.12.10 or compatible
- PostgreSQL database (local or cloud-hosted)
- Telegram Bot Token (from @BotFather)
- Render account (or alternative hosting platform)

### Environment Variables

Create a `.env` file in the root directory:

```bash
# Telegram Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here

# Database Configuration
DATABASE_URL=postgresql://user:password@localhost:5432/turkish_bot

# Webhook Configuration
WEBHOOK_SECRET=your_secret_key_here
RENDER_EXTERNAL_URL=https://your-render-deployment.onrender.com
```

**Environment Variable Reference:**

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | Yes | - | Telegram bot token from @BotFather |
| `DATABASE_URL` | Yes | - | PostgreSQL connection string |
| `WEBHOOK_SECRET` | No | `"turkish-secret"` | URL path secret for webhook |
| `RENDER_EXTERNAL_URL` | Yes | - | Public URL for webhook callbacks |

### Local Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/s86686/turkish-telegram-bot.git
   cd turkish-telegram-bot
   ```

2. **Create virtual environment:**
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up local PostgreSQL:**
   ```bash
   # Create database
   createdb turkish_bot
   
   # Update .env with local connection string
   DATABASE_URL=postgresql://localhost/turkish_bot
   ```

5. **Initialize database:**
   ```bash
   python -m db.seed
   ```

6. **Configure environment:**
   ```bash
   # Create .env file and populate with test values
   echo "BOT_TOKEN=your_test_token" > .env
   echo "DATABASE_URL=postgresql://localhost/turkish_bot" >> .env
   ```

7. **Run locally (polling mode for testing):**
   ```bash
   python bot.py
   ```

### Build Instructions

No explicit build step required. Dependencies resolved via pip install during deployment.

```bash
# Build verification
pip install -r requirements.txt --dry-run
```

### Deployment Instructions

**Deployment to Render:**

1. **Create Render account** and connect GitHub repository
2. **Configure environment variables** in Render dashboard:
   - `BOT_TOKEN`
   - `DATABASE_URL` (Render PostgreSQL)
   - `RENDER_EXTERNAL_URL` (auto-populated by Render)

3. **Create PostgreSQL database** on Render

4. **Connect repository** - Render auto-deploys on push to `main`

5. **Update Telegram webhook** - First bot startup sets webhook via `on_startup()`

**Render Configuration Specification (`render.yaml`):**

```yaml
services:
  - type: worker
    name: turkish-learning-bot
    runtime: python
    buildCommand: pip install -r requirements.txt
    startCommand: python bot.py
    envVars:
      - key: BOT_TOKEN
        sync: false
      - key: DATABASE_URL
        sync: false
```

---

## Configuration

### Configuration Files

#### `config.py`
Central configuration module loading environment variables:
```python
BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET", "turkish-secret")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")
```

#### `render.yaml`
Infrastructure-as-Code for Render deployment (service type: worker).

#### `.gitignore`
Excludes sensitive files:
- `.env` - Environment variables
- `__pycache__/` - Python cache
- `.idea/`, `.vscode/` - IDE files
- `storage/` - Local file storage
- `*.db` - SQLite databases

#### `.python-version`
Specifies Python 3.12.10 for `pyenv` version management.

### Runtime Settings

**Hardcoded Configuration (subject to code changes):**

| Setting | File | Value | Purpose |
|---------|------|-------|---------|
| Daily word limit | `db/models.py` | 15 (default) | Max new words per user per day |
| Quiz direction | `db/models.py` | "TR_RU" (default) | Default Turkish→Russian |
| Selected topic | `db/models.py` | "all" (default) | Default to all words |
| Spaced repetition | `services/review_service.py` | SM2-inspired | Interval multipliers per quality |
| Webhook path | `bot.py` | `/webhook/{WEBHOOK_SECRET}` | HTTP POST endpoint |
| TTS voice | `services/tts_service.py` | "tr-TR-AhmetNeural" | Turkish male voice |

### Environment-Specific Settings

**Development:**
- Local PostgreSQL instance
- Polling mode (not used; webhook server runs locally)
- `.env` with test credentials

**Production (Render):**
- Render-hosted PostgreSQL
- Webhook mode via `RENDER_EXTERNAL_URL`
- Environment variables synchronized with Render dashboard

---

## API Documentation

### Telegram Bot API Endpoints

The bot does not expose custom REST APIs. All interaction is through Telegram's Bot API and webhook callbacks.

#### Webhook Endpoint

**Route:** `POST /webhook/{WEBHOOK_SECRET}`

**Purpose:** Receive Telegram updates via webhook (longpolling alternative)

**Request Format:**
```json
{
  "update_id": 123456789,
  "message": {
    "message_id": 1,
    "from": {
      "id": 987654321,
      "is_bot": false,
      "first_name": "User"
    },
    "chat": {
      "id": 987654321,
      "type": "private"
    },
    "date": 1717598000,
    "text": "/start"
  }
}
```

**Response Format:**
```
HTTP 200 OK
Body: "ok"
```

**Implementation:** `bot.py` lines 54–65

---

### Handler Routes and Command Callbacks

#### `/start` Command

**Handler:** `handlers/start.py`

**Trigger:** `CommandStart()` filter

**Action:**
1. Extract user ID and username from message
2. Call `get_or_create_user()` to upsert in database
3. Send welcome message with main menu

**Response:**
```
🇹🇷 Добро пожаловать в Turkish Learning Bot

Каждый день:
• новые слова
• повторения по Anki
• мини-тесты

Нажмите «📚 Урок» чтобы начать.
```

---

#### "📚 Новые слова" (New Words Button)

**Handler:** `handlers/lesson.py` lines 55–106

**Trigger:** `lambda m: m.text == "📚 Новые слова"`

**Parameters:** None (extracted from message context)

**Action:**
1. Call `get_new_word(telegram_id)` to retrieve next word
2. Construct question text via `build_question_text()`
3. Send question with quiz keyboard (4 multiple choice options)

**Response Scenarios:**
- **Word available:** Display question with 4 options
- **Daily limit reached:** "🎉 Лимит новых слов на сегодня достигнут..."
- **Topic finished:** "🎉 Вы изучили все новые слова этой темы..."
- **No words:** "🎉 Новых слов больше нет."

**Response Format:**
```
Что означает?

🇹🇷 merhaba

[Option 1] [Option 2] [Option 3] [Option 4]
```

---

#### "🔁 Повторения" (Reviews Button)

**Handler:** `handlers/lesson.py` lines 108–140

**Trigger:** `lambda m: m.text == "🔁 Повторения"`

**Parameters:** None

**Action:**
1. Call `get_review_word(telegram_id)` for words due for review
2. Construct and display question with quiz keyboard

**Response Scenarios:** Same as new words (no reviews → "🎉 Сегодня повторений нет.")

---

#### Quiz Answer Callback

**Handler:** `handlers/lesson.py` lines 144–189

**Trigger:** `F.data.startswith("quiz_")`

**Callback Data Format:** `quiz_{option_index}` (e.g., `quiz_0`)

**Parameters:**
- `option_index`: 0–3 (selected answer index)
- `word`: Retrieved from `CURRENT_WORDS` dict

**Action:**
1. Extract selected option index
2. Compare with correct answer
3. Display result (✅ or ❌) with translation and example
4. Show quality rating keyboard

**Response Format:**
```
✅ Верно

🇹🇷 merhaba
🇷🇺 привет

Merhaba, nasılsın?
Привет, как дела?

[😵 Забыл] [😕 Трудно]
[🙂 Хорошо] [😎 Легко]
[🔊 Слушать]
```

---

#### Quality Rating Callback

**Handler:** `handlers/lesson.py` lines 192–228

**Trigger:** `F.data.startswith("q_")`

**Callback Data Format:** `q_{quality}` where quality ∈ {0, 1, 2, 3}

**Parameters:**
- `quality`: 0 (forgot) → 3 (easy)

**Action:**
1. Call `save_review()` with quality rating
2. Calculate next review interval (returned)
3. Display confirmation with interval
4. Show next word button

**Response Format:**
```
✅ Ответ сохранён

📅 Следующее повторение через 3 дн.

[➡ Следующее слово]
```

---

#### TTS Callback

**Handler:** `handlers/lesson.py` lines 231–291

**Trigger:** `F.data == "speak"`

**Parameters:** Current word from `CURRENT_WORDS`

**Action:**
1. Check if already generating audio (prevent race)
2. Call `generate_tts(text)` to create MP3
3. Send voice message to user
4. Clean up temporary audio file

**Response:** Voice message with Turkish pronunciation

---

#### "📈 Статистика" (Statistics Button)

**Handler:** `handlers/stats.py` lines 11–71

**Trigger:** `lambda m: m.text == "📈 Статистика"`

**Parameters:** None

**Action:**
1. Call `get_stats(telegram_id)` for user metrics
2. Calculate accuracy percentage
3. Format and display statistics

**Response Format:**
```
📈 Статистика

📚 Изучено слов: 42

🆕 Сегодня изучено: 15 / 15

🔁 К повторению: 8

📦 Осталось новых слов: 958

🎯 Точность: 84.3%

✅ Правильных ответов: 104
❌ Ошибок: 19
```

---

#### "⚙ Настройки" (Settings Button)

**Handler:** `handlers/settings.py` lines 61–105

**Trigger:** `lambda m: m.text == "⚙ Настройки"`

**Parameters:** None

**Action:**
1. Call `get_direction()` to retrieve current quiz direction
2. Call `get_user_topic()` to retrieve selected topic
3. Display current settings with direction keyboard

**Response Format:**
```
⚙ Настройки

Текущее направление:
🇹🇷 → 🇷🇺

Текущая тема:
🏨 Отель

[🇹🇷 → 🇷🇺] [🇷🇺 → 🇹🇷]
[📚 Тема изучения]
```

---

#### Direction Toggle Callbacks

**Handlers:** `handlers/settings.py` lines 108–145

**Triggers:** `F.data == "dir_tr_ru"` or `F.data == "dir_ru_tr"`

**Parameters:** None

**Action:**
1. Call `set_direction(telegram_id, direction)` to update database
2. Display confirmation

**Response Format:**
```
✅ Направление изменено

🇹🇷 → 🇷🇺
```

---

#### Topic Selection Callbacks

**Handler:** `handlers/settings.py` lines 178–210

**Trigger:** `lambda c: c.data.startswith("topic_")`

**Callback Data Format:** `topic_{topic_name}` (e.g., `topic_hotel`)

**Parameters:** Topic name extracted from callback

**Action:**
1. Call `set_user_topic(telegram_id, topic)` to update database
2. Display confirmation

**Response Format:**
```
✅ Тема изменена

🏨 Отель
```

---

#### "📖 Грамматика" (Grammar Button)

**Handler:** `handlers/grammar.py` lines 82–92

**Trigger:** `lambda m: m.text == "📖 Грамматика"`

**Parameters:** None

**Action:**
1. Load grammar lessons via `load_grammar()`
2. Display grammar menu keyboard

**Response Format:**
```
📖 Мини-грамматика

Выберите тему:

[❓ Как задавать вопросы]
[❌ Как сказать 'не']
[👤 Я / Ты / Он]
[... 8 more lessons ...]
```

---

#### Grammar Lesson Navigation

**Handlers:** `handlers/grammar.py` lines 110–189

**Triggers:**
- `lambda c: c.data.startswith("grammar_") and c.data.count("_") == 1` → Show lesson
- `lambda c: c.data.startswith("grammar_next_")` → Next lesson
- `lambda c: c.data.startswith("grammar_prev_")` → Previous lesson

**Parameters:** Lesson index (0–10)

**Action:**
1. Retrieve lesson from `GRAMMAR` list
2. Display lesson content
3. Show navigation buttons (if applicable)

**Response Format:**
```
❓ Как задавать вопросы

В турецком для вопросов используются частицы mı / mi / mu / mü...

[⬅️ Предыдущий] [➡️ Следующий]
[📚 Все уроки]
```

---

### Error Handling

**No explicit error responses defined.** If operations fail silently:
- `get_new_word()` returns `None` → "🎉 Новых слов больше нет."
- `get_stats()` returns `None` → "Нет данных."
- Missing user → No action taken

---

## Database Documentation

### Database Technologies Used

- **PostgreSQL** - Relational database management system
- **SQLAlchemy 2.0.43** - Python ORM with modern API
- **psycopg2-binary 2.9.10** - PostgreSQL adapter

### Schema Overview

```sql
-- 4 Tables, 1:N and 1:1 relationships

Users (1) ---> (Many) UserWords
             ---> (Many) ReviewHistory

Words (1) ---> (Many) UserWords
```

### Tables/Entities

#### **users** Table

| Column | Type | Constraints | Default | Purpose |
|--------|------|-------------|---------|---------|
| id | Integer | PRIMARY KEY | auto-increment | Internal user ID |
| telegram_id | BigInteger | UNIQUE NOT NULL | - | Telegram user ID |
| username | String(255) | NULLABLE | NULL | Telegram username |
| daily_new_words | Integer | NOT NULL | 15 | Words to learn per day |
| quiz_direction | String(20) | NOT NULL | "TR_RU" | Turkish→Russian or reverse |
| selected_topic | String(50) | NOT NULL | "all" | Topic filter (all, transport, hotel, etc.) |
| created_at | DateTime | NOT NULL | datetime.utcnow() | Account creation timestamp |

**ORM Model:** `db/models.py` lines 23–60

---

#### **words** Table

| Column | Type | Constraints | Default | Purpose |
|--------|------|-------------|---------|---------|
| id | Integer | PRIMARY KEY | auto-increment | Word ID |
| lemma | String(100) | NOT NULL | - | Turkish word (base form) |
| translation | String(100) | NOT NULL | - | Russian translation |
| level | String(10) | NOT NULL | "A1" | CEFR level (A1–C2) |
| topic | String(50) | NOT NULL | "general" | Learning topic (transport, hotel, etc.) |
| example_tr | String | NULLABLE | NULL | Turkish usage example |
| example_ru | String | NULLABLE | NULL | Russian usage example |
| priority | Integer | NOT NULL | 100 | Selection priority (lower = higher) |

**ORM Model:** `db/models.py` lines 141–182

---

#### **user_words** Table

| Column | Type | Constraints | Default | Purpose |
|--------|------|-------------|---------|---------|
| id | Integer | PRIMARY KEY | auto-increment | Record ID |
| user_id | Integer | FK(users.id) | - | Link to user |
| word_id | Integer | NOT NULL | - | Link to word |
| repetitions | Integer | NOT NULL | 0 | Successful review count |
| ease_factor | Float | NOT NULL | 2.5 | SM2 ease factor |
| interval_days | Integer | NOT NULL | 1 | Days until next review |
| correct_count | Integer | NOT NULL | 0 | Total correct answers |
| wrong_count | Integer | NOT NULL | 0 | Total incorrect answers |
| next_review | DateTime | NULLABLE | NULL | Scheduled next review date |
| learned_at | DateTime | NULLABLE | NULL | First learning timestamp |

**ORM Model:** `db/models.py` lines 63–113

**Purpose:** Tracks individual user's learning progress for each word using SM2-inspired metrics.

---

#### **review_history** Table

| Column | Type | Constraints | Default | Purpose |
|--------|------|-------------|---------|---------|
| id | Integer | PRIMARY KEY | auto-increment | Record ID |
| user_id | Integer | NOT NULL | - | User who reviewed |
| word_id | Integer | NOT NULL | - | Word reviewed |
| quality | Integer | NOT NULL | - | Rating 0–3 (forgot to easy) |
| reviewed_at | DateTime | NOT NULL | datetime.utcnow() | Review timestamp |

**ORM Model:** `db/models.py` lines 115–139

**Purpose:** Audit trail of all review events (not currently queried in handlers, but preserved for analytics).

---

### Relationships

```
User (1) ──── (N) UserWord
  │ id              │ user_id (FK)
  │                 │ word_id
  │                 │ next_review
  │                 │ learned_at
  │                 └─ linked to Word.id
  │
  └──── (N) ReviewHistory
         user_id (FK)
         word_id
         quality
         reviewed_at

Word (1) ──── (N) UserWord
  id              word_id (FK)
  lemma
  translation
  topic
  priority
```

---

### Migrations

**No migration system implemented.** Database initialization via:

```python
# db/seed.py
def create_tables():
    Base.metadata.create_all(bind=engine)
```

Called on application startup (`bot.py` line 70).

**For schema changes:**
1. Modify ORM models in `db/models.py`
2. Manually delete tables (or use `ALTER TABLE` in PostgreSQL)
3. Restart application to regenerate schema

**⚠️ Known Issue:** No versioned migrations; dropping tables loses data.

---

## Business Logic

### Core Workflows

#### 1. New User Onboarding

```
User sends /start
    ↓
get_or_create_user(telegram_id, username)
    ├─ Query: SELECT * FROM users WHERE telegram_id = ?
    ├─ If exists: Return user
    └─ If not: INSERT INTO users (telegram_id, username, daily_new_words=15, quiz_direction="TR_RU", selected_topic="all")
         ↓
         Return user record
    ↓
Display welcome message + main menu
```

**Code Reference:** `handlers/start.py` lines 17–35, `services/users.py` lines 47–61

---

#### 2. Learning New Words

```
User clicks "📚 Новые слова"
    ↓
get_new_word(telegram_id)
    ├─ Query: SELECT * FROM users WHERE telegram_id = ?
    ├─ Count words learned today: 
    │   SELECT COUNT(*) FROM user_words 
    │   WHERE user_id = ? AND learned_at.date() = TODAY
    ├─ If count >= user.daily_new_words: 
    │   RETURN "LIMIT_REACHED"
    ├─ Query unlearned words:
    │   SELECT * FROM words 
    │   WHERE id NOT IN (SELECT word_id FROM user_words WHERE user_id = ?)
    │   AND (topic = user.selected_topic OR user.selected_topic = "all")
    │   ORDER BY priority ASC
    ├─ If no words: 
    │   RETURN "TOPIC_FINISHED" or None
    ├─ Select word with min priority:
    │   Pick random word among those with priority = MIN(priority)
    ├─ Build quiz options:
    │   - Correct: word.lemma or word.translation (based on quiz_direction)
    │   - Wrong: 3 random other word translations/lemmas
    │   - Shuffle and index
    └─ Return word object with quiz metadata
    ↓
Display question + 4 options (inline keyboard)
```

**Code Reference:** `services/word_service.py` lines 44–154

---

#### 3. Quiz Answer Validation & Review Scheduling

```
User selects answer option
    ↓
process_quiz(callback, selected_option_index)
    ├─ Retrieve word from CURRENT_WORDS dict
    ├─ Compare selected_option_index with correct_index
    ├─ If match: result = "✅ Верно"
    └─ Else: result = "❌ Неверно"
    ↓
Display result + translation + example + quality keyboard
    ↓
User rates confidence (0–3)
    ↓
save_review(telegram_id, word_id, quality)
    ├─ Query: SELECT * FROM users WHERE telegram_id = ?
    ├─ Query or INSERT user_word:
    │   SELECT * FROM user_words WHERE user_id = ? AND word_id = ?
    │   IF NOT EXISTS: INSERT with defaults (repetitions=0, ease_factor=2.5, interval_days=1)
    ├─ Calculate next_review based on quality:
    │   │
    │   ├─ quality == 0 (Forgot):
    │   │   interval_days = 1
    │   │   repetitions = 0
    │   │
    │   ├─ quality == 1 (Hard):
    │   │   interval_days = 2
    │   │   repetitions = max(0, repetitions - 1)
    │   │
    │   ├─ quality == 2 (Good):
    │   │   repetitions += 1
    │   │   IF repetitions == 1: interval_days = 3
    │   │   ELIF repetitions == 2: interval_days = 7
    │   │   ELSE: interval_days *= 1.8
    │   │
    │   └─ quality == 3 (Easy):
    │       repetitions += 1
    │       IF repetitions == 1: interval_days = 5
    │       ELIF repetitions == 2: interval_days = 14
    │       ELSE: interval_days *= 2.5
    │
    ├─ next_review = NOW + timedelta(days=interval_days)
    ├─ Update correct_count or wrong_count
    ├─ COMMIT changes
    └─ RETURN interval_days
    ↓
Display confirmation: "✅ Ответ сохранён. 📅 Следующее повторение через X дн."
```

**Code Reference:** `services/review_service.py` lines 14–122

---

#### 4. Retrieving Review Words (Spaced Repetition)

```
User clicks "🔁 Повторения"
    ↓
get_review_word(telegram_id)
    ├─ Query: SELECT * FROM users WHERE telegram_id = ?
    ├─ Find due word:
    │   SELECT * FROM user_words 
    │   WHERE user_id = ? AND next_review <= NOW
    │   ORDER BY next_review ASC
    │   LIMIT 1
    ├─ If no due word: RETURN None
    ├─ Fetch associated word: SELECT * FROM words WHERE id = ?
    ├─ If word deleted: DELETE user_word, RETURN get_review_word() (recursion)
    ├─ Build quiz (same as new words)
    └─ RETURN word with quiz
    ↓
Display question + 4 options
```

**Code Reference:** `services/word_service.py` lines 159–237

---

#### 5. Statistics Aggregation

```
User clicks "📈 Статистика"
    ↓
get_stats(telegram_id)
    ├─ Query: SELECT * FROM users WHERE telegram_id = ?
    ├─ Count learned: SELECT COUNT(*) FROM user_words WHERE user_id = ?
    ├─ Sum correct: SELECT SUM(correct_count) FROM user_words WHERE user_id = ?
    ├─ Sum wrong: SELECT SUM(wrong_count) FROM user_words WHERE user_id = ?
    ├─ Count reviews due: 
    │   SELECT COUNT(*) FROM user_words 
    │   WHERE user_id = ? AND next_review <= NOW
    ├─ Calculate remaining new words: 
    │   total_words - learned_count
    ├─ Count learned today:
    │   SELECT COUNT(*) FROM user_words 
    │   WHERE user_id = ? AND learned_at.date() = TODAY
    ├─ Calculate accuracy: 
    │   correct / (correct + wrong) * 100
    └─ RETURN stats dict
    ↓
Display formatted statistics
```

**Code Reference:** `services/stats_service.py` lines 12–93

---

### Important Services

#### `services/word_service.py`

**Core Functions:**
- `get_new_word(telegram_id)`: Selects unlearned word respecting daily limit and topic filter
- `get_review_word(telegram_id)`: Retrieves word due for spaced repetition review
- `build_word_result(word, all_words, direction)`: Constructs quiz-ready word object

**Key Logic:**
- Priority-based selection (min priority word preferred among due words)
- Topic filtering
- Daily limit enforcement
- Recursive orphan cleanup (if word deleted, retry)

---

#### `services/review_service.py`

**Core Function:**
- `save_review(telegram_id, word_id, quality)`: Implements SM2-inspired spaced repetition

**Algorithm:**
- Quality 0 → Hard reset (interval = 1 day)
- Quality 1 → Slight backoff (interval = 2 days)
- Quality 2 → Moderate spacing (3 → 7 → 12.6 days with 1.8x multiplier)
- Quality 3 → Aggressive spacing (5 → 14 → 35 days with 2.5x multiplier)

---

#### `services/quiz_service.py`

**Core Function:**
- `build_quiz(current_word, all_words, direction)`: Generates multiple-choice question

**Logic:**
- Selects correct answer from lemma or translation based on direction
- Samples 3 random wrong answers from other words
- Shuffles and returns with correct index

---

#### `services/stats_service.py`

**Core Function:**
- `get_stats(telegram_id)`: Aggregates all user metrics

**Metrics Calculated:**
- `learned`: Total words in user_words
- `correct`: Sum of correct_count
- `wrong`: Sum of wrong_count
- `review_today`: Count of words with next_review ≤ NOW
- `new_words`: Total words - learned
- `learned_today`: Count of words with learned_at.date() = TODAY
- `daily_limit`: User's daily_new_words setting

---

#### `services/topic_service.py`

**Core Functions:**
- `get_topics()`: Queries distinct topics from words table
- `get_user_topic(telegram_id)`: Retrieves user's selected topic
- `set_user_topic(telegram_id, topic)`: Updates user's topic preference
- `get_topic_name(topic)`: Maps topic slug to emoji label

**Topic Mapping (18 topics):**
```python
TOPIC_NAMES = {
    "general": "📚 Общие слова",
    "transport": "🚌 Транспорт",
    "hotel": "🏨 Отель",
    ... (15 more)
}
```

---

### Processing Pipelines

#### Word Learning Pipeline

```
Start
  │
  ├─→ [Handler: new_words() / reviews()]
  │    └─→ Call get_new_word() / get_review_word()
  │
  ├─→ [Service: word_service]
  │    ├─→ Query database for word
  │    ├─→ Enforce limits/filters
  │    └─→ Call build_quiz()
  │
  ├─→ [Service: quiz_service]
  │    └─→ Generate options with correct answer
  │
  ├─→ [Handler: Render quiz message]
  │    └─→ Send to user with inline keyboard
  │
  ├─→ [Callback: process_quiz()]
  │    ├─→ Validate answer
  │    └─→ Display result
  │
  ├─→ [Callback: rate_word()]
  │    └─→ Call save_review()
  │
  ├─→ [Service: review_service]
  │    ├─→ Query/insert user_word
  │    ├─→ Calculate SM2 interval
  │    └─→ Update database
  │
  └─→ End (Display confirmation)
```

---

## Module Documentation

### `handlers/start.py`

**Purpose:** Handle `/start` command and user onboarding

**Public Interfaces:**
```python
@router.message(CommandStart())
async def start(message: Message):
    """Initialize new user or greet returning user"""
```

**Dependencies:**
- `services.users.get_or_create_user()`
- `keyboards.menu.main_menu`
- `aiogram.Router`, `aiogram.filters.CommandStart`

**Workflow:**
1. Extract user ID and username from message
2. Call service to get or create user record
3. Send welcome message with main menu keyboard

---

### `handlers/lesson.py`

**Purpose:** Core learning loop (new words, reviews, quizzes, quality rating)

**Public Interfaces:**
```python
@router.message(lambda m: m.text == "📚 Новые слова")
async def new_words(message: Message)

@router.message(lambda m: m.text == "🔁 Повторения")
async def reviews(message: Message)

@router.callback_query(F.data.startswith("quiz_"))
async def process_quiz(callback: CallbackQuery)

@router.callback_query(F.data.startswith("q_"))
async def rate_word(callback: CallbackQuery)

@router.callback_query(F.data == "speak")
async def speak_word(callback: CallbackQuery)

@router.callback_query(F.data.startswith("next_"))
async def next_word(callback: CallbackQuery)
```

**Dependencies:**
- `services.word_service`
- `services.review_service`
- `services.tts_service`
- `keyboards.review`

**Global State (Handler-Level):**
```python
CURRENT_WORDS = {}        # {user_id: word_dict}
VOICE_MESSAGES = {}       # {user_id: message_id}
CURRENT_MODE = {}         # {user_id: "new" | "review"}
SPEAK_IN_PROGRESS = set() # {user_id, ...}
```

**Internal Workflow:**
- `new_words()` / `reviews()` → Fetch word → Store in `CURRENT_WORDS` → Display quiz
- `process_quiz()` → Validate answer → Store result → Request quality rating
- `rate_word()` → Save review → Calculate interval → Prompt next word
- `speak_word()` → Generate TTS → Send audio → Cleanup
- `next_word()` → Fetch next word → Repeat quiz or conclude

---

### `handlers/stats.py`

**Purpose:** Display user learning statistics

**Public Interface:**
```python
@router.message(lambda m: m.text == "📈 Статистика")
async def stats(message: Message)
```

**Dependencies:**
- `services.stats_service.get_stats()`

**Workflow:**
1. Call service to aggregate statistics
2. Calculate accuracy percentage
3. Format and display results

---

### `handlers/settings.py`

**Purpose:** Manage user preferences (quiz direction, topic selection)

**Public Interfaces:**
```python
@router.message(lambda m: m.text == "⚙ Настройки")
async def settings(message: Message)

@router.callback_query(F.data == "dir_tr_ru")
async def dir_tr_ru(callback: CallbackQuery)

@router.callback_query(F.data == "dir_ru_tr")
async def dir_ru_tr(callback: CallbackQuery)

@router.callback_query(F.data == "choose_topic")
async def choose_topic(callback: CallbackQuery)

@router.callback_query(lambda c: c.data.startswith("topic_"))
async def set_topic(callback: CallbackQuery)
```

**Dependencies:**
- `services.settings_service`
- `services.topic_service`
- `keyboards.settings`

**Workflow:**
1. Display current settings
2. Allow direction toggle (TR↔RU)
3. Allow topic selection from dynamic list
4. Persist changes to database

---

### `handlers/grammar.py`

**Purpose:** Navigation through mini-grammar reference

**Public Interfaces:**
```python
@router.message(lambda m: m.text == "📖 Грамматика")
async def grammar_menu(message: Message)

@router.callback_query(lambda c: c.data == "grammar_menu")
async def show_grammar_menu(callback: CallbackQuery)

@router.callback_query(lambda c: c.data.startswith("grammar_") and c.data.count("_") == 1)
async def show_lesson(callback: CallbackQuery)

@router.callback_query(lambda c: c.data.startswith("grammar_next_"))
async def next_lesson(callback: CallbackQuery)

@router.callback_query(lambda c: c.data.startswith("grammar_prev_"))
async def prev_lesson(callback: CallbackQuery)
```

**Dependencies:**
- `services.grammar_service.load_grammar()`

**Global State:**
```python
GRAMMAR = load_grammar()  # Loaded at module init
```

**Workflow:**
1. Load grammar.json into memory on startup
2. Display grammar menu with selectable lessons
3. Navigate forward/backward through lessons

---

### `services/word_service.py`

**Purpose:** Word selection logic for learning and review

**Public Interfaces:**
```python
def get_new_word(telegram_id: int) -> dict | str | None
def get_review_word(telegram_id: int) -> dict | str | None
```

**Dependencies:**
- `db.database.SessionLocal()`
- `db.models.User`, `Word`, `UserWord`
- `services.quiz_service.build_quiz()`

**Return Values:**
- `dict`: Word object with quiz metadata
- `"LIMIT_REACHED"`: Daily limit for new words exceeded
- `"TOPIC_FINISHED"`: All words in selected topic learned
- `None`: No words available

**Internal Functions:**
```python
def build_word_result(word, all_words, direction) -> dict
```

---

### `services/review_service.py`

**Purpose:** Spaced repetition review scheduling

**Public Interface:**
```python
def save_review(telegram_id: int, word_id: int, quality: int) -> int
```

**Parameters:**
- `quality` ∈ {0, 1, 2, 3}: User's self-assessment

**Return Value:**
- `int`: Next review interval in days

**Dependencies:**
- `db.database.SessionLocal()`
- `db.models.User`, `UserWord`
- `datetime.timedelta`

**Algorithm Details:**

| Quality | Interpretation | Action | Interval |
|---------|-----------------|--------|----------|
| 0 | Forgot | Reset | 1 day |
| 1 | Hard | Backoff | 2 days |
| 2 | Good | Moderate spacing | 3/7/12.6 days (1st/2nd/3rd+) |
| 3 | Easy | Aggressive spacing | 5/14/35 days (1st/2nd/3rd+) |

---

### `services/quiz_service.py`

**Purpose:** Multiple-choice question generation

**Public Interface:**
```python
def build_quiz(current_word: dict, all_words: list, direction: str = "TR_RU") -> dict
```

**Parameters:**
- `current_word`: Word dict with lemma/translation
- `all_words`: List of all available words
- `direction`: "TR_RU" (Turkish→Russian) or "RU_TR"

**Return Format:**
```python
{
    "question": "merhaba",  # Display text
    "options": ["hello", "goodbye", "thanks", "ok"],  # Shuffled
    "correct": 0  # Index of correct option
}
```

**Logic:**
1. Determine correct answer based on direction
2. Sample 3 random wrong answers from other words
3. Append correct answer and shuffle
4. Return with correct index

---

### `services/stats_service.py`

**Purpose:** User metrics aggregation

**Public Interface:**
```python
def get_stats(telegram_id: int) -> dict | None
```

**Return Format:**
```python
{
    "learned": 42,           # Total words in learning
    "correct": 104,          # Total correct answers
    "wrong": 19,             # Total wrong answers
    "review_today": 8,       # Due for review today
    "new_words": 958,        # Not yet learned
    "learned_today": 15,     # Learned so far today
    "daily_limit": 15        # User's daily word limit
}
```

**Dependencies:**
- `db.database.SessionLocal()`
- `db.models.User`, `UserWord`, `Word`
- `datetime.datetime`

---

### `services/users.py`

**Purpose:** User CRUD operations

**Public Interfaces:**
```python
def get_user_by_telegram_id(telegram_id: int) -> User | None
def create_user(telegram_id: int, username: str | None) -> User
def get_or_create_user(telegram_id: int, username: str | None) -> User
```

**Default User Settings:**
- `daily_new_words`: 15
- `quiz_direction`: "TR_RU"
- `selected_topic`: "all"

---

### `services/topic_service.py`

**Purpose:** Topic enumeration and management

**Public Interfaces:**
```python
def get_topics() -> list[str]
def get_topic_name(topic: str) -> str
def get_user_topic(telegram_id: int) -> str
def set_user_topic(telegram_id: int, topic: str) -> None
```

**18 Predefined Topics:**
- General: general, social, family, people, education, home
- Travel/Locations: transport, hotel, beach, airport, excursions
- Services: pharmacy, restaurant, cafe, bazaar/market, shop
- Emergency: emergency

---

### `services/settings_service.py`

**Purpose:** User preference persistence

**Public Interfaces:**
```python
def set_direction(telegram_id: int, direction: str) -> None
def get_direction(telegram_id: int) -> str
```

**Directions:**
- `"TR_RU"`: Turkish word shown, Russian options
- `"RU_TR"`: Russian word shown, Turkish options

---

### `services/dialog_service.py`

**Purpose:** Load dialog scenarios from JSON

**Public Interfaces:**
```python
def load_dialogs(filename: str) -> list[dict]
def load_all_dialogs() -> dict[str, list[dict]]
```

**Dialog Structure:**
```json
[
  {
    "id": 1,
    "title": "Dialog Title",
    "level": "A1",
    "lines": [
      {"speaker": "Siz", "tr": "Turkish", "ru": "Russian"},
      {"speaker": "Other", "tr": "Turkish", "ru": "Russian"}
    ]
  }
]
```

---

### `services/grammar_service.py`

**Purpose:** Load grammar lessons from JSON

**Public Interface:**
```python
def load_grammar() -> list[dict]
```

**Grammar Lesson Structure:**
```json
[
  {
    "id": "questions",
    "title": "❓ Как задавать вопросы",
    "content": "Lesson explanation text..."
  }
]
```

---

### `services/tts_service.py`

**Purpose:** Turkish text-to-speech synthesis

**Public Interface:**
```python
async def generate_tts(text: str) -> str
```

**Parameters:**
- `text`: Turkish text to synthesize

**Return Value:**
- `str`: Path to generated MP3 file (e.g., `"audio/uuid.mp3"`)

**Dependencies:**
- `edge_tts`: Microsoft Edge TTS API
- Voice: `"tr-TR-AhmetNeural"` (Turkish male)

**Workflow:**
1. Generate UUID for unique filename
2. Create `audio/` directory if missing
3. Call Edge TTS with Turkish voice
4. Save MP3 to disk
5. Return file path

---

### `keyboards/menu.py`

**Purpose:** Main navigation keyboard

**Public Interface:**
```python
main_menu: ReplyKeyboardMarkup
```

**Buttons:**
```
[📚 Новые слова]  [🔁 Повторения]
[📈 Статистика]   [⚙ Настройки]
[🎭 Диалоги]      [📖 Грамматика]
```

---

### `keyboards/review.py`

**Purpose:** Quiz and rating keyboard components

**Public Interfaces:**
```python
def quality_keyboard() -> InlineKeyboardMarkup
def quiz_keyboard(options: list[str]) -> InlineKeyboardMarkup
def next_word_keyboard(mode: str) -> InlineKeyboardMarkup
```

**Keyboards:**
- `quality_keyboard()`: 4 quality buttons + speak button
- `quiz_keyboard()`: Dynamic option buttons (4 options)
- `next_word_keyboard()`: Next word button with mode tracking

---

### `keyboards/settings.py`

**Purpose:** Settings navigation keyboard

**Public Interface:**
```python
def direction_keyboard() -> InlineKeyboardMarkup
```

**Buttons:**
```
[🇹🇷 → 🇷🇺]  (toggle to TR_RU)
[🇷🇺 → 🇹🇷]  (toggle to RU_TR)
[📚 Тема изучения]  (topic selection)
```

---

## Security Considerations

### Authentication

- **Telegram Bot Token:** Required as `BOT_TOKEN` environment variable
  - Never committed to repository
  - Only accessible to authorized deployment environment
  - Regenerate if compromised

- **Webhook Secret:** `WEBHOOK_SECRET` parameter in URL path
  - Protects webhook from unauthorized POST requests
  - Default: `"turkish-secret"` (weak; should override in production)
  - Accessible only via HTTPS (enforced by Render)

- **User Identification:**
  - Via Telegram's `message.from_user.id` (BigInteger)
  - Telegram cryptographically signs all updates
  - No additional authentication required (trust Telegram API)

### Authorization

- **No role-based access control (RBAC):** All users have identical permissions
- **User isolation:** Queries filtered by `user_id` or `telegram_id`
  - Cannot access other users' words, progress, or statistics
  - No cross-user data leakage by design

### Secrets Management

| Secret | Storage | Usage | Rotation |
|--------|---------|-------|----------|
| `BOT_TOKEN` | Render Env Vars | Telegram API auth | Manual via @BotFather |
| `DATABASE_URL` | Render Env Vars | PostgreSQL connection | Manual (change DB password) |
| `WEBHOOK_SECRET` | Render Env Vars | URL path parameter | Optional (not used for crypto) |

**Best Practices:**
- Use strong `WEBHOOK_SECRET` (e.g., 32-char random string)
- Rotate `BOT_TOKEN` periodically (via @BotFather)
- Use strong PostgreSQL password
- Enable SSL/TLS for database connection (built into `postgresql://` URLs)

### Security-Sensitive Components

#### `handlers/lesson.py` - State Management
- **Risk:** `CURRENT_WORDS`, `SPEAK_IN_PROGRESS` are global dicts keyed by user_id
  - User A could theoretically access User B's word if knowing their ID
  - **Mitigation:** State is transient and expires after message edit
  - **Impact:** Low (state cleared per interaction)

#### `services/word_service.py` - Query Injection
- **Risk:** No dynamic SQL; SQLAlchemy parameterizes all queries
- **Mitigation:** ORM prevents SQL injection
- **Impact:** None (safe)

#### `services/tts_service.py` - File System Access
- **Risk:** Generated MP3 files stored in `audio/` directory (potentially world-readable)
- **Mitigation:** Files are temporary and cleaned up immediately
- **Impact:** Low (files deleted after send)

#### Database Access
- **Risk:** `SessionLocal()` creates unthreaded session per function call
- **Mitigation:** Render runs single Python process (no multi-threading)
- **Impact:** None (synchronous operations)

---

## Logging and Monitoring

### Logging Mechanisms

**Current Implementation:**
- Minimal logging (only startup messages and errors)
- Statements via `print()` (Python stdout)

**Startup Logs (from `bot.py`):**
```python
print(f"Webhook set: {webhook_url}")  # Line 81–82
print("Webhook server started")       # Line 116–117
```

**Error Logs (from `services/dialog_service.py`):**
```python
print(f"Loaded dialogs: {filepath.name}")       # Line 60–61
print(f"Error loading {filepath.name}: {e}")    # Line 66–67
```

### Metrics

**No explicit metrics collection.** Statistics available post-hoc via database queries:

```sql
-- Active users (learned at least 1 word)
SELECT COUNT(DISTINCT user_id) FROM user_words;

-- Total words learned across all users
SELECT COUNT(*) FROM user_words;

-- Average accuracy
SELECT AVG(CAST(correct_count AS FLOAT) / (correct_count + wrong_count))
FROM user_words
WHERE correct_count + wrong_count > 0;

-- Words due for review today
SELECT COUNT(*) FROM user_words WHERE next_review <= NOW();
```

### Monitoring Integrations

**None currently implemented.** Render provides:
- Uptime monitoring (HTTP status codes)
- Log aggregation (stdout/stderr)
- Memory and CPU metrics (dashboard)

**Recommendations for production:**
- Integrate Sentry for error tracking
- Add logging framework (e.g., `logging` module)
- Monitor PostgreSQL query performance
- Track Telegram API response times

### Error Handling Strategy

**Silent Failures (Design Limitation):**
- If user not found: Return `None` → Display "Нет данных."
- If service fails: Exception propagates → Aiogram logs to stderr
- If database fails: `SessionLocal()` raises exception → User sees timeout

**Better Practice Needed:**
- Explicit exception handling with user-friendly messages
- Logging with context (user_id, action, error type)
- Exponential backoff for transient failures

---

## Testing

### Testing Framework

**No testing framework implemented.** No `pytest`, `unittest`, or similar present.

### Test Structure

**None.** No `tests/` directory or test files found.

### Coverage Overview

**0% test coverage.** Project lacks:
- Unit tests for services
- Integration tests for handlers
- Database tests
- End-to-end bot tests

### How to Run Tests

**Tests cannot be run.** Recommendation: Add pytest setup:

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Create tests/ directory
mkdir tests

# Add conftest.py and test files
# Run tests
pytest tests/
```

**Priority test areas:**
1. `services/review_service.py` - SM2 interval calculation
2. `services/word_service.py` - Word filtering logic
3. `services/quiz_service.py` - Quiz generation and randomness
4. Handlers - Message and callback processing

---

## Deployment Architecture

### Deployment Model

**Serverless/Container Model (Render):**
- **Type:** Worker service (no HTTP request handling by Render; application serves its own HTTP)
- **Scaling:** Single instance (no auto-scaling configured)
- **Persistence:** PostgreSQL on Render (shared database)

### Infrastructure Components

```
┌─────────────────────────────────────────┐
│           Render.com Platform           │
├─────────────────────────────────────────┤
│                                         │
│  ┌─ Worker Service (Python)          │
│  │ • Instance: 1 (fixed)             │
│  │ • Memory: 512 MB (default)        │
│  │ • Disk: Ephemeral (cleared on    │
│  │         restart)                  │
│  │ • Runtime: python-3.12.10         │
│  │ • Startup: python bot.py          │
│  └─────────────────────────────────┐ │
│                                    │ │
│  ┌─ PostgreSQL Database          │ │
│  │ • Version: Latest              │ │
│  │ • Storage: Persistent (20GB    │ │
│  │           default)             │ │
│  │ • Backups: Automatic           │ │
│  └────────────────────────────────┘ │
│                                     │
│  ┌─ Network                       │
│  │ • Inbound: HTTPS (public URL)  │
│  │ • Outbound: Telegram API       │
│  │ • Outbound: Edge TTS (Azure)   │
│  └─────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Runtime Environments

**Production (Render):**
- **Python Version:** 3.12.10
- **Dependencies:** Installed via `pip install -r requirements.txt`
- **Environment Variables:** Synced from Render dashboard
- **Database:** PostgreSQL (hosted on Render)
- **Secrets:** `BOT_TOKEN`, `DATABASE_URL` (environment variables)

**Local Development:**
- **Python Version:** 3.12.10 (via `.python-version`)
- **Dependencies:** Virtual environment + `requirements.txt`
- **Database:** Local PostgreSQL or Render database via SSH tunnel
- **Secrets:** `.env` file (git-ignored)

---

## Known Technical Debt

### Code Smells

1. **Global State in Handlers** (`handlers/lesson.py` lines 31–34)
   - `CURRENT_WORDS`, `VOICE_MESSAGES`, `CURRENT_MODE`, `SPEAK_IN_PROGRESS` are module-level dicts
   - **Risk:** Memory leaks if keys not cleaned up; potential user isolation issues
   - **Impact:** Low (transient state, cleared per interaction)
   - **Fix:** Use Aiogram's FSM (Finite State Machine) instead

2. **Synchronous Database Calls in Async Context** (all services)
   - Services use `SessionLocal()` blocking calls in async handlers
   - **Risk:** Blocks event loop; poor performance under load
   - **Impact:** Medium (scalability bottleneck)
   - **Fix:** Use `asyncio.to_thread()` or async SQLAlchemy (`sqlalchemy.ext.asyncio`)

3. **Magic Strings and Hardcoded Values**
   - Keyboard labels, messages, and options scattered across handlers
   - **Risk:** Difficult to maintain; no i18n support
   - **Impact:** Low (maintainability only)
   - **Fix:** Extract to configuration or i18n module

4. **Insufficient Error Handling**
   - Many functions return `None` without exception raising
   - **Risk:** Silent failures; difficult debugging
   - **Impact:** Medium (user experience and debugging)
   - **Fix:** Explicit exception hierarchy and logging

### Architectural Risks

1. **No Scalability Model**
   - Single-instance deployment; no load balancing or horizontal scaling
   - Render worker service doesn't auto-scale
   - **Risk:** Performance degradation with high user volume (1000+)
   - **Impact:** High (for production)
   - **Fix:** Migrate to container orchestration (Docker + Kubernetes) or Lambda functions

2. **Database Connection Pooling**
   - Default pool size (10 connections); not tuned for concurrent load
   - **Risk:** Connection exhaustion under 100+ concurrent users
   - **Impact:** High (for production)
   - **Fix:** Tune `pool_size` and `max_overflow` in `db/database.py`

3. **No Webhook Retry Logic**
   - Telegram webhooks not retried on failure
   - **Risk:** Missed user messages; lost state
   - **Impact:** Medium (reliability)
   - **Fix:** Implement message queue (Redis) for reliable delivery

4. **Spaced Repetition Algorithm Not Peer-Reviewed**
   - SM2-inspired but not validated against Anki's implementation
   - **Risk:** Learning intervals may be suboptimal
   - **Impact:** Low (UX only; no security risk)
   - **Fix:** Compare against Anki's algorithm and adjust multipliers

### Areas Lacking Tests

- ✗ `services/review_service.py` - SM2 interval calculation (critical)
- ✗ `services/word_service.py` - Word filtering with priority and topic
- ✗ `handlers/lesson.py` - Quiz logic and answer validation
- ✗ `services/quiz_service.py` - Option randomness and correctness
- ✗ Database operations (ORM queries, transactions)
- ✗ Telegram API integration (webhook handling)

### Areas Lacking Documentation

- ✗ Spaced repetition algorithm specifics (which Anki version?)
- ✗ Priority-based word selection (why `min(priority)`?)
- ✗ Dialog and grammar content schema
- ✗ Deployment troubleshooting guide
- ✗ Performance tuning for high user volume

### Potential Improvements

**High Priority:**
1. Add comprehensive logging (Python `logging` module)
2. Implement unit tests (pytest) for services
3. Use Aiogram's FSM instead of global state
4. Convert to async database access

**Medium Priority:**
1. Add i18n support (currently Russian-only)
2. Implement message queue for reliability
3. Add monitoring and alerting (Sentry, Prometheus)
4. Create API documentation (Swagger/OpenAPI)

**Low Priority:**
1. Add dialog content management UI
2. Implement admin commands (stats, user management)
3. Add A/B testing framework for algorithm tweaks
4. Create mobile app (currently Telegram web only)

---

## Developer Guide

### How to Add New Features

#### Add a New Learning Topic

1. **Add topic to database:**
   ```python
   # Manually insert into words table
   INSERT INTO words (lemma, translation, level, topic, example_tr, example_ru, priority)
   VALUES ('kelime', 'слово', 'A1', 'new_topic', 'Yeni kelime', 'Новое слово', 100);
   ```

2. **Update topic mapping** (`services/topic_service.py`):
   ```python
   TOPIC_NAMES = {
       ...existing topics...,
       "new_topic": "🆕 Новая тема"
   }
   ```

3. **Test via settings menu** - New topic auto-appears in `get_topics()` query

#### Add a New Handler (Command or Button)

1. **Create handler file** (e.g., `handlers/feature.py`):
   ```python
   from aiogram import Router
   from aiogram.types import Message
   
   router = Router()
   
   @router.message(lambda m: m.text == "🎯 Feature")
   async def feature_handler(message: Message):
       await message.answer("Feature response")
   ```

2. **Register router in dispatcher** (`bot.py` line 44–48):
   ```python
   from handlers.feature import router as feature_router
   
   dp.include_router(feature_router)
   ```

3. **Add button to menu** (`keyboards/menu.py`):
   ```python
   main_menu = ReplyKeyboardMarkup(
       keyboard=[
           ...existing buttons...,
           [KeyboardButton(text="🎯 Feature")]
       ]
   )
   ```

#### Add a New Service Function

1. **Create service module** (e.g., `services/feature_service.py`):
   ```python
   from db.database import SessionLocal
   from db.models import User, Word
   
   def feature_function(telegram_id: int):
       db = SessionLocal()
       try:
           # Query and process
           result = ...
           return result
       finally:
           db.close()
   ```

2. **Import and call from handler**:
   ```python
   from services.feature_service import feature_function
   
   @router.message(...)
   async def handler(message: Message):
       result = feature_function(message.from_user.id)
       await message.answer(result)
   ```

#### Add a New Database Model

1. **Define ORM model** (`db/models.py`):
   ```python
   class Feature(Base):
       __tablename__ = "features"
       
       id: Mapped[int] = mapped_column(Integer, primary_key=True)
       user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
       data: Mapped[str] = mapped_column(String(100))
   ```

2. **Create/migrate database:**
   ```bash
   # Delete old tables or use Alembic for migrations
   python -m db.seed  # Recreates schema
   ```

### Coding Conventions Found in Repository

#### Code Style

- **Naming:**
  - `snake_case` for functions and variables
  - `CamelCase` for classes
  - Prefix private with `_` (not enforced)

- **Line Length:** Approximately 80 characters (soft limit)

- **Indentation:** 4 spaces (Python standard)

- **Imports:**
  - Group by: stdlib, third-party, local
  - One import per line (generally)

#### Function Signatures

```python
# Explicit type hints (Python 3.12 feature)
def function_name(
    param1: int,
    param2: str | None = None
) -> dict | None:
    """Docstring (sparse; not consistently used)"""
    ...
```

#### Database Access Pattern

```python
def service_function(identifier: int):
    db = SessionLocal()  # Create session
    
    try:
        # Perform operations
        user = db.query(User).filter(...).first()
        return result
    
    finally:
        db.close()  # Always close
```

#### Handler Pattern

```python
@router.message(filter_condition)
async def handler_name(message: Message):
    # Extract data
    data = extract_from_message(message)
    
    # Call service
    result = service_function(data)
    
    # Send response
    await message.answer(response_text, reply_markup=keyboard)
```

#### Error Handling

- **Silent returns:** `if not user: return None`
- **No explicit exceptions** raised in services
- **User-facing messages:** Check and handle special return values

### Extension Points

**High-Value Extensions:**

1. **Quiz Backend**
   - Modify `services/quiz_service.py` to support:
     - Fill-in-the-blank questions
     - Pronunciation-based answers
     - Multiple correct answers

2. **Scheduling System**
   - Use `apscheduler` (already in requirements) for:
     - Daily reminder notifications
     - Batch word imports
     - Statistics reports

3. **Content Management**
   - Extend `services/dialog_service.py` and `grammar_service.py` to:
     - Load from database instead of JSON
     - Support CRUD operations
     - Version control for content

4. **User Customization**
   - Add to `db/models.User`:
     - Learning time preferences
     - Notification settings
     - Theme preferences

### Common Development Workflows

#### Running the Bot Locally

```bash
# 1. Setup environment
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 2. Create .env
cat > .env << EOF
BOT_TOKEN=your_test_token_from_botfather
DATABASE_URL=postgresql://localhost/turkish_bot
WEBHOOK_SECRET=test-secret
RENDER_EXTERNAL_URL=http://localhost:8000
EOF

# 3. Start bot
python bot.py
```

**Note:** Webhook won't work locally (requires public URL). For local testing, modify `bot.py` to use polling instead:

```python
# Replace webhook setup with polling
await dp.start_polling(bot)
```

#### Debugging

```python
# Add print statements
print(f"Debug: {variable_name}")

# Check logs in Render dashboard
# Settings → Logs tab

# Connect to production database (if needed)
# ssh -L 5432:localhost:5432 render_instance
# psql postgresql://user:pass@localhost/turkish_bot
```

#### Deploying Changes

```bash
# 1. Commit and push to main
git add .
git commit -m "Feature: description"
git push origin main

# 2. Render auto-deploys
# Watch progress in Render dashboard

# 3. Verify deployment
# Send /start to bot and confirm it's responsive
```

#### Database Migrations

```bash
# Temporary solution (no Alembic):
# 1. Backup database
pg_dump postgresql://user:pass@host/db > backup.sql

# 2. Modify db/models.py

# 3. Drop and recreate (DATA LOSS!)
# -- DANGER: Only do in dev/test environments
python -c "from db.database import engine; from db.models import Base; Base.metadata.drop_all(engine)"

# 4. Recreate schema
python -m db.seed

# 5. Restore data (if keeping old schema)
psql postgresql://user:pass@host/db < backup.sql
```

---

## Summary

The **Turkish Telegram Bot** is a focused, single-developer project implementing a language learning bot with spaced repetition, contextual dialogs, and grammar reference. Its architecture is pragmatic (monolithic, webhook-based) and suitable for small-to-medium user volumes. Key strengths include modular service design, clean ORM usage, and comprehensive content (vocabulary, dialogs, grammar). Primary technical debt revolves around testing absence, error handling, and lack of async database access—all addressable for production readiness. The codebase demonstrates clear Python conventions and is well-suited for onboarding new developers with the provided architecture and module documentation.
