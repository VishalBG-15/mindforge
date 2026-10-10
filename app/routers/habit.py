from typing import List
import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.agent.llm import (
    AgentConfigurationError,
    AgentProviderError,
    AgentResponseError,
)
from app.agent.workflow import run_council
from app.core.database import get_db
from app.models.habit import Habit, HabitLog
from app.schemas.council import CouncilResponse
from app.schemas.habit import HabitCreate, HabitResponse, HabitUpdate
from app.schemas.log import HabitLogCreate, HabitLogResponse

router = APIRouter()
logger = logging.getLogger(__name__)


# 1. CREATE: Add a new habit
@router.post("/", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
def create_habit(habit_in: HabitCreate, db: Session = Depends(get_db)):
    db_habit = Habit(
        title=habit_in.title,
        description=habit_in.description
    )
    db.add(db_habit)
    db.commit()
    db.refresh(db_habit)
    return db_habit


# 2. READ ALL: Get all active habits
@router.get("/", response_model=List[HabitResponse])
def get_habits(db: Session = Depends(get_db)):
    return db.query(Habit).filter(Habit.is_active == True).all()


# 3. READ ONE: Get a specific habit by ID
@router.get("/{habit_id}", response_model=HabitResponse)
def get_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with ID {habit_id} not found."
        )
    return habit


# 4. UPDATE: Modify an existing habit
@router.put("/{habit_id}", response_model=HabitResponse)
def update_habit(habit_id: int, habit_in: HabitUpdate, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with ID {habit_id} not found."
        )

    update_data = habit_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(habit, field, value)

    db.commit()
    db.refresh(habit)
    return habit


# 5. DELETE: Soft delete a habit (deactivates without destroying history)
@router.delete("/{habit_id}", status_code=status.HTTP_200_OK)
def delete_habit(habit_id: int, db: Session = Depends(get_db)):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with ID {habit_id} not found."
        )

    habit.is_active = False
    db.commit()
    return {"message": f"Habit '{habit.title}' deactivated successfully."}


# 6. LOG CHECK-IN: Record completion or missed entry for a habit
@router.post("/{habit_id}/logs", response_model=HabitLogResponse, status_code=status.HTTP_201_CREATED)
def log_habit_checkin(
    habit_id: int,
    payload: HabitLogCreate,
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id, Habit.is_active == True).first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active habit with ID {habit_id} not found."
        )

    new_log = HabitLog(
        habit_id=habit_id,
        completed=payload.completed,
        notes=payload.notes
    )
    db.add(new_log)
    db.commit()
    db.refresh(new_log)
    return new_log


# 7. READ LOGS: Retrieve check-in history for analytics evaluation
@router.get("/{habit_id}/logs", response_model=List[HabitLogResponse])
def get_habit_logs(
    habit_id: int,
    limit: int = Query(default=14, ge=1, le=100),
    db: Session = Depends(get_db)
):
    habit = db.query(Habit).filter(Habit.id == habit_id).first()
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Habit with ID {habit_id} not found."
        )

    logs = (
        db.query(HabitLog)
        .filter(HabitLog.habit_id == habit_id)
        .order_by(HabitLog.logged_at.desc())
        .limit(limit)
        .all()
    )
    return logs


@router.post(
    "/{habit_id}/council",
    response_model=CouncilResponse,
    status_code=status.HTTP_201_CREATED,
)
def run_habit_council(habit_id: int, db: Session = Depends(get_db)):
    habit = (
        db.query(Habit)
        .filter(Habit.id == habit_id, Habit.is_active.is_(True))
        .first()
    )
    if not habit:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Active habit with ID {habit_id} not found.",
        )

    try:
        return run_council(db, habit_id)
    except AgentConfigurationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        ) from exc
    except AgentProviderError as exc:
        logger.exception("OpenAI provider failed while running council for habit %s", habit_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc
    except AgentResponseError as exc:
        logger.exception("Council returned an invalid agent response for habit %s", habit_id)
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        ) from exc