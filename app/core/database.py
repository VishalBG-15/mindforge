from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker

DATABASE_URL = "sqlite:///./mindforge.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Modern SQLAlchemy 2.0 typed Base class
class Base(DeclarativeBase):
    pass


def initialize_database():
    Base.metadata.create_all(bind=engine)
    habit_columns = {
        column["name"] for column in inspect(engine).get_columns("habits")
    }
    legacy_habit_columns = {
        "frequency": "VARCHAR(50) NOT NULL DEFAULT 'daily'",
        "target_count": "INTEGER NOT NULL DEFAULT 1",
    }
    with engine.begin() as connection:
        for column, definition in legacy_habit_columns.items():
            if column not in habit_columns:
                connection.execute(
                    text(f"ALTER TABLE habits ADD COLUMN {column} {definition}")
                )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()