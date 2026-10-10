# 🧠 MindForge: Agentic AI-Driven Behavioral Habit Engine

> **MindForge** is an enterprise-grade, agent-driven habit transformation platform. It bridges robust transactional persistence, strict type validation, and multi-node autonomous reasoning to move beyond static habit trackers into adaptive, behavior-aware coaching.

---

## 📑 Table of Contents
1. [Architectural Philosophy](#-architectural-philosophy)
2. [High-Level System Architecture](#-high-level-system-architecture)
3. [Technology Stack & Architectural Justifications](#-technology-stack--architectural-justifications)
4. [Directory & Package Structure](#-directory--package-structure)
5. [Environment Setup & Installation Guide](#-environment-setup--installation-guide)
6. [The Data Persistence Layer (SQLAlchemy & SQLite)](#-the-data-persistence-layer-sqlalchemy--sqlite)
7. [The Data Validation Layer (Pydantic v2)](#-the-data-validation-layer-pydantic-v2)
8. [The API & Networking Layer (FastAPI)](#-the-api--networking-layer-fastapi)
9. [The LangGraph Four-Agent Council](#-langgraph-four-agent-council)
10. [Troubleshooting & Engineering Gotchas](#-troubleshooting--engineering-gotchas)
11. [Project Roadmap & Implementation Milestones](#-project-roadmap--implementation-milestones)

---

## 🏛️ Architectural Philosophy

Most habit trackers fail because they function merely as glorified ledgers—recording binary check-marks without understanding human friction, cognitive load, or environmental triggers. **MindForge** is built on three architectural pillars:

1. **Separation of Concerns (SoC):** Database persistence, network validation, business routing, and intelligence reasoning are strictly isolated. No database models leak into HTTP handlers; no LLM prompts interact directly with raw SQL.
2. **Defensive Schema Design:** Input boundaries are strictly typed and sanitized before reaching memory or disk. System state changes are transactional, idempotent, and auditable.
3. **State-Driven Autonomous Agent Pipeline:** LangGraph runs deterministic ingestion and analytics followed by a **four-agent council**. Each LLM agent has one typed, structured task: diagnose friction, recommend a strategy, critique feasibility, and communicate a coaching directive.

---

## 📐 High-Level System Architecture

```text
                                 [ HTTP Clients / Frontend ]
                                              │
                                              ▼
                             ┌─────────────────────────────────┐
                             │    FastAPI Application Router   │
                             │        (`app/routers/`)         │
                             └────────────────┬────────────────┘
                                              │
                    ┌─────────────────────────┴─────────────────────────┐
                    ▼                                                   ▼
      ┌───────────────────────────┐                       ┌───────────────────────────┐
      │   Pydantic v2 Schemas     │                       │  Database Session Layer   │
      │    (`app/schemas/`)       │                       │    (`app/core/database`)  │
      │  - Enforces API Contract  │                       │  - Connection Pooling     │
      │  - Sanitizes Inputs       │                       │  - Unit of Work (Session) │
      │  - Serializes JSON        │                       └─────────────┬─────────────┘
      └─────────────┬─────────────┘                                     │
                    │                                                   ▼
                    │                                     ┌───────────────────────────┐
                    │                                     │  SQLAlchemy ORM Models    │
                    │                                     │     (`app/models/`)       │
                    │                                     │  - Habits Table Schema    │
                    │                                     │  - Audit Timestamps (UTC) │
                    │                                     └─────────────┬─────────────┘
                    │                                                   │
                    └─────────────────────┬─────────────────────────────┘
                                          │
                                          ▼
                             ┌─────────────────────────┐
                             │ SQLite Database Engine  │
                             │    (`mindforge.db`)     │
                             └────────────┬────────────┘
                                          │ (Historical Context)
                                          ▼
                      ┌───────────────────────────────────────┐
                      │    MindForge Agentic Pipeline         │
                      │          (`app/agent/`)               │
                      │  [Ingest & Quantitative Analytics]    │
                      │  [Agent 1: Diagnostic Profiler]       │
                      │  [Agent 2: Strategy Architect]        │
                      │  [Agent 3: Feasibility Critic]        │
                      │  [Agent 4: Coaching Communicator]     │
                      │  [Persist Council Session]            │
                      └───────────────────────────────────────┘
```

---

## 🛠️ Technology Stack & Architectural Justifications

| Component | Technology | Rationale & Trade-Off Analysis |
| :--- | :--- | :--- |
| **Runtime** | Python 3.12+ | Provides modern typing features (`type` statements, PEP 695), improved exception groups, and native timezone-aware datetime operations. |
| **API Framework** | FastAPI | High-performance ASGI framework built on Starlette and Pydantic. Provides auto-generated OpenAPI/Swagger documentation, native async support, and powerful dependency injection. |
| **Web Server** | Uvicorn | Blazing-fast ASGI server implementation using `uvloop` and `httptools` for production-grade asynchronous networking. |
| **ORM** | SQLAlchemy 2.0 | Decouples Python domain logic from SQL dialects. Enforces the Unit of Work design pattern, transactions, connection lifecycles, and relational mapping. |
| **Database** | SQLite 3 | Zero-configuration, serverless, self-contained relational database stored as a single disk file (`mindforge.db`). Ideal for development and embedded deployments, seamlessly swappable to PostgreSQL via connection string change. |
| **Data Validation** | Pydantic v2 | Rust-backed data validation and serialization library offering 5x–20x performance improvements over v1, strict type coercion, and seamless ORM integration. |
| **Agent Framework** | LangGraph | Orchestrates typed state through deterministic analytics and four sequential council agents. |
| **LLM Provider** | OpenAI `gpt-4o-mini` | Official OpenAI Python SDK; each council agent requests a JSON object at temperature 0.2. |
| **Frontend** | HTML, CSS, vanilla JavaScript | A responsive same-origin dashboard served directly by FastAPI. |

---

## 📁 Directory & Package Structure

```text
mindforge/
├── .gitignore               # Git rules: excludes venv/, caches, .db files, and .env
├── requirements.txt         # Runtime and agent dependencies
├── init_db.py               # Administrative script to bootstrap schema into SQLite
├── mindforge.db             # Local SQLite database file (generated automatically)
├── README.md                # Comprehensive project documentation
└── app/
    ├── __init__.py          # Marks 'app' as a top-level Python package
    ├── core/                # Core platform infrastructure & configurations
    │   ├── __init__.py
    │   └── database.py      # SQLite engine, SessionLocal factory, Base, and get_db()
    ├── models/              # SQLAlchemy ORM database models (Storage Contract)
    │   ├── __init__.py
    │   └── habit.py         # Habit entity definition (table columns, constraints)
    ├── schemas/             # Pydantic validation schemas (Network Contract)
    │   ├── __init__.py
    │   └── habit.py         # HabitBase, HabitCreate, HabitUpdate, HabitResponse
    ├── routers/
    │   └── habit.py         # Habit CRUD, check-in, history, and council API
    ├── schemas/             # Pydantic API contracts
    ├── agent/               # LangGraph workflow and council nodes
    │   ├── workflow.py
    │   ├── state.py
    │   ├── node_1_ingest.py
    │   ├── node_2_analytics.py
    │   ├── node_3_friction.py
    │   ├── node_4_strategy.py
    │   ├── node_4_critic.py
    │   ├── node_5_synthesis.py
    │   ├── node_6_persist.py
    │   └── strategies.json
    ├── static/              # Dashboard HTML, CSS, and JavaScript
    └── main.py              # FastAPI app, DB initialization, and static serving
```

---

## 💻 Environment Setup & Installation Guide

### 1. Repository & Virtual Environment Bootstrap

Clone or initialize the repository in your target directory (e.g., `D:\mindforge`):

```powershell
# 1. Initialize git version tracking
git init

# 2. Spin up an isolated Python virtual environment
python -m venv venv

# 3. Activate the environment (PowerShell)
.\venv\Scripts\Activate.ps1
```

> **Note on PowerShell Security Policies:** If you encounter `PSSecurityException` regarding script execution, execute:
> ```powershell
> Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
> .\venv\Scripts\Activate.ps1
> ```

### 2. Dependency Specification (`requirements.txt`)

The project dependencies, including LangGraph and the OpenAI SDK, are declared in `requirements.txt`. Install them into your activated environment:

```powershell
pip install -r requirements.txt
```

Set the OpenAI key in a local `.env` file (never commit it):

```dotenv
OPENAI_API_KEY=your-key
```

Start the app with `uvicorn app.main:app --reload`, then open `http://127.0.0.1:8000/`. FastAPI serves the dashboard, creates missing tables, and adds the `frequency` and `target_count` columns with defaults when upgrading an older habits table. The API docs are available at `/docs`. Council requests return `503` if `OPENAI_API_KEY` is missing and `502` if an OpenAI request or structured response fails; there is no non-LLM fallback.

---

## 🗄️ The Data Persistence Layer (SQLAlchemy & SQLite)

### 1. Engine & Session Lifecycle (`app/core/database.py`)

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./mindforge.db"

# Engine manages physical connection pooling and SQLite-specific threading
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}  # Permits FastAPI threads to access SQLite
)

# Session factory: generates isolated transactional workspaces
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base: dynamic metaclass that maps Python classes to database tables
Base = declarative_base()

# Dependency provider: guarantees clean connection opening and teardown per request
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

### 2. Model Definition (`app/models/habit.py`)

```python
from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base

class Habit(Base):
    __tablename__ = "habits"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    title = Column(String, nullable=False)
    description = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
```

#### Key Architecture Notes:
* **`check_same_thread: False`**: SQLite defaults to disallowing multi-threaded access. FastAPI operates concurrently across a thread pool; disabling this check allows safe cross-thread handling when wrapped in single-request sessions.
* **`default=lambda: datetime.now(timezone.utc)`**: Python 3.12 deprecated naive `datetime.utcnow()`. Wrapping `datetime.now(timezone.utc)` in a `lambda` ensures the timestamp is evaluated at the exact millisecond of row insertion rather than at server boot.
* **Soft Deletes via `is_active`**: Instead of issuing physical `DELETE` statements that obliterate historical logs, marking `is_active = False` archives the habit while preserving analytics integrity.

### 3. Schema Bootstrap (`init_db.py`)

```python
from app.core.database import engine, Base
from app.models.habit import Habit  # Registers Habit metadata with Base

def create_tables():
    print("Connecting to SQLite and building tables...")
    Base.metadata.create_all(bind=engine)
    print("Success: 'mindforge.db' materialized with 'habits' table!")

if __name__ == "__main__":
    create_tables()
```

Run via:
```powershell
python init_db.py
```

---

## 🛡️ The Data Validation Layer (Pydantic v2)

Located at `app/schemas/habit.py`, this layer decouples your internal database schemas from your public HTTP boundary.

```python
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field

class HabitBase(BaseModel):
    title: str = Field(..., min_length=1, max_length=100, description="Name of the habit")
    description: Optional[str] = Field(None, max_length=500, description="Context, triggers, or cue")

class HabitCreate(HabitBase):
    pass  # Server enforces id, timestamps, and active state

class HabitUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)
    is_active: Optional[bool] = None

class HabitResponse(HabitBase):
    id: int
    is_active: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
```

### Models vs. Schemas: The Critical Distinction

| Feature | SQLAlchemy ORM (`app/models/`) | Pydantic Schemas (`app/schemas/`) |
| :--- | :--- | :--- |
| **Domain** | Storage / Database Engine | Network Boundary / API Contract |
| **Format** | Python classes mapped to SQL tables | Serialized JSON payloads & Python types |
| **Purpose** | Read/write records to `mindforge.db` | Sanitize inputs, enforce limits, guard output data |
| **Security** | None (will store whatever SQL permits) | Rejects bad payloads with `422 Unprocessable Entity` |
| **Serialization** | Python object with lazy loading attributes | Native dictionary and JSON conversion |

---

## 🌐 The API & Networking Layer (FastAPI)

The REST API exposes clean HTTP endpoints interacting with the database through FastAPI's dependency injection (`Depends(get_db)`).

### Implemented Routes (`app/routers/habit.py`):

| Method | Endpoint | Description | Request Body | Response Model |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/habits/` | Create a new habit | `HabitCreate` | `HabitResponse` (HTTP 201) |
| `GET` | `/habits/` | Retrieve all active habits | None | `List[HabitResponse]` |
| `GET` | `/habits/{id}` | Retrieve a specific habit by ID | None | `HabitResponse` |
| `PUT` | `/habits/{id}` | Update title, description, or status | `HabitUpdate` | `HabitResponse` |
| `DELETE` | `/habits/{id}` | Soft delete (set `is_active=False`) | None | `{"message": "Success"}` |
| `POST` | `/habits/{id}/logs` | Record a completion or missed check-in with notes | `HabitLogCreate` | `HabitLogResponse` (HTTP 201) |
| `GET` | `/habits/{id}/logs` | Read recent check-in history | `limit` query (1–100) | `List[HabitLogResponse]` |
| `POST` | `/habits/{id}/council` | Run and persist the four-agent coaching council | Empty JSON object | `CouncilResponse` (HTTP 201) |

---

## 🤖 LangGraph Four-Agent Council

The compiled LangGraph is implemented in `app/agent/workflow.py`. It runs these nodes in sequence:

```text
[ Ingest recent logs ] → [ Deterministic analytics ]
             → [ Agent 1: Diagnostic Profiler ]
             → [ Agent 2: Strategy Architect ]
             → [ Agent 3: Feasibility Critic ]
             → [ Agent 4: Coaching Communicator ]
             → [ Persist council session ]
```

The four LLM calls use the official OpenAI Python SDK, `gpt-4o-mini` by default, temperature `0.2`, and JSON-object responses validated by Pydantic. Node 2 analyzes up to the 14 most recent check-ins and calculates the recent seven-entry completion rate and leading streaks. Node 6 writes the complete result and deliberation to `council_sessions`; it does not silently modify the user's habit target.

---

## ⚠️ Troubleshooting & Engineering Gotchas

### 1. `ModuleNotFoundError: No module named 'sqlalchemy'`
* **Cause:** The terminal ran against global Python instead of your virtual environment.
* **Fix:** Activate the virtual environment via `.\venv\Scripts\Activate.ps1`. In VS Code, configure your interpreter via `Ctrl + Shift + P` $
ightarrow$ `Python: Select Interpreter` $
ightarrow$ choose `.\venv\Scripts\python.exe`.

### 2. `The method "utcnow" in class "datetime" is deprecated`
* **Cause:** Python 3.12 deprecated naive UTC objects.
* **Fix:** Import `timezone` from `datetime` and use `default=lambda: datetime.now(timezone.utc)`.

### 3. `"Habit" is not accessed by Pylance (reportUnusedImport)`
* **Cause:** Pylance sees `from app.models.habit import Habit` inside `init_db.py` without explicit reference.
* **Fix:** This is an intentional side-effect import required to populate `Base.metadata`. You can ignore the warning or append `# noqa: F401`.

### 4. PowerShell Execution Policy Disabled
* **Cause:** Windows restricts unsigned PowerShell scripts by default.
* **Fix:** Run `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process` before running the activation script.

---

## 🗺️ Project Roadmap & Implementation Milestones

- [x] **Milestone 1: Environment Setup** (Git, venv, packages, `.gitignore`, directory layout)
- [x] **Milestone 2: Database Layer** (SQLite configuration, `Base`, `SessionLocal`, `Habit` model)
- [x] **Milestone 3: Database Bootstrap** (`init_db.py` execution, `mindforge.db` creation)
- [x] **Milestone 4: Data Validation Layer** (Pydantic v2 schemas: Base, Create, Update, Response)
- [x] **Milestone 5: Habit API** (CRUD, logs, and council endpoint in `app/routers/habit.py`)
- [x] **Milestone 6: Server Core** (FastAPI app, startup table creation, health check, and OpenAPI docs)
- [x] **Milestone 7: Habit Logging Engine** (`HabitLog` relational model and reflection notes)
- [x] **Milestone 8: Agentic Pipeline** (LangGraph with deterministic analytics and four council agents)
- [x] **Milestone 9: LLM Integration** (OpenAI structured JSON responses and persisted council sessions)
- [x] **Milestone 10: Client Frontend** (Responsive static dashboard served by FastAPI)

---

*Engineered with precision for autonomous habit development.*
