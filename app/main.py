from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from app.core.database import initialize_database
from app.routers import habit

load_dotenv()


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="MindForge API",
    description="Agentic AI Habit Coaching Engine",
    version="0.1.0",
    lifespan=lifespan,
)

# Register the habits router under the /api/v1/habits prefix
app.include_router(habit.router, prefix="/api/v1/habits", tags=["Habits"])

@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy", "service": "MindForge API"}


@app.get("/", include_in_schema=False)
def dashboard():
    return FileResponse(Path(__file__).with_name("static") / "index.html")


app.mount(
    "/static",
    StaticFiles(directory=Path(__file__).with_name("static"), html=True),
    name="dashboard",
)