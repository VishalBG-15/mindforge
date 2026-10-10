from datetime import date, datetime, time, timedelta
from typing import List, Tuple

from app.core.database import SessionLocal, initialize_database
from app.models.habit import Habit, HabitLog


DEMO_HABITS: List[Tuple[str, str, List[bool], List[str]]] = [
    (
        "[Demo] Morning movement",
        "Build a steady walking routine with a flexible, low-pressure target.",
        [True, False, True, True, False, True, True, True, False, True, True, False, True, True],
        [
            "A short walk after lunch was enough to get started.",
            "Rain made the usual route less appealing; an indoor backup could help.",
        ],
    ),
    (
        "[Demo] Focused reading",
        "Read a few pages each day, ideally before winding down for sleep.",
        [True, True, True, True, False, True, True, True, True, True, True, True, True, True],
        [
            "A few pages before bed felt manageable.",
            "The evening got busy, so I missed my usual reading window.",
        ],
    ),
    (
        "[Demo] Evening reflection",
        "Take a moment to write down one thought at the end of the day.",
        [True, False, True, False, True, True, False, True, False, True, True, False, False, False],
        [
            "Writing one sentence helped me close out the day.",
            "I forgot to pause when the evening got busy.",
        ],
    ),
]


def seed_demo_data() -> None:
    initialize_database()
    today = date.today()
    added = 0
    skipped = 0

    with SessionLocal() as db:
        try:
            for title, description, outcomes, reflections in DEMO_HABITS:
                existing = db.query(Habit).filter(Habit.title == title).first()
                if existing:
                    skipped += 1
                    continue

                habit = Habit(
                    title=title,
                    description=description,
                    frequency="daily",
                    target_count=1,
                )
                db.add(habit)
                db.flush()

                logs = []
                for days_ago, completed in zip(range(13, -1, -1), outcomes):
                    logged_date = today - timedelta(days=days_ago)
                    reflection = reflections[0] if completed else reflections[1]
                    logs.append(
                        HabitLog(
                            habit_id=habit.id,
                            completed=completed,
                            notes=reflection,
                            logged_at=datetime.combine(
                                logged_date,
                                time(hour=6, minute=days_ago % 60),
                            ),
                        )
                    )
                db.add_all(logs)
                added += 1

            db.commit()
        except Exception:
            db.rollback()
            raise

    print(f"Added {added} demo habits with 14 days of check-in history each.")
    print(f"Skipped {skipped} demo habits that already existed.")
    print("Demo entries are labeled [Demo] and can be removed from the dashboard.")


if __name__ == "__main__":
    seed_demo_data()
